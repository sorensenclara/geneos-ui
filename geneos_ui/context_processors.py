"""Context processor de GENEOS UI.

Agregar a TEMPLATES[...]["OPTIONS"]["context_processors"]::

    "geneos_ui.context_processors.geneos_ui",

Deja disponible ``gn`` en todos los templates: producto, logos, menú ya
filtrado por permisos y configuración del sidebar.
"""
from .conf import get_config, get_nav_callable
from .navigation import build_nav


def geneos_ui(request):
    cfg = get_config()
    nav_fn = get_nav_callable(cfg)
    nav = build_nav(nav_fn(request), request) if nav_fn else []
    return {
        "gn": {
            "product": cfg["PRODUCT"],
            "variant": cfg["VARIANT"],
            "product_name": cfg["PRODUCT_NAME"],
            "logo_full": cfg["LOGO_FULL"],
            "logo_icon": cfg["LOGO_ICON"],
            "logo_topbar": cfg["LOGO_TOPBAR"],
            "tagline": cfg["TAGLINE"],
            "version_label": cfg["VERSION_LABEL"],
            "home_url": cfg["HOME_URL"],
            "bridges": cfg["BRIDGES"],
            "sidebar_default": cfg["SIDEBAR_DEFAULT"],
            "nav_layout": cfg["NAV_LAYOUT"],
            "load_fonts": cfg["LOAD_FONTS"],
            "nav": nav,
        }
    }
