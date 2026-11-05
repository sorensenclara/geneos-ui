"""Context processor de GENEOS UI.

Agregar a TEMPLATES[...]["OPTIONS"]["context_processors"]::

    "geneos_ui.context_processors.geneos_ui",

Deja disponible ``gn`` en todos los templates: producto, logos, menú ya
filtrado por permisos y configuración del sidebar.
"""
from .conf import _callable, get_config, get_nav_callable
from .navigation import build_links, build_nav


def geneos_ui(request):
    cfg = get_config()
    nav_fn = get_nav_callable(cfg)
    nav = build_nav(nav_fn(request), request) if nav_fn else []
    footer_fn, user_fn = _callable(cfg["NAV_FOOTER"]), _callable(cfg["USER_MENU"])
    logout = None
    if cfg["LOGOUT_URL"]:
        from .navigation import NavItem
        logout = (build_links([NavItem("Cerrar sesión", url=cfg["LOGOUT_URL"])], request) or [{}])[0].get("href")
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
            "sidebar_legacy_key": cfg["SIDEBAR_LEGACY_KEY"],
            "nav_layout": cfg["NAV_LAYOUT"],
            "load_fonts": cfg["LOAD_FONTS"],
            "nav": nav,
            "nav_footer": build_links(footer_fn(request), request) if footer_fn else [],
            "user_menu": build_links(user_fn(request), request) if user_fn else [],
            "logout_url": logout,
            "variants": cfg["VARIANTS"],
            "sidebar_icons": cfg["SIDEBAR_ICONS"],
            "type_scale": cfg["TYPE_SCALE"],
        }
    }
