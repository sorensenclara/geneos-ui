# API pública de GENEOS UI

Todo lo que figura en este documento es contrato: un producto puede usarlo y un cambio incompatible solo llega en una versión mayor (ver [`versionado.md`](versionado.md)). Lo que no figura acá, como las clases internas, las funciones con `_` o los archivos del catálogo, puede cambiar en cualquier versión.

## Configuración: `settings.GENEOS_UI`

Se arma en tres capas: valores por defecto < preset del producto (`geneos_ui/presets.py`, solo GELECTRIC, GEMA, GEAGRO Cereales y GEAGRO Vid) < `GENEOS_UI`.

| Clave | Valor | Por defecto |
| --- | --- | --- |
| `PRODUCT` | Identificador: `[a-z][a-z0-9-]*`. Va en `data-gn-product`. | `"gelectric"` |
| `PRODUCT_NAME` | Nombre visible. | El del preset o el identificador |
| `THEME_CSS` | Lista de CSS del tema (rutas de estáticos). | La del preset; un producto sin preset la necesita (E003) |
| `FONT_CSS` | URL o estático de la fuente. | Titillium Web (Google Fonts) si `LOAD_FONTS` |
| `LOAD_FONTS` | `False` = no cargar ninguna fuente. | `True` |
| `NAV` | Función `(request) -> list[NavItem \| NavSection]`, o su ruta como texto. | `None` |
| `NAV_LAYOUT` | `"vertical"` o `"horizontal"`: disposición inicial en escritorio. | Preset o `"vertical"` |
| `SIDEBAR_DEFAULT` | `"expanded"` o `"collapsed"`. | Preset o `"expanded"` |
| `NAV_ICONS` | Íconos en la barra horizontal clara: `"tint"`, `"as-is"` o `{"rest": variante, "active": variante o None}` del manifiesto. | Preset o `"tint"` |
| `LOGO_FULL`, `LOGO_ICON`, `LOGO_TOPBAR` | Estáticos: sobre el sidebar, sidebar contraído, encabezado claro. | `None` |
| `TAGLINE`, `VERSION_LABEL`, `HOME_URL` | Pie del sidebar y enlace del logo. | `""`, `""`, `"/"` |
| `VARIANT` | Variante del tema (`data-gn-variant`), p. ej. el azul histórico de GELECTRIC. | `None` |
| `BRIDGES` | `["bootstrap5"]`, `["jazzmin"]`. | `[]` |
| `BOOTSTRAP_RGB` | `{"primary": "r, g, b", …}` para el puente `bootstrap5`. | El del preset o `{}` |
| `SIDEBAR_LEGACY_KEY` | Clave vieja de `localStorage` del sidebar que se migra una vez. | `None` |
| `ICON_FAMILY` | Otros conjuntos del manifiesto que comparte (GEAGRO: `("geagro",)`). | `()` |
| `ICON_MANIFEST` | Ruta a un manifiesto de íconos propio, con el formato de `product_icons.json`. | `None` |
| `STATIC_VERSION_QUERY` | `?v=<versión>` en el CSS y el JS de la biblioteca. | `True` |
| `CATALOG` | Catálogo visible: `True`, `False` o `None` (con `DEBUG` o para staff). | `None` |

## Template tags (`{% load geneos_ui %}`)

| Tag | Uso |
| --- | --- |
| `{% gn_css [producto] [puentes] %}` | Fuente, tokens, tema, componentes, puentes y tripletes de Bootstrap. |
| `{% gn_js %}` | JavaScript de la biblioteca (`defer`). |
| `{% gn_theme_boot %}`, `{% gn_nav_boot %}` | En el `<head>`: aplican el tema y la disposición guardados antes de pintar. |
| `{% gn_prefs %}` | Solapa de preferencias (ya incluida en `layouts/app.html`). |
| `{% gn_theme_switch %}`, `{% gn_nav_switch %}` | Selectores sueltos, si un producto los quiere en otro lugar. |
| `{% gn_sidebar [nav] [sidebar_id] [gn] [hidden] %}` | Menú (ya incluido en el layout). |
| `{% gn_breadcrumbs crumbs %}` | `[("Inicio", "/"), ("Clientes", None)]`. |
| `{% gn_pagination page_obj [sizes] [param] [size_param] %}` | Paginación que conserva los filtros. |
| `{% gn_sort_th "Etiqueta" "campo" [param] [css_class] %}` | Encabezado ordenable (`?o=campo` / `?o=-campo`, `aria-sort`). |
| `{% gn_cell "Etiqueta" [css_class] %}…{% endgn_cell %}` | `<td data-th>` para tablas responsive. |
| `{% gn_query clave=valor %}` | Querystring actual con cambios. |
| `{% gn_badge "texto" tipo [punto] %}` | Tipos: `good`, `warning`, `critical`, `info`, `neutral`, `brand`, `solid`. |
| `{% gn_icon "i-nombre" [css_class] [label] %}` | Ícono del sprite. |
| `{% gn_product_icon "producto:módulo" [variante] [css_class] [label] [set_name] %}` | Ícono original del manifiesto. |
| `{% gn_messages_json %}` | Mensajes de Django como notificaciones (ya incluido en el layout). |

