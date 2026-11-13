# Gráficos Chart.js opcionales

GENEOS UI mantiene los gráficos SVG existentes (`data-gn-chart="line"` y `"donut"`) sin dependencias. Para gráficos interactivos avanzados se puede habilitar Chart.js 4 **sólo en las páginas que lo necesiten**.

## Dependencia

El proyecto consumidor debe cargar Chart.js **4.x** antes del adaptador. En entornos productivos se recomienda alojar el archivo JS en los estáticos del propio proyecto o de un proveedor confiable, con una versión fijada y una política CSP adecuada.

```django
{% load geneos_ui %}
{# Al final de la página o en el bloque de scripts del layout: #}
<script src="{% static 'vendor/chartjs/chart.umd.min.js' %}" defer></script>
{% gn_js %}
{% gn_chartjs_js %}
```

El ejemplo presupone que se cargó `{% load static %}` y que existe ese archivo Chart.js en el proyecto consumidor. El tag `gn_chartjs_js` **sólo** incluye el adaptador; no descarga ni incorpora Chart.js.

## Ejemplo Django

```django
{{ ventas|json_script:"datos-ventas" }}
<div class="gn-chart"
     data-gn-chart="bar"
     data-gn-engine="chartjs"
     data-gn-source="datos-ventas"
     data-gn-title="Ventas mensuales"
     data-gn-unit="$"></div>
```

Ejemplo de `ventas`:
```json
[{"label":"Enero","value":120},{"label":"Febrero","value":155}]
```

Tipos admitidos: `line`, `bar`, `pie`, `donut` (alias de `doughnut`) y `doughnut`. Usan la misma estructura `[{label, value}]` que los SVG clásicos. El adaptador toma sus colores de `--gn-chart-1` a `--gn-chart-5`, así como tipografía, ejes y grilla de los tokens activos. El atributo `data-gn-unit` agrega una unidad a los tooltips.

Cada gráfico incorpora una tabla accesible oculta para lectores de pantalla. Se admiten colores particulares por segmento con `{"label":"A","value":20,"color":"#123456"}` en gráficos circulares; enviar valores de color solamente desde configuraciones confiables.

## API JavaScript

- `GN.renderCharts(contenedor)`: actualiza los SVG y, si el adaptador está presente, Chart.js.
- `GN.renderChartJS(contenedor)`: dibuja o actualiza sólo los Chart.js.
- `GN.destroyChartJS(contenedor)`: libera los gráficos Chart.js de un contenedor antes de eliminarlo.

Para contenido insertado después de cargar la página: `GN.init(contenedor)` o `GN.renderCharts(contenedor)`. Para cambiar de tema, invocar `GN.renderChartJS(document)` después de aplicar los nuevos tokens si se desea actualizar sus colores.

Sin Chart.js o sin el adaptador, GENEOS UI continúa funcionando y los SVG siguen visibles. Ninguna pantalla existente pasa a Chart.js automáticamente.
