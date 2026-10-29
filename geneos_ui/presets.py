"""Presets de los productos de GENEOS que ya usan la biblioteca.

Es el único lugar del código de ``geneos_ui`` que nombra a un producto. Un
preset es lo mismo que un producto escribiría en ``GENEOS_UI``: la
configuración final se arma como

    valores por defecto  <  preset del producto (si existe)  <  settings.GENEOS_UI

Un producto nuevo no necesita preset: declara estas mismas claves en su
``settings.py`` (ver ``docs/nuevo-producto.md``).
"""

# Valores por defecto para cualquier producto, con o sin preset.
FONT_TITILLIUM = "https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap"

PRESETS = {
    "gelectric": {
        "PRODUCT_NAME": "GELECTRIC",
        "THEME_CSS": ["geneos_ui/css/themes/gelectric.css"],
        "BOOTSTRAP_RGB": {"primary": "27, 107, 76", "success": "23, 166, 114", "danger": "229, 72, 77"},
        # decisión del 26/10/2026: GELECTRIC arranca con el sidebar contraído, como hoy
        "SIDEBAR_DEFAULT": "collapsed",
        "NAV_LAYOUT": "vertical",
        # barra horizontal clara: los íconos de color de los módulos (no hay variante activa)
        "NAV_ICONS": {"rest": "tile", "active": None},
        # GELECTRIC guardaba el sidebar con esta clave ("1" = expandido); se migra una vez
        "SIDEBAR_LEGACY_KEY": "geletric-sidebar-pinned",
    },
    "gema": {
        "PRODUCT_NAME": "GEMA",
        "THEME_CSS": ["geneos_ui/css/themes/gema.css"],
        "BOOTSTRAP_RGB": {"primary": "236, 108, 5", "danger": "198, 40, 40", "success": "23, 166, 114"},
        "SIDEBAR_DEFAULT": "expanded",
        "NAV_LAYOUT": "horizontal",
        # menú superior de GEMA (core/base.html): SVG normal y "-active"
        "NAV_ICONS": {"rest": "base", "active": "active"},
    },
    "geagro-cereales": {
        "PRODUCT_NAME": "GEAGRO Cereales",
        "THEME_CSS": ["geneos_ui/css/themes/geagro-cereales.css"],
        "BOOTSTRAP_RGB": {"primary": "198, 164, 0", "success": "90, 153, 76", "danger": "207, 78, 78", "info": "17, 130, 55"},
        "SIDEBAR_DEFAULT": "expanded",
        "NAV_LAYOUT": "vertical",
        # solo hay SVG blancos completos: en la barra clara se pintan con los tokens del tema
        "NAV_ICONS": "tint",
        # comparte los íconos de "geagro" con Vid
        "ICON_FAMILY": ("geagro",),
    },
    "geagro-vid": {
        "PRODUCT_NAME": "GEAGRO Vid",
        "THEME_CSS": ["geneos_ui/css/themes/geagro-vid.css"],
        "BOOTSTRAP_RGB": {"primary": "107, 63, 110", "success": "90, 153, 76", "danger": "207, 78, 78", "info": "17, 130, 55"},
        "SIDEBAR_DEFAULT": "expanded",
        "NAV_LAYOUT": "vertical",
        "NAV_ICONS": "tint",
        "ICON_FAMILY": ("geagro",),
    },
}

# Conjuntos de íconos del manifiesto que no son un producto en sí ("geagro" son
# los archivos comunes de Cereales y Vid): cómo se muestran en la barra clara.
ICON_SETS = {
    "geagro": {"NAV_ICONS": "tint"},
}


def preset(product):
    return PRESETS.get(product, {})
