# Gráficos Chart.js opcionales

GENEOS UI mantiene los gráficos SVG existentes (`data-gn-chart="line"` y `"donut"`) sin dependencias. Para gráficos interactivos avanzados se puede habilitar Chart.js 4 **sólo en las páginas que lo necesiten**.

## Instalación y carga centralizada

GENEOS UI incluye Chart.js **4.5.1** en sus propios archivos estáticos (licencia MIT). No hay que instalar Chart.js, agregar CDN ni copiar archivos en GECLUB, GERP, GEMA u otros productos.

Con el tag habitual `{% gn_js %}`, GENEOS UI carga el adaptador automáticamente. Si la pantalla contiene un elemento con `data-gn-engine="chartjs"`, el adaptador solicita **bajo demanda** el Chart.js local desde `geneos_ui/vendor/chartjs/chart.umd.min.js`. Las pantallas sin gráficos no descargan el archivo pesado.

El repositorio mantiene un workflow reproducible en `.github/workflows/vendor-chartjs.yml` para incorporar el archivo UMD de la versión fijada junto con su licencia. La publicación del paquete debe incluir el archivo generado.

```django
{% load geneos_ui %}
{% gn_js %}
```

No uses `{% gn_chartjs_js %}` además de `{% gn_js %}`: el tag habitual ya lo incluye. El tag específico queda disponible para integraciones personalizadas que no utilicen el tag general.

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
