"""Configuración por capas: valores por defecto < preset < GENEOS_UI."""
import warnings

import pytest

from geneos_ui import presets
from geneos_ui.conf import get_config, nav_icons_for

# valores de la 0.2.1 (conf.py, product_icons.py y bridges/bootstrap5.css de ese tag)
V021 = {
    "gelectric": {"PRODUCT_NAME": "GELECTRIC", "SIDEBAR_DEFAULT": "collapsed", "NAV_LAYOUT": "vertical",
                  "NAV_ICONS": {"rest": "tile", "active": None},
                  "BOOTSTRAP_RGB": {"primary": "27, 107, 76", "success": "23, 166, 114", "danger": "229, 72, 77"}},
    "gema": {"PRODUCT_NAME": "GEMA", "SIDEBAR_DEFAULT": "expanded", "NAV_LAYOUT": "horizontal",
             "NAV_ICONS": {"rest": "base", "active": "active"},
             "BOOTSTRAP_RGB": {"primary": "236, 108, 5", "danger": "198, 40, 40", "success": "23, 166, 114"}},
    "geagro-cereales": {"PRODUCT_NAME": "GEAGRO Cereales", "SIDEBAR_DEFAULT": "expanded", "NAV_LAYOUT": "vertical", "NAV_ICONS": "tint",
                        "BOOTSTRAP_RGB": {"primary": "198, 164, 0", "success": "90, 153, 76", "danger": "207, 78, 78", "info": "17, 130, 55"}},
    "geagro-vid": {"PRODUCT_NAME": "GEAGRO Vid", "SIDEBAR_DEFAULT": "expanded", "NAV_LAYOUT": "vertical", "NAV_ICONS": "tint",
                   "BOOTSTRAP_RGB": {"primary": "107, 63, 110", "success": "90, 153, 76", "danger": "207, 78, 78", "info": "17, 130, 55"}},
}


@pytest.mark.parametrize("product", sorted(V021))
def test_los_presets_dan_los_valores_de_la_0_2_1(settings, product):
    settings.GENEOS_UI = {"PRODUCT": product}
    cfg = get_config()
    for key, value in V021[product].items():
        assert cfg[key] == value, key
    assert cfg["THEME_CSS"] == [f"geneos_ui/css/themes/{product}.css"]
    assert cfg["FONT_CSS"] == presets.FONT_TITILLIUM


def test_settings_pisa_al_preset(settings):
    settings.GENEOS_UI = {"PRODUCT": "gema", "NAV_LAYOUT": "vertical", "SIDEBAR_DEFAULT": "collapsed", "LOAD_FONTS": False}
    cfg = get_config()
    assert (cfg["NAV_LAYOUT"], cfg["SIDEBAR_DEFAULT"], cfg["FONT_CSS"]) == ("vertical", "collapsed", None)
    assert cfg["NAV_ICONS"] == {"rest": "base", "active": "active"}  # lo que no se declara sigue saliendo del preset


def test_valores_invalidos_vuelven_al_preset(settings):
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "NAV_LAYOUT": "diagonal", "SIDEBAR_DEFAULT": None}
    cfg = get_config()
    assert (cfg["NAV_LAYOUT"], cfg["SIDEBAR_DEFAULT"]) == ("vertical", "collapsed")


def test_producto_sin_preset_usa_los_valores_por_defecto(settings):
    settings.GENEOS_UI = {"PRODUCT": "geflota", "THEME_CSS": "flota/css/tema.css"}
    cfg = get_config()
    assert cfg["THEME_CSS"] == ["flota/css/tema.css"] and cfg["PRODUCT_NAME"] == "geflota"
    assert (cfg["NAV_LAYOUT"], cfg["SIDEBAR_DEFAULT"], cfg["NAV_ICONS"]) == ("vertical", "expanded", "tint")
    assert cfg["SIDEBAR_LEGACY_KEY"] is None and cfg["BOOTSTRAP_RGB"] == {} and not cfg["HAS_PRESET"]


def test_modo_de_iconos_por_conjunto(settings):
    # el catálogo muestra los cuatro productos con la configuración de uno solo
    settings.GENEOS_UI = {"PRODUCT": "gelectric"}
    assert nav_icons_for("gema") == {"rest": "base", "active": "active"}
    assert nav_icons_for("geagro") == "tint" and nav_icons_for("geagro-vid") == "tint"
    settings.GENEOS_UI = {"PRODUCT": "gema", "NAV_ICONS": "as-is"}
    assert nav_icons_for("gema") == "as-is"


def test_alias_de_la_0_2_x_con_aviso():
    from geneos_ui import conf, product_icons
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        assert conf.PRODUCTS == {k: v["PRODUCT_NAME"] for k, v in V021.items()}
        assert conf.SIDEBAR_DEFAULTS["gelectric"] == "collapsed"
        assert conf.NAV_LAYOUT_DEFAULTS["gema"] == "horizontal"
        assert product_icons.HNAV_VARIANTS == {"gema": ("base", "active"), "gelectric": ("tile", None)}
        assert product_icons.HNAV_TINT == {"geagro", "geagro-cereales", "geagro-vid"}
    assert len(w) == 5 and all(issubclass(x.category, DeprecationWarning) for x in w)


def test_claves_del_navegador_no_cambian():
    """Si cambian, los usuarios pierden el tema, el menú o el sidebar que eligieron."""
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent / "geneos_ui"
    js = (root / "static/geneos_ui/js/geneos-ui.js").read_text()
    sidebar = (root / "templates/geneos_ui/components/sidebar.html").read_text()
    assert 'THEME_KEY = "gn-theme"' in js and 'NAV_KEY = "gn-nav"' in js and 'PIN_KEY = "gn-sidebar-expanded"' in js
    assert 'data-gn-storage-key="gn-sidebar-expanded:{{ gn.product }}"' in sidebar
    assert presets.PRESETS["gelectric"]["SIDEBAR_LEGACY_KEY"] == "geletric-sidebar-pinned"
