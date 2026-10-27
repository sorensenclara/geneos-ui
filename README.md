# geneos-ui

Sistema de diseño y biblioteca de componentes compartida para los productos Django de GENEOS: **GELECTRIC**, **GEMA**, **GEAGRO Cereales** y **GEAGRO Vid**.

La estructura (sidebar, botones, tablas, filtros, formularios) toma como referencia a GELECTRIC. Cada producto conserva su identidad con un tema de color propio y sus logotipos.

> Estado: **v0.1.0, borrador para aprobación.** Todavía no está integrado en ningún producto.

## Qué incluye

| Pieza | Archivo | Descripción |
| --- | --- | --- |
| Tokens | `static/geneos_ui/css/tokens.css` | Neutros, tipografía, espaciado, radios, sombras y colores derivados (`--gn-*`). |
| Temas | `static/geneos_ui/css/themes/*.css` | Un archivo por producto con sus colores reales (`--gn-c-*`). |
| Componentes | `static/geneos_ui/css/geneos-ui.css` | Clases `gn-*` dentro de `@layer geneos-ui`. |
| Puentes | `static/geneos_ui/css/bridges/` | Opcionales: retintan Bootstrap 5 (Lexa) y Jazzmin con los tokens. |
| JavaScript | `static/geneos_ui/js/geneos-ui.js` | Sin dependencias. Sidebar, buscador, dropdowns, pestañas, filtros, tablas, modales, notificaciones y gráficos. |
| Íconos de acciones | `templates/geneos_ui/components/icon_sprite.html` | Sprite SVG de GELECTRIC más acciones genéricas (descargar, eliminar, info…). |
| Iconografía de producto | `static/geneos_ui/icons/<producto>/` y `product_icons.json` | Íconos originales de cada producto, sin modificar, con su nombre, origen y estado de uso. Ver [`docs/iconografia.md`](docs/iconografia.md). |
| Templates | `templates/geneos_ui/` | Layout de aplicación, layout de login, sidebar, breadcrumbs y paginación. |
| Navegación | `geneos_ui/navigation.py` | Menú declarativo con permisos, ítem activo e índice de búsqueda. |
| Catálogo | `/ui-kit/` (vista del paquete) y `dist/ui-kit.html` | Todos los componentes, variantes y estados con los cuatro temas. |

## Compatibilidad

- Python ≥ 3.10, Django ≥ 5.0 y < 6.0 (GELECTRIC 5.x, GEMA 5.2.17, GEAGRO 5.2.5).
- No depende de Bootstrap, jQuery ni de otras librerías. Convive con ellas porque solo usa clases `gn-` y atributos `data-gn-`.
- Navegadores: necesita `color-mix()`, `@layer` y `<dialog>` (Chrome/Edge 111+, Firefox 113+, Safari 16.2+).

## Instalación en un producto

El repositorio principal es **GitHub**: https://github.com/sorensenclara/geneos-ui .

```text
# requirements.txt — usar un tag publicado después de aprobar el diseño
geneos-ui @ git+https://github.com/sorensenclara/geneos-ui.git@v0.1.0
```

```python
# settings.py
INSTALLED_APPS += ["geneos_ui"]

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "geneos_ui.context_processors.geneos_ui",
]

GENEOS_UI = {
    "PRODUCT": "gema",                      # gelectric | gema | geagro-cereales | geagro-vid
    "NAV": "core.navigation.get_nav",       # función (request) -> list[NavItem | NavSection]
    "LOGO_FULL": "core/images/gema-logo-white.svg",
    "LOGO_ICON": "core/images/gema-logo-favicon.svg",
    "TAGLINE": "Gestión de matafuegos",
    "BRIDGES": ["bootstrap5"],              # solo si hay pantallas con Bootstrap sin migrar
    # "SIDEBAR_DEFAULT": "expanded",        # opcional; por defecto GELECTRIC arranca contraído y el resto expandido
}

# urls.py (opcional: catálogo visible con DEBUG o para staff)
path("ui-kit/", include("geneos_ui.urls")),
```

```django
{% extends "geneos_ui/layouts/app.html" %}
{% load geneos_ui %}
{% block content %}…{% endblock %}
```

### Menú del producto

