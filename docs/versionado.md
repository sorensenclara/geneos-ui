# Versiones de GENEOS UI

GENEOS UI sigue [SemVer](https://semver.org/lang/es/) sobre la API pública de [`api.md`](api.md). La fuente es GitHub (`sorensenclara/geneos-ui`), con un tag `vX.Y.Z` por versión. Cada producto fija una versión exacta en su `requirements.txt` y la actualiza en su rama de trabajo, con revisión.

## Qué tipo de cambio es

| Cambio | Versión |
| --- | --- |
| Corrección visual o de comportamiento que no cambia el HTML generado ni la API | Corrección (`0.3.1`) |
| Componente, tag, clave de `GENEOS_UI`, token o variante nuevos; HTML generado distinto con el mismo resultado visual | Menor (`0.4.0`) |
| Se quita o renombra algo de la API pública, o un producto tiene que tocar sus templates para seguir viéndose igual | Mayor (`1.0.0`) |

Mientras la versión empiece con `0.`, un cambio incompatible puede llegar en una versión menor, pero siempre con un aviso de deprecado en la versión anterior. Desde la `1.0.0`, solo en una mayor.

## Deprecado

1. Lo que se va a quitar sigue funcionando al menos una versión menor y emite `DeprecationWarning`, o un aviso de `manage.py check`.
2. Figura en la tabla «Deprecado» de [`api.md`](api.md) y en el `CHANGELOG.md`, con su reemplazo.
3. Se quita en la versión que indica esa tabla.

## Antes de publicar una versión

- [ ] `pytest` en verde, incluidas las pruebas de HTML de referencia (`tests/snapshots/`) y de navegador (`tests/visual/`).
- [ ] Capturas comparadas con la versión anterior (`tests/visual/capture.py` y `compare.py`, o el job de CI). Una diferencia buscada se revisa a mano y se anota en el `CHANGELOG.md`.
- [ ] Si cambió a propósito el HTML de los productos, se regenera la referencia (`python tests/snapshots/generate.py <versión>`) en el mismo commit y se explica en el `CHANGELOG.md`.
- [ ] Versión en `pyproject.toml`, `geneos_ui/__init__.py` y `GN.version`; el `CHANGELOG.md` con fecha.
- [ ] Aprobación de la responsable antes del tag y la publicación.

## Actualizar un producto

1. Cambiar el tag en `requirements.txt` y correr `pip install -r requirements.txt`.
2. `python manage.py check`: avisos de deprecado y de templates sobrescritos.
3. `python manage.py collectstatic`. El `?v=<versión>` evita que el navegador use el CSS anterior.
4. Revisar las pantallas principales en claro y oscuro, con menú vertical y horizontal, y en el celular.
