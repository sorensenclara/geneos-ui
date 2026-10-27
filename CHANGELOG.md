# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

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