Los tags que escriben `<script>` o `<style>` en línea agregan el `nonce` de CSP si está en el contexto (`csp_nonce`) o en el request (`request.csp_nonce`).

## Navegación: `geneos_ui.navigation`

`NavItem(label, url=None, url_args=(), url_kwargs={}, icon=None, icon_static=None, children=[], perms=(), visible=None, keywords="", badge=None, match=(), id=None, icon_static_h=None, icon_static_h_active=None)` y `NavSection(label, perms=(), visible=None)`. Se usan siempre con argumentos por nombre, salvo `label`.

## Layouts y bloques

`geneos_ui/layouts/app.html`: `title`, `favicon`, `head_css`, `extra_css`, `body_class`, `sidebar`, `topbar_brand`, `topbar_search`, `topbar_context`, `topbar_actions`, `user_menu`, `user_menu_items`, `user_role`, `logout`, `breadcrumbs`, `page_head`, `content`, `prefs`, `extra_js`.

`geneos_ui/layouts/auth.html`: `title`, `auth_content`.

Sobrescribir un template de la biblioteca copiándolo en el producto deja ese componente sin las mejoras de las versiones siguientes (aviso W003). Para personalizar, se usan los bloques.

## CSS

- **Tokens de identidad** que define cada tema: `--gn-c-sidebar`, `--gn-c-sidebar-deep`, `--gn-c-brand`, `--gn-c-brand-hover`, `--gn-c-brand-press`, `--gn-c-on-brand`, `--gn-c-ink`, `--gn-c-accent`, `--gn-c-on-accent`, `--gn-c-good`, `--gn-c-warning`, `--gn-c-critical`, `--gn-c-info` y `--gn-c-neutral`; opcionales `--gn-flourish`, `--gn-chart-1…4` y `--gn-font`.
- **Tokens de la barra horizontal** que un tema puede ajustar: `--gn-hnav-accent`, `--gn-hnav-band`, `--gn-hnav-band-h` y `--gn-hnav-icon-tint`.
- **Tokens semánticos y clases `gn-*`:** ver [`componentes.md`](componentes.md). Todo va dentro de `@layer geneos-ui`.

## JavaScript

- **Objeto `GN`:** `GN.version`, `GN.init(root)`, `GN.toast(texto, {kind, title})`, `GN.announce(texto)`, `GN.openModal(id)`, `GN.closeModal(id)`, `GN.setLoading(botón, bool, texto)`, `GN.renderCharts(root)`, `GN.setTheme(t)`, `GN.getTheme()`, `GN.setNav(n)`, `GN.getNav()`, `GN.setNavDefault(n)`, `GN.prefs.open()` / `GN.prefs.close()` y `GN.sidebar.expand()` / `collapse()` / `open()` / `close()`.
- **Eventos en `document`:** `gn:theme` (`detail.theme`), `gn:nav` (`detail.layout`), `gn:filters` y `gn:pill`.
- **Atributos `data-gn-*`** que activan comportamiento: los de [`componentes.md`](componentes.md).

## Claves de `localStorage`

`gn-theme`, `gn-nav` y `gn-sidebar-expanded:<producto>`. No cambian entre versiones menores: si cambiaran, los usuarios perderían lo que eligieron.

## Chequeos

| Código | Qué controla |
| --- | --- |
| `geneos_ui.E001` | `PRODUCT` con formato inválido. |
| `geneos_ui.E002` | Puente desconocido. |
| `geneos_ui.E003` | Producto sin preset y sin `THEME_CSS`. |
| `geneos_ui.E004` | Un archivo de `THEME_CSS` no está en los estáticos. |
| `geneos_ui.E005` | `NAV_ICONS` inválido. |
| `geneos_ui.W001` | `SIDEBAR_DEFAULT` inválido. |
| `geneos_ui.W002` | Un logo no está en los estáticos. |
| `geneos_ui.W003` | Un template de componente está sobrescrito en el producto. |

## Deprecado

| Qué | Desde | Se quita en | Reemplazo |
| --- | --- | --- | --- |
| `geneos_ui.conf.PRODUCTS`, `SIDEBAR_DEFAULTS`, `NAV_LAYOUT_DEFAULTS` | 0.3.0 | 0.4.0 | `geneos_ui.presets.PRESETS` o `get_config()` |
| `geneos_ui.product_icons.HNAV_VARIANTS`, `HNAV_TINT` | 0.3.0 | 0.4.0 | `GENEOS_UI["NAV_ICONS"]` |
