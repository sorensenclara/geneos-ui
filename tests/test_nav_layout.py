"""Preferencia de disposición del menú: horizontal o vertical, independiente del tema."""
from django.template import Context, Template
from django.test import Client, override_settings

from geneos_ui.catalog_data import PRODUCTS
from geneos_ui.conf import NAV_LAYOUT_DEFAULTS, get_config
from geneos_ui.navigation import build_nav


def test_valores_por_producto():
    assert NAV_LAYOUT_DEFAULTS == {"gema": "horizontal", "gelectric": "vertical",
                                   "geagro-cereales": "vertical", "geagro-vid": "vertical"}


@override_settings(GENEOS_UI={"PRODUCT": "gema"})
def test_config_toma_el_valor_del_producto():
    assert get_config()["NAV_LAYOUT"] == "horizontal"


@override_settings(GENEOS_UI={"PRODUCT": "gema", "NAV_LAYOUT": "vertical"})
def test_config_se_puede_cambiar():
    assert get_config()["NAV_LAYOUT"] == "vertical"


@override_settings(GENEOS_UI={"PRODUCT": "gelectric", "NAV_LAYOUT": "diagonal"})
def test_valor_invalido_usa_el_del_producto():
    assert get_config()["NAV_LAYOUT"] == "vertical"


def test_boot_lee_la_preferencia_y_usa_el_valor_del_producto():
    out = Template("{% load geneos_ui %}{% gn_nav_boot %}").render(Context())
    assert "localStorage.getItem('gn-nav')" in out
    assert "data-gn-nav-default" in out and "setAttribute('data-gn-nav'" in out
    # no toca el tema
    assert "gn-theme" not in out


def test_selector_accesible():
    out = Template("{% load geneos_ui %}{% gn_nav_switch %}").render(Context())
    assert 'role="radiogroup"' in out and 'aria-label="Disposición del menú"' in out
    assert 'data-gn-nav-value="horizontal"' in out and 'data-gn-nav-value="vertical"' in out


def test_un_solo_menu_con_iconos_para_las_dos_disposiciones():
    """GEMA: mismo NavItem, con el SVG blanco (vertical) y los SVG normal y -active (horizontal)."""
    nav = build_nav(next(p for p in PRODUCTS if p["key"] == "gema")["nav"](None), None)
    clientes = next(e for e in nav if e.get("label") == "Clientes")
    assert clientes["icon_static"].endswith("iconos/clientes-white.svg")
    assert clientes["icon_h"].endswith("iconos/clientes.svg")
    assert clientes["icon_h_active"].endswith("iconos/clientes-active.svg")
    html = Template("{% load geneos_ui %}{% gn_nav_icon e %}").render(Context({"e": clientes}))
    assert html.count("<img") == 3
    # los productos sin variantes para barra clara usan solo los íconos blancos
    gel = build_nav(next(p for p in PRODUCTS if p["key"] == "gelectric")["nav"](None), None)
    assert all(not e.get("icon_h") for e in gel if e["type"] != "section")


@override_settings(DEBUG=True)
def test_catalogo_expone_la_disposicion_de_cada_producto():
    html = Client().get("/?static=1").content.decode()
    assert "data-gn-nav=" in html and "data-gn-nav-default=" in html
    assert 'data-kit-switch="gema" data-kit-nav-default="horizontal"' in html
    assert 'data-kit-switch="gelectric" data-kit-nav-default="vertical"' in html
    assert "data-gn-nav-switch" in html and "data-gn-theme-switch" in html
    assert html.count('class="gn-sidebar"') == 4  # un menú por producto, sin duplicar por disposición


@override_settings(DEBUG=True)
def test_menu_mas_en_cada_sidebar_y_fuera_del_buscador():
    html = Client().get("/?static=1").content.decode()
    assert html.count("data-gn-nav-more") >= 4
    assert 'aria-controls="gn-sidebar-gelectric-more"' in html


def test_tokens_de_activo_por_producto():
    from pathlib import Path
    css = Path(__file__).resolve().parent.parent / "geneos_ui" / "static" / "geneos_ui" / "css"
    tokens = (css / "tokens.css").read_text()
    gema = (css / "themes" / "gema.css").read_text()
    assert "--gn-hnav-active-bg: var(--gn-sidebar-active-bg)" in tokens
    assert "--gn-hnav-active-bg: transparent" in gema and "--gn-hnav-active-weight: 400" in gema
