# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [Sin publicar] · 0.6.0

Escala tipográfica legible, opcional. Los productos que no la activan no cambian: el HTML y las capturas del catálogo son idénticos a la 0.5.0.

### Agregado
- `GENEOS_UI["TYPE_SCALE"]`: `"compacta"` (predeterminada) o `"legible"`. La legible agrega `data-gn-type="legible"` en `<html>` (layouts de la aplicación y de acceso): base de 15 px, tablas y secundarios de 14, ayudas de 13, ningún texto por debajo de 12, interlineado 1,5, controles de 36 px en escritorio y 40 hasta 860 px, campos de 16 px en el celular (iOS no hace zoom) y valores de KPI de 30 px. Chequeo `geneos_ui.E007` para un valor inválido; `gn.type_scale` en el contexto.
- Tokens por función: `--gn-fs-label`, `-meta`, `-control`, `-body`, `-input`, `-input-sm`, `-input-xs`, `-input-lg`, `-nav`, `-control-lg`, `-emph`, `-kpi-label`, `-card-title`, `-modal-title`, `-auth-title`, `-counter`, `-chart-axis`, `-donut-value`, `-donut-label`, `--gn-fs-3xl`, `--gn-lh-tight/-snug/-base`, `--gn-size-counter` y `--gn-field-h` (alto de campos, buscador y botón del menú: 36 px, 40 en el celular con la escala legible).
- Tests: `tests/test_type_scale.py` y `tests/visual/test_type_scale.py` (Chromium: tamaños por función, mínimo de 12 px, alto de controles, campos de 16 px en el celular, sin scroll horizontal a 1440, 390 y 320 px).

### Cambiado
- `geneos-ui.css` ya no tiene tamaños de letra fijos: los 84 valores en px pasaron a tokens con el mismo valor en la escala compacta. Quedan fijos las iniciales del avatar grande (decorativas) y el campo de fecha a 16 px en el celular. Los textos de los gráficos SVG (ejes, centro del donut) también toman tokens.

### Corregido
- La tabla oculta que acompaña a cada gráfico (para lectores de pantalla) ensanchaba la página en pantallas de 320 px.

## [0.5.0] · 2026-11-05

Selectores de fecha, hora y fecha y hora para formularios de Django, con calendario accesible. Los cuatro productos no cambian: el HTML de sus pantallas es el mismo de la 0.4.0 y los scripts nuevos se cargan solo donde hay un selector.

