"""Lectura de settings.GENEOS_UI.

La configuración final se arma en tres capas, cada una pisa a la anterior::

    DEFAULTS  <  presets.PRESETS[PRODUCT] (si existe)  <  settings.GENEOS_UI

Un producto con preset (GELECTRIC, GEMA, GEAGRO Cereales, GEAGRO Vid) solo
necesita ``PRODUCT`` y ``NAV``. Un producto nuevo declara también su tema::

    GENEOS_UI = {
        "PRODUCT": "geflota",                       # identificador: [a-z][a-z0-9-]*
        "PRODUCT_NAME": "GEFLOTA",
        "THEME_CSS": ["flota/css/tema.css"],        # sus colores --gn-c-* (estáticos del producto)
        "NAV": "flota.navigation.get_nav",          # función (request) -> list[NavItem]
        "NAV_LAYOUT": "vertical",                   # "vertical" | "horizontal"; el usuario puede cambiarla
        "NAV_ICONS": "tint",                        # íconos en la barra horizontal clara
        "LOGO_FULL": "flota/logos/blanco.svg",
        "LOGO_ICON": "flota/logos/iso.svg",
        "LOGO_TOPBAR": "flota/logos/color.svg",
    }

Ver ``docs/api.md`` para todas las claves.
"""
import re
import warnings

from django.conf import settings
from django.utils.module_loading import import_string

from . import presets

BRIDGES = ("bootstrap5", "jazzmin")
NAV_LAYOUTS = ("vertical", "horizontal")
SIDEBAR_STATES = ("expanded", "collapsed")
NAV_ICON_MODES = ("tint", "as-is")
PRODUCT_RE = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")

DEFAULTS = {
    "PRODUCT": "gelectric",
    "VARIANT": None,
    "PRODUCT_NAME": None,             # None = el del preset o el identificador
    "NAV": None,
    "THEME_CSS": None,                # lista de rutas de estáticos; None = la del preset
    "FONT_CSS": None,                 # URL o ruta de estáticos; None = Titillium Web si LOAD_FONTS
    "LOAD_FONTS": True,
    "LOGO_FULL": None,
    "LOGO_ICON": None,
    "LOGO_TOPBAR": None,              # logo para fondo claro, en el encabezado con navegación horizontal
    "TAGLINE": "",
    "VERSION_LABEL": "",
    "HOME_URL": "/",
    "BRIDGES": [],
    "BOOTSTRAP_RGB": {},              # {"primary": "224, 122, 16", …} para el puente bootstrap5
    "SIDEBAR_DEFAULT": "expanded",    # "expanded" | "collapsed"
    "SIDEBAR_LEGACY_KEY": None,       # clave vieja de localStorage del sidebar, se migra una vez
    "NAV_LAYOUT": "vertical",         # "vertical" | "horizontal"
    "NAV_ICONS": "tint",              # "tint" | "as-is" | {"rest": variante, "active": variante}
    "ICON_FAMILY": (),                # otros conjuntos del manifiesto que el producto comparte
    "ICON_MANIFEST": None,            # ruta a un manifiesto de íconos propio (mismo formato que product_icons.json)
    "STATIC_VERSION_QUERY": True,     # ?v=<versión> en el CSS y el JS de la biblioteca
    "CATALOG": None,                  # None = solo con DEBUG o para staff
}


def user_settings():
    return getattr(settings, "GENEOS_UI", {}) or {}


def get_config():
    user = user_settings()
    product = user.get("PRODUCT", DEFAULTS["PRODUCT"])
    cfg = {**DEFAULTS, **presets.preset(product), **user}
    cfg["HAS_PRESET"] = product in presets.PRESETS
    if not cfg["PRODUCT_NAME"]:
        cfg["PRODUCT_NAME"] = cfg["PRODUCT"]
    if cfg["SIDEBAR_DEFAULT"] not in SIDEBAR_STATES:
        cfg["SIDEBAR_DEFAULT"] = presets.preset(product).get("SIDEBAR_DEFAULT", DEFAULTS["SIDEBAR_DEFAULT"])
    if cfg["NAV_LAYOUT"] not in NAV_LAYOUTS:
        cfg["NAV_LAYOUT"] = presets.preset(product).get("NAV_LAYOUT", DEFAULTS["NAV_LAYOUT"])
    if cfg["THEME_CSS"] is None:
        cfg["THEME_CSS"] = []
    elif isinstance(cfg["THEME_CSS"], str):
        cfg["THEME_CSS"] = [cfg["THEME_CSS"]]
    if cfg["FONT_CSS"] is None and cfg["LOAD_FONTS"]:
        cfg["FONT_CSS"] = presets.FONT_TITILLIUM
    return cfg


def nav_icons_for(icon_set, cfg=None):
    """Cómo se muestran en la barra horizontal clara los íconos de un conjunto del manifiesto.

    El conjunto del producto actual (o de su ``ICON_FAMILY``) sigue su ``NAV_ICONS``;
    el de otro producto, el de su preset. Así el catálogo muestra los cuatro a la vez.
    """
    cfg = cfg or get_config()
    if icon_set == cfg["PRODUCT"]:
        return cfg["NAV_ICONS"]
    if icon_set in presets.PRESETS:
        return presets.PRESETS[icon_set].get("NAV_ICONS", DEFAULTS["NAV_ICONS"])
    if icon_set in presets.ICON_SETS:
        return presets.ICON_SETS[icon_set].get("NAV_ICONS", DEFAULTS["NAV_ICONS"])
    return cfg["NAV_ICONS"] if icon_set in tuple(cfg["ICON_FAMILY"] or ()) else DEFAULTS["NAV_ICONS"]


def icon_family(product, cfg=None):
    """Conjuntos del manifiesto donde se buscan los íconos "producto:módulo"."""
    cfg = cfg or get_config()
    family = presets.preset(product).get("ICON_FAMILY", ())
    if product == cfg["PRODUCT"]:
        family = cfg["ICON_FAMILY"] or family
    return (product, *tuple(family))


def get_nav_callable(cfg=None):
    cfg = cfg or get_config()
    nav = cfg.get("NAV")
    if not nav:
        return None
    if callable(nav):
        return nav
    return import_string(nav)


# --- compatibilidad con la 0.2.x: se quitan en la 0.4.0 -------------------
def _deprecated(name, value):
    warnings.warn(f"geneos_ui.conf.{name} está deprecado: usar geneos_ui.presets.PRESETS o get_config().",
                  DeprecationWarning, stacklevel=3)
    return value


def __getattr__(name):
    if name == "PRODUCTS":
        return _deprecated(name, {k: v["PRODUCT_NAME"] for k, v in presets.PRESETS.items()})
    if name == "SIDEBAR_DEFAULTS":
        return _deprecated(name, {k: v["SIDEBAR_DEFAULT"] for k, v in presets.PRESETS.items()})
    if name == "NAV_LAYOUT_DEFAULTS":
        return _deprecated(name, {k: v["NAV_LAYOUT"] for k, v in presets.PRESETS.items()})
    raise AttributeError(name)
