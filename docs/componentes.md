# Componentes de GENEOS UI

Referencia rápida de markup. El catálogo (`/ui-kit/` o `dist/ui-kit.html`) muestra cada uno funcionando con los cuatro temas.

## Tokens

| Token | Uso |
| --- | --- |
| `--gn-c-*` | Colores de identidad que define cada tema. No usarlos en componentes. |
| `--gn-brand`, `--gn-brand-hover`, `--gn-brand-press`, `--gn-on-brand` | Acción principal. |
| `--gn-brand-ink` | Texto y bordes con color de marca sobre fondo claro (contraste ≥ 4,5:1). |
| `--gn-brand-soft`, `--gn-brand-soft-2` | Fondos tenues de marca (hover de secundarios, íconos). |
| `--gn-accent` | Indicador de activo: barra del sidebar, pestaña seleccionada. |
| `--gn-good` / `-soft` / `-ink` (y `warning`, `critical`, `info`) | Estados. `-ink` es la versión legible para texto. |
| `--gn-bg`, `--gn-surface`, `--gn-surface-2`, `--gn-border`, `--gn-text`, `--gn-text-2`, `--gn-text-muted` | Neutros compartidos. |
| `--gn-space-1…10`, `--gn-radius*`, `--gn-fs-*` | Espaciado, radios y tipografía. |

Personalizar: redefinir cualquier `--gn-*` en el CSS del producto, después de `{% gn_css %}`.

## Navegación

**Sidebar**: `{% gn_sidebar %}` (lo incluye `layouts/app.html`). Atributos que usa el JS: `data-gn-sidebar`, `data-gn-group-toggle`, `data-gn-sidebar-toggle` (botón de menú), `data-gn-scrim`, `data-gn-keywords` (sinónimos para el buscador).

**Breadcrumbs**: `{% gn_breadcrumbs crumbs %}`.

**Pie del menú y menú del usuario**: `GENEOS_UI["NAV_FOOTER"]`, `["USER_MENU"]` y `["LOGOUT_URL"]`. Un ítem sin destino real no se muestra.

## Vista de módulo

**Encabezado**: `{% gn_page_head title=modulo.nombre subtitle="10 funcionalidades" eyebrow="Módulo" icon="gelectric:contabilidad" %}<a class="gn-btn gn-btn--secondary" href="/">Volver</a>{% endgn_page_head %}`. El ícono es el original del módulo (`producto:módulo`, ruta de estáticos o `i-*`); si no hay ícono, no se reserva lugar.

**Lista de funcionalidades**: el mismo componente para todos los módulos.
```django
{% gn_link_list items=funcionalidades columns=2 empty_status="En definición" %}

{% gn_link_list %}
  {% gn_link_item label="Ficha del asociado" href=url_ficha description="Consulta y edición" icon="i-id-card" %}
  {% gn_link_item label="Reintegro al darse de baja" status="Próximamente" status_kind="neutral" %}
{% endgn_link_list %}
```
Un ítem con `href` es un enlace; sin `href` es una fila estática con su estado (`empty_status` por defecto). Dos columnas en escritorio y una en el celular (≤ 860 px); el nombre ocupa hasta dos líneas y completo queda en `title`.

**Pestañas**
```html
<div class="gn-tabs" role="tablist" aria-label="Ficha">
  <button class="gn-tabs__tab" role="tab" aria-controls="p1" aria-selected="true">Datos</button>
  <button class="gn-tabs__tab" role="tab" aria-controls="p2" aria-selected="false">Historial</button>
</div>
<div class="gn-tab-panel" role="tabpanel" id="p1">…</div>
<div class="gn-tab-panel" role="tabpanel" id="p2" hidden>…</div>
```

**Menú desplegable / menú de acciones**
```html
<div class="gn-dropdown">
  <button class="gn-btn gn-btn--ghost gn-btn--icon" data-gn-dropdown="m1" aria-label="Más acciones">{% gn_icon "i-more" %}</button>
  <div class="gn-dropdown__menu" id="m1" role="menu" hidden>
    <button class="gn-dropdown__item" role="menuitem">{% gn_icon "i-edit" %}Editar</button>
    <div class="gn-dropdown__sep" role="separator"></div>
    <button class="gn-dropdown__item gn-dropdown__item--danger" role="menuitem">{% gn_icon "i-trash" %}Eliminar</button>
  </div>
</div>
```

## Botones

