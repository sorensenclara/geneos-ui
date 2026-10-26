# Integración en los productos

**No empezar hasta que se apruebe el UI Kit.** Todo el trabajo va en las ramas de trabajo, nunca en las ramas originales ni en producción.

| Producto | Repositorio | Rama de trabajo | Commit de origen |
| --- | --- | --- | --- |
| GELECTRIC | sorensenclara/geletric-django | `2026` | `3772f02` (`main`) |
| GEMA | sorensenclara/GEMA | `2026` | `4ff87ef` (`feature/diseno-ui`) |
| GEAGRO Cereales | sorensenclara/geneos-geagro | `2026-cereales` | `25fdfa8` (`dev_agro`) |
| GEAGRO Vid | sorensenclara/geneos-geagro | `2026-vid` | `bd5da7d` (`vid_alert`) |

## Pasos comunes

1. Agregar `geneos-ui` con versión fija a `requirements.txt`, `geneos_ui` a `INSTALLED_APPS`, el context processor y `GENEOS_UI`.
2. Cargar `{% gn_css %}` en el layout actual, sin tocar markup. Las pantallas no cambian, salvo donde un puente unifique color.
3. Migrar de a un componente (badges, alertas, botones, después tablas y filtros), con captura antes y después de cada pantalla.
4. Pasar el layout a `geneos_ui/layouts/app.html` con el menú declarado en `navigation.py`.
5. Revisión en staging; merge solo con aprobación.

## Por producto

**GELECTRIC**: es el origen. `core/modules_data.py` pasa a `NavItem` con submenús (hoy los ítems solo aparecen en el buscador). `base.html` extiende el layout del paquete. El selector azul/verde queda como `VARIANT`; el verde es el valor por defecto. El sidebar arranca contraído, como hoy (valor por defecto de GELECTRIC); `GENEOS_UI["SIDEBAR_DEFAULT"]` lo cambia si hiciera falta.

**GEMA**: el menú horizontal de `core/base.html` se reemplaza por el sidebar. Las condiciones del menú repiten las del template actual (`is_company_admin`, `is_operador`, `is_cliente_final`). Puente `bootstrap5` mientras queden pantallas Lexa. Quedan fuera al principio `empresas/panel_base.html` (superadmin) y `reports/` (PDF).

**GEAGRO Cereales y Vid**: el portal (`templates/partials/base.html`, `sidebar.html`, `topbar.html`) pasa al layout del paquete; el filtro campaña/cultivo va en el bloque `topbar_context`. El backoffice Jazzmin **no se modifica** por ahora (decisión del 26/10/2026): ni navegación ni colores. Las dos ramas usan la misma versión del paquete y difieren solo en `PRODUCT` y `NAV`.

## Riesgos a vigilar

- No cargar el sidebar de Lexa y el de GENEOS UI en la misma página (`app.js` de Lexa controla clases del `<body>`).
- `jazzmin_custom.css` usa rutas fijas `/static/img/icons/…`.
- GEMA tiene `compañia.svg` duplicado con distinta normalización Unicode; no renombrar sin revisar referencias.
- Confirmar la versión de Python de producción de GEMA y GEAGRO (no está declarada en los repos).
