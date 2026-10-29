"""GEFLOTA: así declara un producto nuevo su integración con GENEOS UI.

Todo lo propio del producto está en este bloque GENEOS_UI y en la app
``geflota`` (menú, pantallas, tema, logos e íconos). geneos_ui/ no se toca.
"""
from .settings import *  # noqa: F401,F403

GENEOS_UI = {
    "PRODUCT": "geflota",
    "PRODUCT_NAME": "GEFLOTA",
    "THEME_CSS": ["geflota/css/tema-geflota.css"],
    "NAV": "geflota.navigation.get_nav",
    "NAV_LAYOUT": "vertical",
    "SIDEBAR_DEFAULT": "expanded",
    "NAV_ICONS": "tint",
    "LOGO_FULL": "geflota/logos/geflota-blanco.svg",
    "LOGO_ICON": "geflota/logos/geflota-iso.svg",
    "LOGO_TOPBAR": "geflota/logos/geflota-color.svg",
    "TAGLINE": "Tu flota en orden",
    "VERSION_LABEL": "v0.1 · prueba",
    "HOME_URL": "/geflota/",
    "BOOTSTRAP_RGB": {"primary": "179, 86, 9"},
}
