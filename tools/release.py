"""Verificaciones de publicación de GENEOS UI (usadas por .github/workflows/release.yml).

    python tools/release.py verificar v0.9.0        # la etiqueta coincide con la versión del código
    python tools/release.py preparar  v0.9.0rc1     # solo en CI: escribe 0.9.0rc1 en la copia de trabajo

Reglas:
- Etiquetas válidas: vX.Y.Z (estable) o vX.Y.ZrcN (candidata). Nada más.
- X.Y.Z tiene que ser exactamente la versión de pyproject.toml, geneos_ui/__init__.py y geneos-ui.js.
- Una candidata (rcN) se publica con su número completo sin modificar el repositorio: CI reescribe
  la versión solo en la copia que construye.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVOS = {
    "pyproject.toml": (r'^version = "([^"]+)"$', 'version = "{v}"'),
    "geneos_ui/__init__.py": (r'^__version__ = "([^"]+)"$', '__version__ = "{v}"'),
    "geneos_ui/static/geneos_ui/js/geneos-ui.js": (r'window\.GN\.version = "([^"]+)";', 'window.GN.version = "{v}";'),
}
ETIQUETA = re.compile(r"^v(?P<base>\d+\.\d+\.\d+)(?P<rc>rc\d+)?$")


def leer_etiqueta(etiqueta):
    m = ETIQUETA.match(etiqueta)
    if not m:
        sys.exit(f"Etiqueta inválida «{etiqueta}»: usar vX.Y.Z o vX.Y.ZrcN (por ejemplo v0.9.0 o v0.9.0rc1).")
    return m["base"], m["base"] + (m["rc"] or ""), bool(m["rc"])


def versiones():
    encontradas = {}
    for ruta, (patron, _) in ARCHIVOS.items():
        m = re.search(patron, (RAIZ / ruta).read_text(encoding="utf-8"), re.M)
        if not m:
            sys.exit(f"No encontré la versión en {ruta}.")
        encontradas[ruta] = m.group(1)
    return encontradas


def verificar(etiqueta):
    base, completa, candidata = leer_etiqueta(etiqueta)
    distintas = {r: v for r, v in versiones().items() if v != base}
    if distintas:
        detalle = ", ".join(f"{r} = {v}" for r, v in distintas.items())
        sys.exit(f"La etiqueta {etiqueta} pide la versión {base}, pero el código dice: {detalle}.")
    print(f"ok: {etiqueta} → paquete {completa} ({'candidata' if candidata else 'estable'})")
    return completa, candidata


def preparar(etiqueta):
    completa, candidata = verificar(etiqueta)
    if candidata:
        for ruta, (patron, plantilla) in ARCHIVOS.items():
            p = RAIZ / ruta
            p.write_text(re.sub(patron, plantilla.format(v=completa), p.read_text(encoding="utf-8"), count=1, flags=re.M), encoding="utf-8")
        print(f"versión de la copia de trabajo: {completa}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("verificar", "preparar"):
        sys.exit(__doc__)
    {"verificar": verificar, "preparar": preparar}[sys.argv[1]](sys.argv[2])
