"""HTML de referencia de los cuatro productos.

Renderiza con el código actual las piezas que genera el paquete (layout,
sidebar, encabezado, preferencias, paginación, badges, breadcrumbs, íconos,
login y catálogo) para cada producto. ``test_html_snapshots.py`` compara el
resultado con la referencia guardada de una versión anterior.

    python tests/snapshots/generate.py 0.2.1   → tests/snapshots/0.2.1/*.html

Funciona también sobre el código de una versión anterior (se copia este
archivo a un checkout de ese tag), así la referencia sale del código publicado.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRODUCTS = ("gelectric", "gema", "geagro-cereales", "geagro-vid")
NAV = {
    "gelectric": "geneos_ui.catalog_data.nav_gelectric",
    "gema": "geneos_ui.catalog_data.nav_gema",
    "geagro-cereales": "geneos_ui.catalog_data.nav_geagro_cereales",
    "geagro-vid": "geneos_ui.catalog_data.nav_geagro_vid",
}
ICON_REFS = ("gema:clientes", "gelectric:asociados", "geagro:dashboard", "geagro-cereales:campos", "geagro-vid:fenologia")


def product_settings(p):
    return {
        "PRODUCT": p, "NAV": NAV[p], "TAGLINE": "Sandbox",
        "LOGO_FULL": f"demo/logos/{p}-full.svg", "LOGO_ICON": f"demo/logos/{p}-icon.svg",
        "LOGO_TOPBAR": f"demo/logos/{p}-topbar.svg",
    }


def normalize(html):
    """Lo que cambia a propósito entre versiones y no es diseño ni comportamiento."""
    html = re.sub(r'(\.(?:css|js))\?v=[^"&\s]+', r"\1", html)            # ?v=<versión> de los estáticos
    html = re.sub(r'<span class="kit-kind[^"]*"[^>]*>.*?</span>', "", html, flags=re.S)  # marcas del catálogo
    html = re.sub(r'GN\.version = "[^"]+"', 'GN.version = "x"', html)
    html = re.sub(r"UI Kit v[0-9.]+", "UI Kit vX", html)
    return html


def render_all():
    from django.core.paginator import Paginator
    from django.template import Context, Template
    from django.test import Client, RequestFactory, override_settings

    out = {}
    rf = RequestFactory()
    for p in PRODUCTS:
        with override_settings(GENEOS_UI=product_settings(p), DEBUG=True):
            out[f"{p}-demo"] = Client().get("/demo/?page=3&o=-nombre").content.decode()
            out[f"{p}-auth"] = Template(
                '{% extends "geneos_ui/layouts/auth.html" %}{% block auth_content %}<h1>Ingresar</h1>{% endblock %}'
            ).render(Context({"gn": __import__("geneos_ui.context_processors", fromlist=["x"]).geneos_ui(rf.get("/"))["gn"]}))
            out[f"{p}-css"] = Template("{% load geneos_ui %}{% gn_css %}|{% gn_css bridges='bootstrap5,jazzmin' %}|{% gn_js %}").render(Context())
            req = rf.get("/x/", {"q": "abc", "page": "4"})
            page = Paginator(list(range(300)), 25).get_page(4)
            out[f"{p}-tags"] = Template(
                "{% load geneos_ui %}{% gn_theme_boot %}{% gn_nav_boot %}{% gn_prefs %}{% gn_theme_switch %}{% gn_nav_switch %}"
                "{% gn_pagination page %}{% gn_sort_th 'Nombre' 'nombre' %}{% gn_badge 'Vencido' 'critical' True %}"
                "{% gn_breadcrumbs crumbs %}{% gn_icon 'i-gear' %}"
                + "".join(f"{{% gn_product_icon '{r}' %}}{{% gn_product_icon '{r}' 'base' %}}" for r in ICON_REFS)
            ).render(Context({"request": req, "page": page, "crumbs": [("Inicio", "/"), ("Clientes", None)]}))
    with override_settings(DEBUG=True):
        out["catalog"] = Client().get("/?static=1").content.decode()
    return {k: normalize(v) for k, v in out.items()}


def main(version):
    sys.path[:0] = [str(ROOT), str(ROOT / "sandbox")]
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sandbox.settings")
    import django
    django.setup()
    dest = Path(__file__).resolve().parent / version
    dest.mkdir(parents=True, exist_ok=True)
    for name, html in render_all().items():
        (dest / f"{name}.html").write_text(html, encoding="utf-8")
    print(dest, len(list(dest.glob("*.html"))), "archivos")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "actual")