```python
# core/navigation.py
from geneos_ui.navigation import NavItem, NavSection

def get_nav(request):
    u = request.user
    return [
        NavItem("Inicio", url="dashboard", icon="gema:inicio"),
        NavSection("Gestión"),
        NavItem("Clientes", url="cliente:list", icon="gema:clientes",
                visible=lambda r: u.is_company_admin or u.is_operador),
        NavItem("Matafuegos", icon="gema:matafuegos", children=[
            NavItem("Listado", url="matafuegos:list"),
            NavItem("Vencimientos", url="matafuegos:panel-vencimientos",
                    keywords="vencidos por vencer avisos whatsapp"),
        ]),
        NavItem("Usuarios", url="accounts:user-list", icon="gema:usuarios",
                visible=lambda r: u.is_company_admin),
    ]
```

`icon="gema:clientes"` usa el ícono original del producto (variante blanca en el sidebar). Si el módulo no tiene ícono propio, el manifiesto lo marca como pendiente y el sidebar muestra un marcador neutro. Los nombres `i-*` quedan para acciones comunes.

Las reglas de permisos siguen siendo del producto: `perms=("app.view_x",)` usa los permisos de Django y `visible=` acepta cualquier función.

## Template tags

```django
{% load geneos_ui %}
{% gn_css %} {% gn_js %}
{% gn_theme_boot %}                        {# en el <head>: aplica el modo guardado; sin preferencia, claro #}
{% gn_theme_switch %}                      {# selector Claro / Oscuro; guarda la elección en localStorage #}
{% gn_icon "i-download" %}                     {# acción común del sprite #}
{% gn_product_icon "gema:clientes" "base" %}  {# ícono original: white, base, active, tile… #}
{% gn_badge "Vencido" "critical" True %}
{% gn_breadcrumbs crumbs %}                 {# [("Inicio", "/"), ("Clientes", None)] #}
{% gn_sort_th "Nombre" "nombre" %}          {# ?o=nombre / ?o=-nombre, con aria-sort #}
{% gn_cell "Saldo" "is-num" %}…{% endgn_cell %}
{% gn_pagination page_obj %}
{% gn_query page=2 %}
```

## Desarrollo

```bash
pip install -e ".[test]"
pytest
cd sandbox && python manage.py runserver      # http://127.0.0.1:8000/ catálogo · /demo/ listado
GN_PRODUCT=gema python manage.py runserver    # otro producto en el layout de demo
python tools/build_catalog.py                 # dist/ui-kit.html, catálogo en un solo archivo
python tools/import_product_icons.py --check --gelectric … --gema … --geagro …   # copia de íconos idéntica a los originales
```

Los logotipos de `sandbox/static/demo/logos/` son copias de los originales de cada repositorio y se usan solo en el catálogo. El paquete no incluye logotipos: cada producto los declara en `GENEOS_UI`.

## Revisión visual del catálogo

- **Sin instalar nada:** abrir `dist/ui-kit.html` con doble clic. Es un archivo autónomo (solo usa internet para la fuente Titillium Web). Se regenera con `python tools/build_catalog.py`.
- **Con Django:** `cd sandbox && python manage.py runserver` y abrir `http://127.0.0.1:8000/`.
- **Cambiar de producto:** selector arriba a la derecha del encabezado, `?product=gema` en el sandbox o `#gema` en el archivo (`gelectric`, `gema`, `geagro-cereales`, `geagro-vid`).
- **Celular:** herramientas de desarrollo del navegador en modo dispositivo, o `python manage.py runserver 0.0.0.0:8000` y abrir `http://<IP-de-la-computadora>:8000/` desde un teléfono en la misma red.
- **Verificar identidad:** `python tools/verify_identity.py --gelectric … --gema … --geagro …` compara colores, logotipos y tipografías con las ramas de trabajo y escribe `docs/verificacion-identidad.md`.

## Versionado

SemVer con `CHANGELOG.md` y tags `vX.Y.Z`.

- **major**: cambios de markup, nombres de clase o de tokens que obligan a tocar templates.
- **minor**: componentes o variantes nuevas.
- **patch**: correcciones visuales o de comportamiento sin cambios de API.

Los tags se crean en GitLab. Cada producto fija una versión exacta y la actualiza con su propio merge request, en su rama de trabajo (`2026`, `2026-cereales`, `2026-vid`).

Más detalle en [`docs/componentes.md`](docs/componentes.md), [`docs/integracion.md`](docs/integracion.md), [`docs/iconografia.md`](docs/iconografia.md) y [`docs/pendientes.md`](docs/pendientes.md).