`gn-btn` + una variante: `--primary`, `--secondary`, `--tertiary`, `--ghost`, `--danger` (`--solid` para confirmaciones), `--success`, `--warning`, `--info`. Modificadores: `--sm`, `--lg`, `--icon`, `--block`. Estados: `disabled`, `aria-disabled="true"`, `.is-loading` (o `GN.setLoading(btn, true, "Guardando…")`).

## Formularios y filtros

```html
<div class="gn-field">
  <label class="gn-field__label" for="serie">Número de serie<span class="gn-required" aria-hidden="true">*</span></label>
  <input class="gn-input" id="serie" aria-invalid="true" aria-describedby="serie-e" required>
  <span class="gn-field__error" id="serie-e">{% gn_icon "i-alert" %}Ya existe en otro cliente.</span>
</div>
```
Controles: `gn-input`, `gn-select`, `gn-textarea`, `gn-check` (checkbox y radio), `gn-switch`, `gn-search`, `gn-input-group`. Grillas: `gn-form-grid`, `gn-form-grid--3`, `gn-field--full`.

Filtros combinados: `gn-filters` con `gn-pills` (filtro rápido), `gn-filters__panel` (colapsable en móvil con `data-gn-filters-toggle`), `gn-filter` por campo y el constructor "+ Agregar filtro" (`data-gn-filter-builder="id-del-json"`, mismo formato de datos que GELECTRIC). Nada se envía hasta presionar Filtrar.

## Fecha y hora (0.5.0)

```python
from geneos_ui.widgets import GnDateInput, GnDateTimeInput, GnTimeInput

class TurnoForm(forms.Form):
    inicio = forms.DateTimeField(
        widget=GnDateTimeInput(default_time="09:00", minute_step=5, attrs={"min": "2026-01-01T00:00"}),
        error_messages={"invalid": "Ingresá una fecha y hora válidas"},
    )
    dia = forms.DateField(widget=GnDateInput())
    hora = forms.TimeField(widget=GnTimeInput(minute_step=15))
```
En el template: `{{ form.media }}` (o `{% gn_datetime_js %}` si el formulario no se arma con Django) y el campo dentro de `gn-field` como cualquier otro.

- **Un solo input**, con el `name` del campo. Sin JavaScript es nativo y envía ISO; con JavaScript se ve y se envía `dd/mm/aaaa HH:mm` (`dd/mm/aaaa`, `HH:mm`). El widget convierte a ISO antes de que valide el campo.
- **Botón** a la derecha del campo (`aria-haspopup="dialog"`, `aria-expanded`, `aria-controls`) que abre el panel. **Alt+↓** también lo abre desde el campo.
- **Panel** (`gn-popover`): junto al campo, en este orden: abajo si entra; arriba (sin tapar la etiqueta); desplazando lo justo el contenedor con scroll; al costado o dentro de la ventana, siempre entero y con «Ahora»/«Listo» visibles. Scroll interno solo si la ventana es más baja que el panel, con el pie fijo. No lo recortan contenedores con `overflow` (si un ancestro con `transform` lo atraparía, se lleva al `<body>` mientras está abierto); en el celular, hoja inferior compacta con la hora y las acciones fijas abajo. Calendario (`gn-calendar`), hora y minutos (`gn-time`: dos campos `HH : mm` de 24 horas que se escriben directo o se ajustan con ↑/↓, Inicio/Fin; un valor vacío o fuera de rango se marca con un mensaje y no se corrige solo), «Ahora»/«Hoy» y «Listo». En fecha sola, elegir un día cierra el panel. Escape cierra y devuelve el foco al botón; tocar fuera o salir con Tab también cierra.
- **Validación en el navegador**: al salir del campo y al enviar. Lo escrito se normaliza; si no es válido o queda fuera de `min`/`max`, se marca `aria-invalid` y se muestra el error debajo, vinculado con `aria-describedby`. El servidor valida igual (y es quien decide).
- **Opciones**: `minute_step` (paso de la lista de minutos; a mano se puede escribir cualquiera), `default_time` (hora que se completa al elegir solo el día), `invalid_message`, `picker_label` (nombre del botón y del panel, p. ej. «Elegir fecha de finalización»).
- **JavaScript**: `GN.datetime.value(input)` devuelve ISO (`""` vacío, `null` inválido) y `GN.datetime.setValue(input, iso)` lo cambia y dispara `input` y `change`. Útil para reglas entre campos (fin posterior al inicio).

