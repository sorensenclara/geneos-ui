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
- Mensajes dinámicos anunciados con `aria-live` (`GN.announce()`).
- Se respeta `prefers-reduced-motion`.
