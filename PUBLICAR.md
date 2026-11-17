# Publicar una versión de GENEOS UI

- Las versiones se publican como **GitHub Releases** de `sorensenclara/geneos-ui`.
- No hace falta configurar nada ni cargar credenciales: el flujo usa el token automático de GitHub Actions.
- El repositorio es público, así que los productos descargan el paquete sin cuenta ni token.

## Tipos de versión

| Etiqueta | Tipo | Desde dónde | En GitHub |
|---|---|---|---|
| `v0.9.0rc1`, `v0.9.0rc2`… | De prueba (candidata) | Cualquier rama | *Pre-release* |
| `v0.9.0` | Estable | Solo un commit que ya está en `main` | *Latest* |

## Publicar

1. **Antes de una versión nueva** (por ejemplo, de 0.9.0 a 0.10.0), actualizar `0.9.0`:
   - en `pyproject.toml`;
   - en `geneos_ui/__init__.py`;
   - en `window.GN.version` de `geneos-ui.js`.

   Además, agregar la sección correspondiente en `CHANGELOG.md`.

   Para una candidata, en esos tres archivos va el número **sin** `rcN` (`0.9.0`): el flujo agrega el `rc1` solo en el paquete.

2. **Subir los cambios y la etiqueta:**
   - versión de prueba, desde la rama de trabajo:
     ```bash
     git push origin feature/mi-rama
     git tag v0.9.0rc1
     git push origin v0.9.0rc1
     ```
   - versión estable, desde `main`:
     ```bash
     git checkout main && git pull
     git tag v0.9.0
     git push origin v0.9.0
     ```

3. **Mirar el resultado** en *Actions → Publicar versión de GENEOS UI*. El flujo hace esto, en orden:
   1. **Verifica.**
      - La etiqueta tiene que tener formato `vX.Y.Z` o `vX.Y.ZrcN`.
      - La versión tiene que coincidir con los tres archivos.
      - No tiene que existir ya un release con ese nombre.
      - Si es estable, el commit tiene que estar en `main`.
   2. **Prueba:** corre las pruebas con Python 3.10 y 3.13.
   3. **Construye:** arma el wheel y el sdist, calcula `SHA256SUMS` e instala el wheel en un entorno vacío.
   4. **Publica:** crea el release con los tres archivos y la línea de instalación lista para copiar.

   Si algo falla, no se publica nada. Una etiqueta mal escrita no publica nada.

## Instalar en un producto

En el `requirements.txt` del producto va una sola línea, copiada de las notas del release:

```
geneos-ui @ https://github.com/sorensenclara/geneos-ui/releases/download/v0.9.0rc1/geneos_ui-0.9.0rc1-py3-none-any.whl#sha256=<hash>
```

- `pip install -r requirements.txt` la descarga y **verifica el SHA256**. Si el archivo no coincide, la instalación falla.
- Para actualizar GENEOS UI en un producto, se reemplaza esa línea por la del release nuevo.

## Reglas de seguridad

- **Las versiones publicadas no se modifican.** Si un release tiene un error, se publica otro número: `rc2` o `0.9.1`. El flujo rechaza una etiqueta cuyo release ya existe.
- **Las versiones anteriores siguen disponibles sin cambios.** Los productos que usan `v0.2.0` a `v0.8.0` no se ven afectados.
- **No borrar etiquetas ni releases publicados**: algún producto puede depender de ellos.
- **Si una publicación quedó a medias**, por ejemplo un pre-release creado sin archivos: borrar ese pre-release en GitHub y publicar el número siguiente.
