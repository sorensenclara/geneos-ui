# Pendientes

Funcionalidades y recursos que existen en los productos o que se necesitan, pero que todavía no se incorporan a GENEOS UI. Relevado sobre las ramas de trabajo (`2026`, `2026-cereales`, `2026-vid`); los repositorios de los productos no se modificaron.

## Funcionalidades

| Producto | Funcionalidad | Situación | Decisión |
| --- | --- | --- | --- |
| GEAGRO Cereales y Vid | Historial (portal del productor) | Existe el template `agro_system/templates/pages/historial.html`, pero ninguna URL lo sirve y no figura en `templates/partials/sidebar.html`. | No se agrega al sidebar hasta que tenga URL y navegación activa (27/10/2026). |

## Íconos originales

| Producto | Ítem | Interfaz | Hoy en el producto | En GENEOS UI | Qué falta |
| --- | --- | --- | --- | --- | --- |
| GEAGRO Vid | Fenología | Portal del productor | `mdi mdi-sprout-outline` | Marcador pendiente | Ícono original definitivo, versión blanca para el sidebar. |
| GEAGRO Vid | Informes | Portal del productor | `mdi mdi-chart-bar` | Marcador pendiente | Ícono original definitivo en SVG blanco o monocromático. El PNG a color «GEAGRO - Icon Gráficos» queda como recurso disponible y no se usa en el sidebar. |
| GEAGRO Vid | Monitoreo de cultivo | Backoffice (Jazzmin, app `crop_monitoring`) | Sin ícono asignado en `JAZZMIN_SETTINGS["icons"]` | Marcador pendiente en la referencia del backoffice | Ícono original definitivo. |

Los pendientes de íconos están registrados en `geneos_ui/product_icons.json` con estado `pendiente` y sin archivo. Cuando lleguen los archivos definitivos, se agregan a la rama del producto y se vuelve a ejecutar `tools/import_product_icons.py`.
