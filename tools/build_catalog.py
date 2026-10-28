"""Genera dist/ui-kit.html: el catálogo en un solo archivo, sin servidor.

Renderiza la vista real del catálogo (mismos templates, CSS y JS de la
librería) y la empaqueta con todo embebido, para revisarla en el navegador
o publicarla como página.

    python tools/build_catalog.py            → dist/ui-kit.html (documento completo)
    python tools/build_catalog.py --fragment → dist/ui-kit.fragment.html (sin <html>/<head>/<body>)
"""
import base64
from urllib.parse import unquote
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "sandbox")]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sandbox.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.staticfiles import finders  # noqa: E402
from django.test import Client  # noqa: E402

from geneos_ui.templatetags.geneos_ui import NAV_BOOT, THEME_BOOT  # noqa: E402

settings.DEBUG = True
settings.ALLOWED_HOSTS = ["*"]


def read_static(path):
    found = finders.find(path)
    if not found:
        raise FileNotFoundError(path)
    return Path(found).read_text(encoding="utf-8")


def data_uri(path):
    path = unquote(path)  # nombres originales con espacios y ñ
    found = finders.find(path)
    raw = Path(found).read_bytes()
    mime = "image/svg+xml" if path.endswith(".svg") else "image/png"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def build(fragment=False):
    html = Client().get("/?static=1").content.decode()
    static_url = settings.STATIC_URL

    # CSS: hojas locales embebidas, Google Fonts queda como <link>
    def inline_css(m):
        href = m.group(1)
        if href.startswith(static_url):
            return "<style>\n" + read_static(href[len(static_url):]) + "\n</style>"
        return m.group(0)
    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">', inline_css, html)

    # JS embebido
    def inline_js(m):
        src = m.group(1)
        return "<script>\n" + read_static(src[len(static_url):]) + "\n</script>"
    html = re.sub(r'<script src="([^"]+)"(?: defer)?></script>', inline_js, html)

    # imágenes como data URI
    html = re.sub(r'src="' + re.escape(static_url) + r'([^"]+)"', lambda m: f'src="{data_uri(m.group(1))}"', html)
    # íconos pintados por máscara en la barra horizontal (style="--gn-icon-src: url(...)")
    html = re.sub(r'url\(&quot;' + re.escape(static_url) + r'([^&]+)&quot;\)', lambda m: f'url(&quot;{data_uri(m.group(1))}&quot;)', html)

    # Claro por defecto: el modo lo decide solo la elección guardada del usuario
    # (no el modo del sistema operativo), así que no se agregan media queries.
    extra_css = "<style>\nbody { background: var(--gn-bg); color: var(--gn-text); }\n</style>"
    html = html.replace("</head>", extra_css + "\n</head>")

    if fragment:
        head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
        head = re.sub(r'<meta charset="utf-8">\s*', "", head)
        head = re.sub(r'<meta name="viewport"[^>]*>\s*', "", head)
        body_match = re.search(r'<body class="([^"]*)">(.*)</body>', html, re.S)
        classes, body = body_match.group(1).strip(), body_match.group(2)
        boot = ("<script>document.documentElement.setAttribute('data-gn-product','gelectric');"
                "document.documentElement.setAttribute('data-gn-nav-default','vertical');</script>\n" + THEME_BOOT + NAV_BOOT)
        html = head.strip() + "\n" + boot + f'\n<div class="{classes}">\n' + body + "\n</div>\n"
        out = ROOT / "dist" / "ui-kit.fragment.html"
    else:
        out = ROOT / "dist" / "ui-kit.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(out, f"{len(html) / 1024:.0f} KB")
    return out


if __name__ == "__main__":
    build(fragment="--fragment" in sys.argv)