### Agregado
- **Widgets** `geneos_ui.widgets.GnDateTimeInput`, `GnDateInput` y `GnTimeInput` (opciones `minute_step`, `default_time`, `invalid_message`, `picker_label`; `min` y `max` por `attrs`). Un único `<input>` por campo, sin campos ocultos: sin JavaScript es el control nativo (`datetime-local`, `date`, `time`) con valor ISO; con JavaScript pasa a texto con `dd/mm/aaaa HH:mm`, que es lo mismo que se envía. `value_from_datadict` acepta los dos formatos y le entrega ISO al campo, así que sirve con `DateTimeField`, `DateField` y `TimeField` sin tocar `input_formats`. Un texto inválido vuelve a mostrarse tal cual (`data-gn-raw`) con el error del campo.
- **`gn-popover`**: panel no modal (`role="dialog"`) que se ubica abajo o arriba según el espacio, no lo recortan contenedores con `overflow` y se abre abajo del campo si entra; si no, arriba (sin tapar la etiqueta); si no entra en ninguno de los dos lados, desplaza lo justo el contenedor con scroll del campo o se ubica al costado, siempre entero y con «Ahora» y «Listo» a la vista. Solo si la ventana es más baja que el panel usa scroll interno, con el pie fijo. Si un ancestro con `transform`/`filter`/`contain` lo recortaría, mientras está abierto se lleva al `<body>` (o al `<dialog>` abierto). Se recalcula al desplazar y al cambiar el tamaño de la ventana; en pantallas de hasta 480 px se muestra como hoja inferior compacta (semanas de 36 px, hora y acciones fijas abajo, áreas seguras del dispositivo). Escape lo cierra y devuelve el foco; también se cierra al tocar fuera o salir con Tab. Uso suelto con `data-gn-popover="id"` y `data-gn-popover-close`.
- **`gn-calendar`**: [Cally 0.9.2](https://github.com/WickyNilliams/cally) (MIT, `vendor/cally/`, sin modificar, hash verificado en los tests) estilizado con `::part()` y solo tokens; español de Argentina, semana desde el lunes, mes y año en el encabezado, `min`/`max`. Teclado: flechas, Inicio/Fin, RePág/AvPág (Mayús: año), Enter.
- **`gn-time`**: dos campos compactos `HH : mm` (`role="spinbutton"`, teclado numérico en el celular): se escribe directo (al completar la hora pasa solo a los minutos) o se ajusta con ↑/↓ (minutos de a `minute_step`, Mayús+↑/↓ de a 1), Inicio/Fin y flechas para mouse o touch fuera del orden de tabulación. Formato de 24 horas; un valor vacío o fuera de rango no se corrige solo: queda marcado con un mensaje vinculado por `aria-describedby` («La hora tiene que estar entre 00 y 23.»), el campo principal no cambia y «Listo» no cierra hasta corregirlo. Al desplazar la página el panel acompaña al campo y conserva su lado.
- `{% gn_datetime_js %}` para páginas sin `{{ form.media }}`. `GN.datetime` (`value`, `setValue`, `validate`, `parseDate`, `parseTime`, `parseDateTime`), `GN.popover` y `GN.initDateTime(root)`; `GN.init(root)` también inicializa los selectores agregados después.
- Validación en el navegador al salir del campo y al enviar: normaliza lo escrito (`5/11/26 9` → `05/11/2026 09:00`), marca `aria-invalid` y muestra el error vinculado con `aria-describedby`. Alt+↓ abre el panel desde el campo.
- Catálogo: sección «Fecha y hora» con ejemplos de cada producto, estados (rango, error del servidor, deshabilitado), calendario y panel sueltos. `tools/build_catalog.py` embebe también los módulos ES.
- Tests: `tests/test_datetime.py` (lectura de formatos, render, envío con y sin JS, zona horaria, media, Cally sin cambios, CSS sin colores fijos) y `tests/visual/test_datetime.py` (Chromium: sin JS, teclado, foco, Escape, arriba/abajo, celular, modo oscuro, validación).

### Cambiado
- `GN.version` y `__version__`: 0.5.0.
- Referencia de HTML: la sección «Fecha y hora», su entrada en el índice y los scripts del catálogo se registran como cambios intencionales en `tests/test_html_snapshots.py`.

## [0.4.0] · 2026-10-30

Componentes compartidos para las vistas de módulo, el menú y las preferencias, y una forma de llevar pantallas existentes al layout sin reescribir su CSS. GEMA, GEAGRO Cereales y GEAGRO Vid se ven igual que en la 0.3.0: mismo HTML y mismas capturas. GELECTRIC solo cambia en el panel de Preferencias, que suma el grupo «Color».

### Agregado
- **Lista de funcionalidades** `{% gn_link_list %}` (con `items=` o con `{% gn_link_item %}`): ícono, descripción, enlace y estado; dos columnas en escritorio y una en el celular; nombres completos en hasta dos líneas. Un ítem sin enlace se muestra como fila estática con su estado, no como un enlace vacío.
- **Encabezado de pantalla** `{% gn_page_head %}` con el ícono original del módulo, y `{% gn_any_icon %}` para usar `i-*`, `producto:módulo` o una ruta de estáticos. Un ícono pendiente en el manifiesto no se muestra ni se reemplaza por otro.
- **Variantes de color elegidas por el usuario**: `VARIANTS` y `VARIANT_LEGACY`. GELECTRIC: verde por defecto y azul a elección; la elección hecha con el selector anterior (`geletric-brand-color`) se migra una vez. Se guarda en `gn-variant:<producto>`. `GN.setVariant`, `GN.getVariant` y el evento `gn:variant`.
- **Pie del menú y menú del usuario**: `NAV_FOOTER`, `USER_MENU` y `LOGOUT_URL` (formulario POST con CSRF). Un ítem sin URL o con `"#"` no se muestra; «Ayuda y soporte» aparece solo cuando el producto le da un destino.
- **Accesos directos en el buscador del menú**: `NavItem(search_links=[NavLink(…)])`, con permisos. `url` acepta también `mailto:` y `tel:`.
- **CSS existente del producto**: `LEGACY_CSS` (capa `legacy`, después de la biblioteca) y el bloque `content_attrs` con `data-gn-legacy` (panel claro en modo oscuro) o `data-gn-legacy="dark"` (CSS puente del producto). Tokens `--gn-legacy-light-bg` y `--gn-legacy-light-text`.
- `SIDEBAR_ICONS = "tint"`: los íconos propios del sidebar toman los colores del sidebar en reposo, hover y activo.
- Chequeos E006 (`SIDEBAR_ICONS`) y W004 (`LEGACY_CSS`); W003 cubre también `link_list.html` y `page_head.html`.
- Catálogo: sección «Vista de módulo» al final, por producto.
- GEFLOTA (solo sandbox) usa todo lo anterior sin cambios en `geneos_ui/`.

### Cambiado
- HTML: con `VARIANTS`, `gn_theme_boot` agrega un `<script>` que aplica la variante guardada antes de pintar y `gn_prefs` agrega el grupo «Color». Solo afecta a GELECTRIC entre los cuatro productos. Referencia de HTML regenerada sobre la 0.3.0 (`tests/snapshots/0.3.0`).
- Única captura distinta de la 0.3.0: `gelectric-preferencias.png` (grupo «Color»), registrada en `tests/visual/cambios-esperados.txt`. CI compara contra `v0.3.0`.

### Quitado
- `geneos_ui.conf.PRODUCTS`, `SIDEBAR_DEFAULTS`, `NAV_LAYOUT_DEFAULTS` y `geneos_ui.product_icons.HNAV_VARIANTS`, `HNAV_TINT`, deprecados en la 0.3.0. Reemplazo: `geneos_ui.presets.PRESETS`, `get_config()` y `GENEOS_UI["NAV_ICONS"]`. Ningún producto los usa.

## [0.3.0] · 2026-10-29

Un producto nuevo se incorpora desde su propio `settings.py`, sin cambiar la biblioteca. Los cuatro productos actuales se ven y se comportan igual que en la 0.2.1: mismo HTML (salvo lo indicado abajo) y capturas idénticas en claro y oscuro, menú horizontal y vertical, desplegables, preferencias y celular.

### Agregado
- `geneos_ui/presets.py`: GELECTRIC, GEMA, GEAGRO Cereales y GEAGRO Vid como presets. La configuración se arma en capas: valores por defecto < preset < `GENEOS_UI`.
- Claves nuevas de `GENEOS_UI`: `THEME_CSS`, `FONT_CSS`, `NAV_ICONS`, `BOOTSTRAP_RGB`, `SIDEBAR_LEGACY_KEY`, `ICON_FAMILY`, `ICON_MANIFEST` y `STATIC_VERSION_QUERY`.
- `NavItem(icon_static_h=…, icon_static_h_active=…)`: variante clara propia de un ícono para la barra horizontal; con `NAV_ICONS = "tint"` alcanza el SVG blanco.
- Chequeos E003 (sin preset ni tema), E004 (tema inexistente), E005 (`NAV_ICONS`), W002 (logos) y W003 (template de componente sobrescrito por el producto).
- `?v=<versión>` en el CSS y el JS de la biblioteca, y `nonce` de CSP en los `<script>` y `<style>` en línea.
- Catálogo: cada sección dice si es «Componente», «HTML de referencia» o «Ejemplo».
- GEFLOTA, producto ficticio de pruebas, solo en el sandbox (`sandbox/geflota`, `settings_geflota.py`).
- Documentación: `docs/api.md` (API pública), `docs/versionado.md` y `docs/nuevo-producto.md`.
- Pruebas: HTML de referencia de la 0.2.1 (`tests/snapshots/`), capturas comparadas (`tests/visual/`), pruebas en el navegador, producto nuevo, chequeos, presets y ningún producto escrito en el código de la biblioteca. CI con Python 3.10 a 3.13 y Django 5.2, Django 6.1 informativo, instalación limpia del wheel y capturas contra `v0.2.1`.

### Cambiado
- `PRODUCT` acepta cualquier identificador; E001 controla solo el formato.
- Requiere Django 5.2 LTS (`>=5.2,<6.0`). Django 5.0 y 5.1 ya no reciben parches de seguridad.
- Los tripletes `--bs-*-rgb` del puente Bootstrap ya no están en `bridges/bootstrap5.css`: los escribe `gn_css` desde `BOOTSTRAP_RGB` (mismos valores), con `:root[data-gn-product]` para ganarle a Bootstrap en cualquier orden. HTML: un `<style>` después del puente.
- La migración de la clave vieja del sidebar de GELECTRIC pasó del JS a la configuración. HTML: atributo `data-gn-legacy-key` en el sidebar de GELECTRIC.
- Menú: si varias rutas coinciden, queda activa la más específica. No cambia nada en los cuatro productos, cuyo inicio es `/`.
- Solapa de preferencias: 22 px de ancho en escritorio (antes 30) para entrar en el margen de 24 px del contenido sin tapar ningún control; 44 px de alto (WCAG 2.5.8). En el celular sigue de 30 px; el contenido deja lugar al final de la página y el foco del teclado no queda debajo de la solapa (WCAG 2.4.11). Únicas capturas distintas de la 0.2.1: las dos con el panel abierto, que se corre 8 px.

### Deprecado
- `geneos_ui.conf.PRODUCTS`, `SIDEBAR_DEFAULTS`, `NAV_LAYOUT_DEFAULTS` y `geneos_ui.product_icons.HNAV_VARIANTS`, `HNAV_TINT`. Siguen funcionando con aviso; se quitan en la 0.4.0.

## [0.2.1] · 2026-10-28

### Cambiado · menú horizontal unificado
- Los cuatro productos usan la estructura del menú superior de GEMA: barra blanca en modo claro y oscura en modo oscuro, flotando sobre una franja del color institucional (GEMA azul, GELECTRIC verde, GEAGRO Cereales verde oscuro, GEAGRO Vid violeta). Esquinas de 8 px, sombra suave, márgenes laterales de 24 px, alto de 76 px, ícono arriba y texto en una línea (con «…» y tooltip si no entra).
- Todo se define en los tokens compartidos (`tokens.css`); los temas aportan solo sus colores. La franja es configurable (`--gn-hnav-band`, `--gn-hnav-band-h`) y los indicadores del activo usan `--gn-hnav-accent` (por defecto el color de marca en claro y el de acento en oscuro). GEMA no necesita tokens propios.
- GEAGRO Cereales: en modo claro la línea del activo usa el dorado oscuro de la marca (5,1:1 sobre blanco); el amarillo #c6a400 daba 2,4:1. En modo oscuro sigue el amarillo #f3c600.
- Íconos sobre fondo claro, siempre originales: GEMA con sus SVG normal y `-active`; GELECTRIC con sus íconos de color de los módulos (`product_icons.HNAV_VARIANTS`); GEAGRO, que solo tiene completos los SVG blancos, con ese mismo archivo como máscara pintada con `--gn-hnav-icon-tint` / `--gn-hnav-icon-tint-active` (`product_icons.HNAV_TINT`).
- Contraste medido: texto activo ≥ 5,1:1 y línea del activo ≥ 3,1:1 en los ocho casos (cuatro productos, claro y oscuro).
- `tools/build_catalog.py` incrusta también los íconos usados como máscara.

### Agregado · preferencias de interfaz
- Solapa flotante en el borde izquierdo (`{% gn_prefs %}`, incluida en `layouts/app.html` en `{% block prefs %}`) que abre un panel compacto con **Apariencia** (Claro / Oscuro) y **Navegación en escritorio** (Horizontal / Vertical). Reutiliza `{% gn_theme_switch %}` y `{% gn_nav_switch %}` con su misma lógica y persistencia; los cambios se aplican sin recargar.
- Se cierra con la X, Esc o un clic afuera; el foco vuelve a la solapa. Es `position: fixed`: no desplaza el contenido ni cambia su ancho. API: `GN.prefs.open()` / `GN.prefs.close()`.
- Con menú vertical la solapa se apoya en el borde del sidebar (expandido o contraído) y nunca lo tapa. En celulares baja cerca del borde inferior, queda debajo del menú lateral abierto y muestra solo la apariencia.
- Los selectores de tema y navegación salen del encabezado del catálogo.
- El ícono `i-gear` se redibujó como engranaje con dientes: el anterior se confundía con `i-sun`.

## [0.2.0] · 2026-10-28

### Navegación horizontal: ajustes finales
- La barra horizontal queda siempre en una fila. Los módulos que no entran pasan al menú «Más», agrupados por módulo y con el estado activo; se recalcula al cambiar el tamaño de la ventana, la disposición o el producto. En GELECTRIC aparece desde 1024 px (Sueldos, Integraciones y Técnico).
- Módulo activo más claro en GELECTRIC y GEAGRO: fondo del ítem activo del sidebar, texto en negrita y línea inferior del color de acento. GEMA conserva su estilo (solo texto y línea naranja).
- Altura uniforme: todos los ítems miden lo mismo, con el ícono arriba, el texto en hasta dos líneas y la línea del activo alineada abajo.
- Los desplegables se alinean a la derecha si no entran en la ventana y limitan su alto con desplazamiento interno.
- Barra alineada con el ancho del contenido en pantallas grandes. Los badges van a la derecha del ícono.
- Encabezado entre 861 y 1279 px: los selectores de tema y navegación muestran solo el ícono y, con selectores de contexto (GEAGRO), el chip de usuario muestra solo el avatar, para que nada se superponga.
- Fenología e Informes (GEAGRO Vid) siguen pendientes: no hay íconos originales en ninguna rama ni en el historial de `geneos-geagro`.
- Probado en 1024, 1280, 1440 y 1920 px; en pantallas de hasta 860 px sigue el menú lateral desplegable.


### Agregado · disposición del menú
- Segunda preferencia de visualización, con la misma lógica que el modo claro/oscuro: navegación **horizontal** o **vertical** (`data-gn-nav`, `localStorage["gn-nav"]`, `{% gn_nav_boot %}`, `{% gn_nav_switch %}`, `GN.setNav()` / `GN.getNav()`, evento `gn:nav`). Cambia sin recargar y es independiente del tema y del producto.
- Valor por producto (`GENEOS_UI["NAV_LAYOUT"]`): GEMA horizontal; GELECTRIC, GEAGRO Cereales y GEAGRO Vid vertical.
- Un solo menú para las dos disposiciones: el mismo `gn-sidebar` se reacomoda como barra horizontal. Submenús como desplegables (uno por vez, Esc, clic afuera, flechas izquierda/derecha).
- GEMA en horizontal conserva su menú superior: barra blanca flotante sobre la franja azul, ícono arriba del texto, SVG normal y `-active` originales y línea naranja bajo el ítem activo. GELECTRIC y GEAGRO usan en horizontal una barra con el color de su sidebar y sus mismos íconos blancos.
- `LOGO_TOPBAR`: logo original para fondo claro en el encabezado con menú horizontal (en modo oscuro se usa el logo blanco del sidebar). Copias verificadas en `sandbox/static/demo/logos/*-topbar.svg`.
- En pantallas chicas se usa siempre el menú lateral desplegable.

### Cambiado · contenido por producto y GEAGRO portal/backoffice
- Los ejemplos del catálogo (tipografía, navegación, botones, formularios, filtros, tablas, indicadores, estados, modales, notificaciones y comparación) usan los datos y procesos de cada sistema: GELECTRIC (asociados, suministros, reclamos, cuota capital), GEMA (clientes, matafuegos, recargas, pruebas hidráulicas, vencimientos), GEAGRO Cereales (campaña, lotes, cultivos, labores, alertas) y GEAGRO Vid (cuarteles, fenología, alertas sanitarias, labores). El contenido vive en `geneos_ui/catalog_examples.py`.
- El sidebar de GEAGRO es solo el del portal del productor, igual al de `templates/partials/sidebar.html`. Operaciones, Acopio, Ventas, Productores, Parámetros, Usuarios y Monitoreo de cultivo son del backoffice (Jazzmin) y se muestran aparte, como referencia, con sus propios íconos.
- GEAGRO Vid usa «Campaña» y «Lote», como el sistema.
- El menú de GEAGRO dice «Alertas y avisos».
- Sidebar: los nombres que no entran y se cortan con «…» muestran el nombre completo en un tooltip también con el sidebar expandido.
- `docs/pendientes.md`: Historial de GEAGRO (sin URL ni navegación) y los íconos definitivos que faltan (Fenología, Informes, Monitoreo de cultivo).
- Iconografía: filtro por conjunto (portal, backoffice, línea VID, PNG…) y fondo de vista previa claro, oscuro o del producto.
- Sección propia «Íconos de acciones comunes»: el set original de 47 íconos de GELECTRIC (marcando los que solo usa GELECTRIC) y las 14 acciones agregadas.
- Tests: términos de un producto no aparecen en otro; el menú del portal coincide con el real; el backoffice usa solo íconos del backoffice.

### Agregado · iconografía original
- 119 archivos de íconos originales (SVG y PNG) de GELECTRIC, GEMA y GEAGRO, copiados byte a byte desde las ramas de trabajo con su nombre original, en `static/geneos_ui/icons/<producto>/activos|disponibles/`.
- Manifiesto `geneos_ui/product_icons.json` con producto, módulo, variante, formato, ruta y commit de origen, SHA-256 y estado de uso (activo, disponible, pendiente). Lo genera `tools/import_product_icons.py`, que también verifica la copia contra los originales (`--check`).
- `NavItem(icon="producto:módulo")` y `{% gn_product_icon %}`. Los ítems sin ícono propio (Fenología, Informes y Monitoreo de cultivo en Vid) se muestran con un marcador de pendiente.
- Sección «Iconografía por producto» en el catálogo, con filtros por producto, módulo y estado.

### Cambiado
- El sidebar, los indicadores y la comparación del catálogo usan los íconos originales de cada producto.
- Se quitaron del sprite 14 íconos dibujados para el catálogo que representaban módulos (matafuego, uva, silo, camión, etc.). El sprite queda para acciones comunes.

### Corregido
- El catálogo de GitHub Pages abría en azul oscuro y el selector no pasaba a modo claro: el build agregaba un `@media (prefers-color-scheme: dark)` que mantenía el modo oscuro. Se quitó; el modo ya no depende del sistema operativo.

### Cambiado
- Modo claro por defecto (fondo `#FFFFFF`, superficies gris claro, texto oscuro). Modo oscuro negro: fondo `#090909`, superficies `#171717` y `#242424`.
- Nuevos tokens `--gn-elevated`, `--gn-field`, `--gn-disabled-bg`, `--gn-disabled-text` y `--gn-critical-strong`.
- Tintes de marca y de estado recalculados para que texto, hover, activo, badges y alertas superen 4,5:1 en los dos modos y en los cuatro productos (excepto el blanco sobre naranja de GEMA, aceptado por identidad).

### Agregado
- `GN.setTheme("light" | "dark")`, `GN.getTheme()` y evento `gn:theme`. La elección se guarda en `localStorage` (`gn-theme`); sin preferencia guardada arranca en claro.
- Template tags `{% gn_theme_boot %}` (en el `<head>`, evita el destello) y `{% gn_theme_switch %}` (selector Claro / Oscuro accesible con teclado).

## [0.1.0] · 2026-10-26 · borrador para aprobación

### Agregado
- Tokens base (`tokens.css`) con neutros, tipografía Titillium Web, espaciado de 4 px, radios y sombras de GELECTRIC, colores derivados por `color-mix()` y modo oscuro opcional.
- Temas de GELECTRIC (verde por defecto, variante azul), GEMA (azul y naranja), GEAGRO Cereales (verde y amarillo) y GEAGRO Vid (violeta y verde), con colores tomados de cada repositorio.
- Componentes `gn-*` en `@layer geneos-ui`: sidebar con submenús y buscador, encabezado, breadcrumbs, pestañas, menús desplegables, botones, formularios, buscadores, filtros combinados, tablas responsive con acordeón y orden, paginación, tarjetas, indicadores, gráficos de línea y dona, badges, alertas, notificaciones, modales, tooltips, acordeones, pasos, vacío y carga.
- `geneos-ui.js` sin dependencias.
- Navegación declarativa (`NavItem`, `NavSection`) con permisos, ítem activo e índice de búsqueda.
- Template tags, layouts de aplicación y login, catálogo `/ui-kit/` y `tools/build_catalog.py`.
- Puentes opcionales para Bootstrap 5 (Lexa) y Jazzmin.
