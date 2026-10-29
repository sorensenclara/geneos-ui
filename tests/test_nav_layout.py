"""Preferencia de disposición del menú: horizontal o vertical, independiente del tema."""
from django.template import Context, Template
from django.test import Client, override_settings

from geneos_ui.catalog_data import PRODUCTS
from geneos_ui.conf import get_config
from geneos_ui.presets import PRESETS
from geneos_ui.navigation import build_nav


def test_valores_por_producto():
    assert {k: v["NAV_LAYOUT"] for k, v in PRESETS.items()} == {"gema": "horizontal", "gelectric": "vertical",
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

def _nav(key):
    return build_nav(next(p for p in PRODUCTS if p["key"] == key)["nav"](None), None)


def test_gelectric_usa_sus_iconos_de_color_en_la_barra_clara():
    gel = [e for e in _nav("gelectric") if e.get("icon_static")]
    assert gel and all(e["icon_h"] and "/icon - " in e["icon_h"] for e in gel)
    assert all(not e["icon_h_active"] and not e["icon_h_tint"] for e in gel)


def test_geagro_pinta_su_svg_blanco_original_con_los_tokens():
    for key in ("geagro-cereales", "geagro-vid"):
        items = [e for e in _nav(key) if e.get("icon_static")]
        assert items and all(e["icon_h_tint"] and not e["icon_h"] for e in items)
        html = Template("{% load geneos_ui %}{% gn_nav_icon e %}").render(Context({"e": items[0]}))
        assert 'class="gn-nav__icon-tint"' in html and items[0]["icon_static"].split("/")[-1] in html
        # los pendientes siguen con el marcador neutro, sin máscara
        assert all(not e["icon_h_tint"] for e in _nav(key) if e.get("icon_pending"))


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
    # un solo diseño (el de GEMA) en los tokens compartidos: barra blanca sobre franja institucional
    for decl in ("--gn-hnav-bg: var(--gn-elevated)", "--gn-hnav-band: var(--gn-c-sidebar)", "--gn-hnav-band-h: 40px",
                 "--gn-hnav-radius: 8px", "--gn-hnav-inset: 24px", "--gn-hnav-active-bg: transparent",
                 "--gn-hnav-active-line: var(--gn-hnav-accent)"):
        assert decl in tokens
    # los temas no redefinen la estructura ni el fondo de la barra
    for f in (css / "themes").glob("*.css"):
        t = f.read_text()
        for prop in ("--gn-hnav-bg:", "--gn-hnav-radius:", "--gn-hnav-inset:", "--gn-hnav-height:", "--gn-hnav-shadow:"):
            assert prop not in t, (f.name, prop)
    # GEMA es la referencia: no declara ningún token propio de la barra
    import re
    assert not re.search(r"--gn-hnav-[a-z-]+\s*:", gema)


def test_panel_de_preferencias_reune_los_dos_selectores():
    out = Template("{% load geneos_ui %}{% gn_prefs %}").render(Context())
    assert 'data-gn-prefs-toggle' in out and 'aria-controls="gn-prefs-panel"' in out and 'aria-expanded="false"' in out
    assert 'role="dialog"' in out and "data-gn-prefs-close" in out
    assert out.count("data-gn-theme-switch") == 1 and out.count("data-gn-nav-switch") == 1
    assert "Apariencia" in out and "Navegación en escritorio" in out


@override_settings(DEBUG=True)
def test_selectores_fuera_del_encabezado_y_en_la_solapa():
    html = Client().get("/?static=1").content.decode()
    topbar = html.split('<header class="gn-topbar">', 1)[1].split("</header>", 1)[0]
    assert "data-gn-theme-switch" not in topbar and "data-gn-nav-switch" not in topbar
    assert html.count("data-gn-prefs-toggle") == 1
