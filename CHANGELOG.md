# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Versionado [SemVer](https://semver.org/lang/es/).

## [0.1.0] · 2026-10-26 · borrador para aprobación

### Agregado
- Tokens base (`tokens.css`) con neutros, tipografía Titillium Web, espaciado de 4 px, radios y sombras de GELECTRIC, colores derivados por `color-mix()` y modo oscuro opcional.
- Temas de GELECTRIC (verde por defecto, variante azul), GEMA (azul y naranja), GEAGRO Cereales (verde y amarillo) y GEAGRO Vid (violeta y verde), con colores tomados de cada repositorio.
- Componentes `gn-*` en `@layer geneos-ui`: sidebar con submenús y buscador, encabezado, breadcrumbs, pestañas, menús desplegables, botones, formularios, buscadores, filtros combinados, tablas responsive con acordeón y orden, paginación, tarjetas, indicadores, gráficos de línea y dona, badges, alertas, notificaciones, modales, tooltips, acordeones, pasos, vacío y carga.
- `geneos-ui.js` sin dependencias.
- Navegación declarativa (`NavItem`, `NavSection`) con permisos, ítem activo e índice de búsqueda.
- Template tags, layouts de aplicación y login, catálogo `/ui-kit/` y `tools/build_catalog.py`.
- Puentes opcionales para Bootstrap 5 (Lexa) y Jazzmin.
