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
| `VARIANTS` | Variantes de color que el usuario elige en Preferencias: `[("", "Verde"), ("blue", "Azul")]`. `""` es el tema base. | Preset o `()` |
| `VARIANT_LEGACY` | `{"key": "clave-vieja", "values": {"valor viejo": "variante"}}`: la elección guardada con un selector anterior se migra una vez. | Preset o `None` |
| `NAV_FOOTER` | Función `(request) -> list[NavItem]` (o su ruta): pie del sidebar, p. ej. «Ayuda y soporte». En el menú horizontal va al menú del usuario. | `None` |
| `USER_MENU` | Función `(request) -> list[NavItem]`: opciones del menú del usuario. | `None` |
| `LOGOUT_URL` | Nombre de URL o ruta: «Cerrar sesión» en el menú del usuario, como formulario POST con CSRF. | `None` |
| `LEGACY_CSS` | CSS existente del producto (estáticos), cargado en la capa `legacy` después de la biblioteca. | `[]` |
| `SIDEBAR_ICONS` | `"as-is"` o `"tint"`: los íconos propios del sidebar se pintan con los colores del sidebar (reposo, hover y activo). | `"as-is"` |
| `CATALOG` | Catálogo visible: `True`, `False` o `None` (con `DEBUG` o para staff). | `None` |

## Template tags (`{% load geneos_ui %}`)

| Tag | Uso |
| --- | --- |
| `{% gn_css [producto] [puentes] %}` | Fuente, tokens, tema, componentes, puentes y tripletes de Bootstrap. |
| `{% gn_js %}` | JavaScript de la biblioteca (`defer`). |
| `{% gn_datetime_js %}` | Cally (módulo) y `datetime.js`: lo mismo que `{{ form.media }}` de los widgets de fecha y hora (0.5.0). |
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
| `{% gn_any_icon ref [css_class] [label] [as var] %}` | `"i-nombre"` (sprite), `"producto:módulo"` (ícono original; si está pendiente, nada) o ruta de estáticos. |
| `{% gn_page_head title= [subtitle=] [eyebrow=] [icon=] %}acciones{% endgn_page_head %}` | Encabezado de pantalla con ícono opcional. Sin acciones: `{% gn_page_head … only %}`. |
| `{% gn_link_list items=lista [columns=2] [empty_status=] [label=] %}` | Lista de funcionalidades: cada ítem `{label, href, description, icon, status, status_kind}`. Dos columnas en escritorio, una en el celular; nombres completos en hasta dos líneas. Sin `href`, el ítem no es un enlace. |
| `{% gn_link_list %}{% gn_link_item label= href= … %}…{% endgn_link_list %}` | La misma lista escrita en el template. |
| `{% gn_prefs [products] %}` | Con `VARIANTS`, agrega el grupo «Color». |

Los tags que escriben `<script>` o `<style>` en línea agregan el `nonce` de CSP si está en el contexto (`csp_nonce`) o en el request (`request.csp_nonce`).

## Widgets: `geneos_ui.widgets` (0.5.0)

| Widget | Sin JS | Con JS (se ve y se envía) |
| --- | --- | --- |
| `GnDateTimeInput(attrs=None, *, minute_step=5, default_time=None, invalid_message=None, picker_label=None)` | `datetime-local` | `dd/mm/aaaa HH:mm` |
| `GnDateInput(…)` | `date` | `dd/mm/aaaa` |
| `GnTimeInput(…)` | `time` | `HH:mm` |

`min` y `max` van en `attrs`, en ISO. Funciones de lectura: `parse_date`, `parse_time`, `parse_datetime` (aceptan el formato visible y el ISO; devuelven `None` si no es válido). `datetime_media()` devuelve el `Media` de los tres.

## Navegación: `geneos_ui.navigation`

`NavItem(label, url=None, url_args=(), url_kwargs={}, icon=None, icon_static=None, children=[], perms=(), visible=None, keywords="", badge=None, match=(), id=None, icon_static_h=None, icon_static_h_active=None, search_links=[])`, `NavSection(label, perms=(), visible=None)` y `NavLink(label, url=None, url_args=(), url_kwargs={}, perms=(), visible=None, keywords="")`. Se usan siempre con argumentos por nombre, salvo `label`.

- `search_links`: funcionalidades que no son ítems del menú pero se encuentran con el buscador del sidebar. Aparecen debajo de su ítem solo cuando coinciden, respetan `perms` y `visible`, y Enter abre la primera.
- `url` acepta nombres de URL, rutas, `http(s)://`, `mailto:` y `tel:`. En `NAV_FOOTER` y `USER_MENU`, un ítem sin URL o con `"#"` no se muestra.