Sueltos:
```html
<calendar-date data-gn-calendar locale="es-AR" first-day-of-week="1" value="2026-11-05" aria-label="Vencimientos del mes"></calendar-date>

<button type="button" class="gn-btn gn-btn--secondary" data-gn-popover="ayuda">Ver detalle</button>
<div class="gn-popover" id="ayuda" role="dialog" aria-label="Detalle" hidden>
  …<button type="button" class="gn-btn gn-btn--primary gn-btn--sm" data-gn-popover-close>Entendido</button>
</div>
```
El calendario es [Cally 0.9.2](https://github.com/WickyNilliams/cally) (MIT) en `static/geneos_ui/vendor/cally/`, sin modificar; se carga como módulo y se estiliza con `::part()` y tokens. Si no carga, los campos de fecha quedan nativos. El rango de fechas (`gn-date-range-picker`) y la migración del filtro `daterange` quedan para la 0.6.0.

## Tablas

```html
<div class="gn-table-wrap">
  <table class="gn-table gn-table--responsive">
    <thead><tr><th scope="col">Cliente</th>{% gn_sort_th "Saldo" "saldo" "o" "is-num" %}</tr></thead>
    <tbody><tr>{% gn_cell "Cliente" %}…{% endgn_cell %}{% gn_cell "Saldo" "is-num" %}…{% endgn_cell %}</tr></tbody>
  </table>
</div>
{% gn_pagination page_obj %}
```
`--responsive`: en móvil cada fila es una tarjeta con la etiqueta de cada columna. `--accordion`: además, la fila se abre y cierra; requiere una primera celda `td.gn-row-summary` con un `button.gn-row-summary__btn`. Orden en el navegador para tablas chicas: `data-gn-sort="client"`.

## Tarjetas, indicadores y gráficos

`gn-card` (`__head`, `__body`, `__foot`, `--link`), `gn-kpi`, `gn-grid--2/3/4/main-aside`, `gn-list`, `gn-dl`, `gn-bars`.

Gráficos sin librerías: `<div class="gn-chart" data-gn-chart="line" data-gn-source="id-json" data-gn-unit="MWh" data-gn-title="…">` y `data-gn-chart="donut"`. Los datos van en `{{ datos|json_script:"id-json" }}` como `[{"label": "May", "value": 2580}]`. Cada gráfico incluye una tabla oculta para lectores de pantalla.

## Estados e interacción

- **Badges**: `gn-badge gn-badge--good|warning|critical|info|neutral|brand|solid`, `--dot`. Tag: `{% gn_badge "Vencido" "critical" True %}`.
- **Alertas**: `gn-alert gn-alert--good|warning|critical|info`, cierre con `data-gn-dismiss`.
- **Notificaciones**: `GN.toast("Mensaje", {kind: "good", title: "…"})`. Los `messages` de Django se muestran solos (`{% gn_messages_json %}` en el layout).
- **Modales**: `<dialog class="gn-modal" id="x">` + botón `data-gn-modal-open="x"`; cierre con `data-gn-modal-close`, `Esc` o clic en el fondo.
- **Tooltips**: `data-gn-tooltip="Texto"`.
- **Acordeones**: `<div class="gn-accordion"><details><summary>…</summary><div class="gn-accordion__body">…</div></details></div>`.
- **Pasos**: `<ol class="gn-steps">` con `li.is-done` / `li.is-current`.
- **Vacío y carga**: `gn-empty`, `gn-skeleton`.

## Accesibilidad

- Foco visible en todos los controles (`--gn-focus`).
- Sidebar: `aria-current`, `aria-expanded`, `/` para buscar, flechas para recorrer, `Esc` cierra el cajón móvil, foco atrapado en el cajón.
- Dropdowns: `aria-expanded`, flechas, `Home`/`End`, `Esc` devuelve el foco.
- Pestañas: patrón WAI-ARIA con flechas.
- Fecha y hora: botón con `aria-haspopup="dialog"` y `aria-expanded`; panel `role="dialog"` con nombre; grilla de Cally con días como botones (`aria-pressed`, `aria-current="date"`, nombre completo «13 de noviembre») y el mes anunciado en `aria-live`; formato del campo anunciado por `aria-describedby`; `Esc` devuelve el foco al botón. Verificado con Chromium en `tests/visual/test_datetime.py`.
- Mensajes dinámicos anunciados con `aria-live` (`GN.announce()`).
- Se respeta `prefers-reduced-motion`.
