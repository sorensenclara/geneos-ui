"""gn_css y gn_js: tema del producto, fuente, puente Bootstrap, versión y nonce de CSP."""
from django.template import Context, Template
from django.test import RequestFactory

from geneos_ui import __version__


def render(tpl, **ctx):
    return Template("{% load geneos_ui %}" + tpl).render(Context(ctx))


def test_orden_y_version(settings):
    settings.GENEOS_UI = {"PRODUCT": "gema"}
    html = render("{% gn_css %}{% gn_js %}")
    order = [html.index(x) for x in ("fonts.googleapis.com", "tokens.css", "themes/gema.css", "geneos-ui.css", "geneos-ui.js")]
    assert order == sorted(order)
    assert f"tokens.css?v={__version__}" in html and f"geneos-ui.js?v={__version__}" in html
    settings.GENEOS_UI = {"PRODUCT": "gema", "STATIC_VERSION_QUERY": False}
    assert "?v=" not in render("{% gn_css %}{% gn_js %}")


def test_tema_y_fuente_del_producto(settings):
    settings.GENEOS_UI = {"PRODUCT": "geflota", "THEME_CSS": ["flota/tema.css", "flota/extra.css"], "FONT_CSS": "flota/fuente.css"}
    html = render("{% gn_css %}")
    assert "/static/flota/tema.css" in html and "/static/flota/extra.css" in html and "/static/flota/fuente.css" in html
    assert "themes/geflota.css" not in html and "fonts.googleapis.com" not in html
    settings.GENEOS_UI = {"PRODUCT": "geflota", "THEME_CSS": ["flota/tema.css"], "LOAD_FONTS": False}
    assert "fonts.googleapis.com" not in render("{% gn_css %}")


def test_tripletes_de_bootstrap_solo_con_el_puente(settings):
    settings.GENEOS_UI = {"PRODUCT": "gema"}
    assert "--bs-primary-rgb" not in render("{% gn_css %}")
    html = render("{% gn_css bridges='bootstrap5' %}")
    assert '<style>:root[data-gn-product="gema"] {' in html and "--bs-primary-rgb: 236, 108, 5;" in html
    assert html.index("bridges/bootstrap5.css") < html.index("<style>")
    settings.GENEOS_UI = {"PRODUCT": "geflota", "THEME_CSS": ["t.css"], "BRIDGES": ["bootstrap5"], "BOOTSTRAP_RGB": {"primary": "224, 122, 16"}}
    assert '[data-gn-product="geflota"] { --bs-primary-rgb: 224, 122, 16; }' in render("{% gn_css %}")


def test_puente_sin_productos():
    from pathlib import Path
    css = (Path(__file__).resolve().parent.parent / "geneos_ui/static/geneos_ui/css/bridges/bootstrap5.css").read_text()
    assert '[data-gn-product="' not in css


def test_nonce_de_csp(settings):
    settings.GENEOS_UI = {"PRODUCT": "gema", "BRIDGES": ["bootstrap5"]}
    req = RequestFactory().get("/")
    req.csp_nonce = "abc123"
    html = render("{% gn_theme_boot %}{% gn_nav_boot %}{% gn_css %}", request=req)
    assert html.count('nonce="abc123"') == 3
    # el context processor de CSP de Django 6 deja csp_nonce en el contexto
    assert 'nonce="xyz"' in render("{% gn_theme_boot %}", csp_nonce="xyz")
    assert "nonce" not in render("{% gn_theme_boot %}{% gn_nav_boot %}")


def test_css_de_otro_producto_en_el_catalogo(settings):
    settings.GENEOS_UI = {"PRODUCT": "gelectric"}
    assert "themes/gema.css" in render('{% gn_css "gema" %}')