## Layouts y bloques

`geneos_ui/layouts/app.html`: `title`, `favicon`, `head_css`, `extra_css`, `body_class`, `sidebar`, `topbar_brand`, `topbar_search`, `topbar_context`, `topbar_actions`, `user_menu`, `user_menu_items`, `user_role`, `logout`, `breadcrumbs`, `page_head`, `content_attrs`, `content`, `prefs`, `extra_js`.

`content_attrs` agrega atributos al `<main>`. Para pantallas existentes que todavía no tienen modo oscuro:

- `data-gn-legacy`: en oscuro, el contenido se muestra en un panel claro (`--gn-legacy-light-bg`, `--gn-legacy-light-text`). Nada cambia en claro.
- `data-gn-legacy="dark"`: el producto traduce sus variables CSS a los tokens `--gn-*` en un CSS puente (ver [`integracion.md`](integracion.md#css-existente-y-modo-oscuro)).

`geneos_ui/layouts/auth.html`: `title`, `auth_content`.

Sobrescribir un template de la biblioteca copiándolo en el producto deja ese componente sin las mejoras de las versiones siguientes (aviso W003). Para personalizar, se usan los bloques.

## CSS

- **Tokens de identidad** que define cada tema: `--gn-c-sidebar`, `--gn-c-sidebar-deep`, `--gn-c-brand`, `--gn-c-brand-hover`, `--gn-c-brand-press`, `--gn-c-on-brand`, `--gn-c-ink`, `--gn-c-accent`, `--gn-c-on-accent`, `--gn-c-good`, `--gn-c-warning`, `--gn-c-critical`, `--gn-c-info` y `--gn-c-neutral`; opcionales `--gn-flourish`, `--gn-chart-1…4` y `--gn-font`.
- **Tokens de la barra horizontal** que un tema puede ajustar: `--gn-hnav-accent`, `--gn-hnav-band`, `--gn-hnav-band-h` y `--gn-hnav-icon-tint`.
- **Tokens semánticos y clases `gn-*`:** ver [`componentes.md`](componentes.md). Todo va dentro de `@layer geneos-ui`.

## JavaScript

- **Objeto `GN`:** `GN.version`, `GN.init(root)`, `GN.toast(texto, {kind, title})`, `GN.announce(texto)`, `GN.openModal(id)`, `GN.closeModal(id)`, `GN.setLoading(botón, bool, texto)`, `GN.renderCharts(root)`, `GN.setTheme(t)`, `GN.getTheme()`, `GN.setNav(n)`, `GN.getNav()`, `GN.setNavDefault(n)`, `GN.setVariant(v)`, `GN.getVariant()`, `GN.prefs.open()` / `GN.prefs.close()` y `GN.sidebar.expand()` / `collapse()` / `open()` / `close()`. Con `datetime.js` (0.5.0): `GN.datetime.value(input)`, `GN.datetime.setValue(input, iso)`, `GN.datetime.validate(input)`, `GN.datetime.parseDate/parseTime/parseDateTime`, `GN.popover.open(panel, ancla, botón)` / `GN.popover.close()` y `GN.initDateTime(root)`.
- **Eventos en `document`:** `gn:theme` (`detail.theme`), `gn:nav` (`detail.layout`), `gn:variant` (`detail.product`, `detail.variant`), `gn:filters` y `gn:pill`.
- **Atributos `data-gn-*`** que activan comportamiento: los de [`componentes.md`](componentes.md).

## Claves de `localStorage`

`gn-theme`, `gn-nav`, `gn-sidebar-expanded:<producto>` y `gn-variant:<producto>` (desde la 0.4.0). No cambian entre versiones menores: si cambiaran, los usuarios perderían lo que eligieron.

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
| `geneos_ui.E006` | `SIDEBAR_ICONS` inválido. |
| `geneos_ui.W003` | Un template de componente está sobrescrito en el producto. |
| `geneos_ui.W004` | Un archivo de `LEGACY_CSS` no está en los estáticos. |

## Deprecado

Nada deprecado en la 0.4.0.

## Quitado

| Qué | Deprecado en | Quitado en | Reemplazo |
| --- | --- | --- | --- |
| `geneos_ui.conf.PRODUCTS`, `SIDEBAR_DEFAULTS`, `NAV_LAYOUT_DEFAULTS` | 0.3.0 | 0.4.0 | `geneos_ui.presets.PRESETS` o `get_config()` |
| `geneos_ui.product_icons.HNAV_VARIANTS`, `HNAV_TINT` | 0.3.0 | 0.4.0 | `GENEOS_UI["NAV_ICONS"]` |
