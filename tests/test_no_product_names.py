"""Ningún producto está escrito en el código de la biblioteca.

Los cuatro productos actuales solo se nombran en presets.py, en sus temas, en
el manifiesto e íconos originales y en el catálogo (que es su demostración).
Comentarios y docstrings no cuentan.
"""
import io
import re
import tokenize
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent / "geneos_ui"
NAMES = re.compile(r"gema|gelectric|geletric|geagro", re.I)
ALLOWED = {"presets.py", "catalog_data.py", "catalog_examples.py", "views.py"}  # views.py = vista del catálogo


def _code_strings(path):
    """Literales e identificadores de un .py, sin comentarios ni docstrings."""
    toks = list(tokenize.generate_tokens(io.StringIO(path.read_text(encoding="utf-8")).readline))
    out = []
    for i, t in enumerate(toks):
        if t.type == tokenize.COMMENT:
            continue
        if t.type == tokenize.STRING:
            prev = next((p for p in reversed(toks[:i]) if p.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)), None)
            if prev is None or prev.string in (":",) or prev.type == tokenize.NEWLINE:
                continue  # docstring
        out.append(t.string)
    return " ".join(out)


def test_python_sin_nombres_de_productos():
    bad = [p.name for p in PKG.glob("*.py") if p.name not in ALLOWED and NAMES.search(_code_strings(p))]
    bad += [p.name for p in (PKG / "templatetags").glob("*.py") if NAMES.search(_code_strings(p))]
    assert bad == []


def _strip_comments(text, kind):
    if kind == "js":
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        return re.sub(r"(^|\s)//[^\n]*", r"\1", text)
    if kind == "css":
        return re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"\{#.*?#\}|<!--.*?-->", "", text, flags=re.S)


def test_js_css_y_templates_sin_nombres_de_productos():
    files = [PKG / "static/geneos_ui/js/geneos-ui.js", PKG / "static/geneos_ui/css/geneos-ui.css",
             PKG / "static/geneos_ui/css/tokens.css", *(PKG / "static/geneos_ui/css/bridges").glob("*.css"),
             *(PKG / "templates/geneos_ui/components").glob("*.html"), *(PKG / "templates/geneos_ui/layouts").glob("*.html")]
    bad = [f.name for f in files if NAMES.search(_strip_comments(f.read_text(encoding="utf-8"), f.suffix.lstrip(".")))]
    assert bad == []
