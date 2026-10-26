# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

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
