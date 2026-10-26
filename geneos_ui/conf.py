"""Lectura y validación de settings.GENEOS_UI.

Ejemplo en el settings de un producto::

    GENEOS_UI = {
        "PRODUCT": "gelectric",                 # tema a cargar
        "NAV": "core.navigation.get_nav",       # función (request) -> list[NavItem]
        "PRODUCT_NAME": "GELETRIC",
        "LOGO_FULL": "core/images/SVG/Isologotipo GELETRIC white.svg",
        "LOGO_ICON": "core/images/SVG/Iso GELETRIC.svg",
        "TAGLINE": "Energía que nos une",
        "BRIDGES": [],                          # "bootstrap5", "jazzmin"
    }
"""
from django.conf import settings
from django.utils.module_loading import import_string

PRODUCTS = {
    "gelectric": "GELECTRIC",
    "gema": "GEMA",
    "geagro-cereales": "GEAGRO Cereales",
    "geagro-vid": "GEAGRO Vid",
}
BRIDGES = ("bootstrap5", "jazzmin")

# Estado inicial del sidebar en escritorio para cada producto (decisión del
# 26/10/2026: GELECTRIC arranca contraído, como hoy). Cada producto puede
# cambiarlo con GENEOS_UI["SIDEBAR_DEFAULT"]; el usuario después elige y el
# navegador lo recuerda.
SIDEBAR_DEFAULTS = {
    "gelectric": "collapsed",
    "gema": "expanded",
    "geagro-cereales": "expanded",
    "geagro-vid": "expanded",
}

DEFAULTS = {
    "PRODUCT": "gelectric",
    "VARIANT": None,
    "PRODUCT_NAME": None,
    "NAV": None,
    "LOGO_FULL": None,
    "LOGO_ICON": None,
    "TAGLINE": "",
    "VERSION_LABEL": "",
    "HOME_URL": "/",
    "BRIDGES": [],
    "SIDEBAR_DEFAULT": None,         # "expanded" | "collapsed"; None = el valor del producto
    "LOAD_FONTS": True,              # Titillium Web desde Google Fonts
    "CATALOG": None,                 # None = solo con DEBUG o para staff
}


def get_config():
    user = getattr(settings, "GENEOS_UI", {}) or {}
    cfg = {**DEFAULTS, **user}
    if not cfg["SIDEBAR_DEFAULT"]:
        cfg["SIDEBAR_DEFAULT"] = SIDEBAR_DEFAULTS.get(cfg["PRODUCT"], "expanded")
    if not cfg["PRODUCT_NAME"]:
        cfg["PRODUCT_NAME"] = PRODUCTS.get(cfg["PRODUCT"], cfg["PRODUCT"])
    return cfg


def get_nav_callable(cfg=None):
    cfg = cfg or get_config()
    nav = cfg.get("NAV")
    if not nav:
        return None
    if callable(nav):
        return nav
    return import_string(nav)
