# Incorporar un producto nuevo

Desde la 0.3.0, un producto se incorpora a GENEOS UI desde su propio repositorio, sin cambiar `geneos-ui`. El ejemplo completo es **GEFLOTA**, un producto ficticio que vive solo en el sandbox (`sandbox/geflota/` y `sandbox/sandbox/settings_geflota.py`). No forma parte del paquete ni del catálogo.

```bash
cd sandbox
DJANGO_SETTINGS_MODULE=sandbox.settings_geflota python manage.py runserver
# http://127.0.0.1:8000/geflota/
```

## 1. Instalar la biblioteca

```text
# requirements.txt
geneos-ui @ git+https://github.com/sorensenclara/geneos-ui.git@v0.3.0
```

```python
# settings.py
INSTALLED_APPS += ["geneos_ui"]
TEMPLATES[0]["OPTIONS"]["context_processors"] += ["geneos_ui.context_processors.geneos_ui"]
```

## 2. Declarar el producto

Todo lo propio del producto va en `GENEOS_UI`. Este es el de GEFLOTA:

```python
GENEOS_UI = {
    "PRODUCT": "geflota",                              # identificador: minúsculas, números y guiones
    "PRODUCT_NAME": "GEFLOTA",
    "THEME_CSS": ["geflota/css/tema-geflota.css"],     # sus colores (paso 3)
    "NAV": "geflota.navigation.get_nav",               # su menú (paso 4)
    "NAV_LAYOUT": "vertical",                          # disposición por defecto; el usuario puede cambiarla
    "SIDEBAR_DEFAULT": "expanded",
    "NAV_ICONS": "tint",                               # sus SVG blancos también se ven en la barra horizontal clara
    "LOGO_FULL": "geflota/logos/geflota-blanco.svg",   # sobre el sidebar de color
    "LOGO_ICON": "geflota/logos/geflota-iso.svg",      # sidebar contraído
    "LOGO_TOPBAR": "geflota/logos/geflota-color.svg",  # encabezado con menú horizontal (fondo claro)
    "TAGLINE": "Tu flota en orden",
    "HOME_URL": "/",
    "BOOTSTRAP_RGB": {"primary": "179, 86, 9"},        # solo si tiene pantallas con Bootstrap (puente bootstrap5)
}
```

`python manage.py check` valida la configuración: identificador, tema y logos existentes y `NAV_ICONS` válido (ver [`api.md`](api.md#chequeos)).

## 3. Identidad visual

Un CSS en los estáticos del producto con sus colores de identidad. El resto (modo oscuro, estados, foco, barra horizontal, contraste del texto de marca) lo deriva la biblioteca.

```css
/* geflota/static/geflota/css/tema-geflota.css */
@layer geneos-ui {
  [data-gn-product="geflota"] {
    --gn-c-sidebar: #0f3d5c;   --gn-c-sidebar-deep: #0a2c43;
    --gn-c-brand: #b35609;     --gn-c-brand-hover: #9a4a07;  --gn-c-brand-press: #833f06;
    --gn-c-on-brand: #ffffff;  --gn-c-ink: #b35609;
    --gn-c-accent: #f29a3a;    --gn-c-on-accent: #1d1d1d;
    --gn-c-good: #2e8b57;  --gn-c-warning: #e0972b;  --gn-c-critical: #d64545;  --gn-c-info: #1f6f99;  --gn-c-neutral: #64748b;
  }
}
```

Contraste a verificar: blanco sobre `--gn-c-brand` ≥ 4,5:1 (botones), `--gn-c-ink` sobre blanco ≥ 4,5:1 (texto de marca) y `--gn-c-accent` sobre `--gn-c-sidebar` ≥ 3:1 (indicador del activo). Si el color de marca no llega a 3:1 sobre la barra horizontal blanca, se define `--gn-hnav-accent` en el tema, como hace GEAGRO Cereales.

- **Tipografía:** Titillium Web por defecto. Otra fuente: `FONT_CSS` (URL o estático) y `--gn-font` en el tema; `LOAD_FONTS: False` para no cargar ninguna.
- **Logos:** archivos del producto, declarados en `GENEOS_UI`.
- **Íconos:** los `i-*` del sprite sirven para cualquier producto. Los propios van con `NavItem(icon_static="…svg")`. Con `NAV_ICONS: "tint"`, el SVG blanco del sidebar se pinta con los colores del tema en la barra horizontal clara; si el producto tiene una variante clara propia, va en `icon_static_h` (y `icon_static_h_active`). Un manifiesto de íconos como el de la biblioteca se declara con `ICON_MANIFEST`.

## 4. Menú y permisos

```python
# geflota/navigation.py
from geneos_ui.navigation import NavItem, NavSection

def get_nav(request):
    return [
        NavItem("Inicio", url="geflota:inicio", icon_static="geflota/iconos/inicio.svg"),
        NavSection("Operación"),
        NavItem("Vehículos", url="geflota:vehiculos", icon_static="geflota/iconos/vehiculos.svg",
                keywords="patente dominio unidad"),
        NavItem("Mantenimiento", icon_static="geflota/iconos/mantenimiento.svg", children=[
            NavItem("Órdenes de servicio", url="geflota:ordenes"),
            NavItem("Vencimientos", url="geflota:vencimientos", badge="3"),
        ]),
        NavItem("Costos", url="geflota:costos", icon="i-coins", perms=("geflota.view_costos",)),
        NavItem("Choferes", url="geflota:choferes", icon_static="geflota/iconos/choferes.svg",
                visible=lambda r: r.user.groups.filter(name="Administración").exists()),
    ]
```

Las reglas son del producto: `perms` usa los permisos de Django y `visible` cualquier función del `request`. La biblioteca filtra, resuelve las URLs, marca el activo (la ruta más específica) y arma el buscador del menú.

## 5. Pantallas

```django
{% extends "geneos_ui/layouts/app.html" %}
{% load geneos_ui %}
{% block breadcrumbs %}{% gn_breadcrumbs crumbs %}{% endblock %}
{% block content %}
  <table class="gn-table gn-table--responsive">
    <thead><tr>{% gn_sort_th "Patente" "patente" %}<th scope="col">Estado</th></tr></thead>
    <tbody>{% for v in page_obj %}<tr>{% gn_cell "Patente" %}{{ v.patente }}{% endgn_cell %}{% gn_cell "Estado" %}{% gn_badge v.estado "good" True %}{% endgn_cell %}</tr>{% endfor %}</tbody>
  </table>
  {% gn_pagination page_obj %}
{% endblock %}
```

El catálogo marca cada pieza como **Componente** (tag o template: recibe las mejoras al actualizar la versión) o **HTML de referencia** (solo comparten CSS y JS: el HTML se escribe en la pantalla). Ver [`api.md`](api.md).

## Qué recibe el producto sin escribir nada

Layout y encabezado, sidebar con buscador, permisos y cajón en el celular, barra horizontal con su franja y su color, modo claro y oscuro, panel de preferencias, ordenamiento, paginación, badges, breadcrumbs y los mensajes de Django como notificaciones.

## Qué sigue siendo propio

Modelos, vistas y permisos; el contenido de cada pantalla; dashboards, reportes y PDF; los íconos de sus módulos; y, hasta la 0.4.0, el HTML de tarjetas, KPI, filtros, campos de formulario, modales y alertas.
