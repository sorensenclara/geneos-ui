"""Iconografía original de cada producto.

Los archivos están en ``static/geneos_ui/icons/<producto>/activos|disponibles/``
con su nombre original y sin modificaciones. ``product_icons.json`` (generado por
``tools/import_product_icons.py``) registra producto, módulo, variante, formato,
ruta de origen, commit, SHA-256 y estado de uso de cada uno.

En la navegación se referencian como ``"<producto>:<módulo>"``::

    NavItem("Clientes", url="cliente:list", icon="gema:clientes")
    NavItem("Fenología", url="fenologia", icon="geagro-vid:fenologia")   # pendiente → marcador neutro

Los nombres ``i-*`` del sprite siguen siendo los íconos de acciones comunes.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

MANIFEST = Path(__file__).with_name("product_icons.json")

# en el sidebar se usa la variante blanca; el set del portal tiene prioridad sobre el del backoffice
NAV_VARIANT = "white"
SET_PRIORITY = {"portal": 0, "modulos": 0, "menu": 0, "backoffice": 1}
# Navegación horizontal (barra blanca/oscura, igual en los cuatro productos).
# Variantes originales (reposo, activo) para fondo claro, cuando el producto las tiene:
#   GEMA: los SVG normales y "-active" de su menú superior (core/base.html).
#   GELECTRIC: los íconos de color de los módulos (core/static/core/images/SVG/icon - *.svg);
#   no hay variante activa, el activo se marca con la línea y el color del texto.
HNAV_VARIANTS = {"gema": ("base", "active"), "gelectric": ("tile", None)}
# GEAGRO solo tiene íconos blancos completos para estos módulos (las variantes "simple",
# "color" y "tile-vid" cubren solo algunos y mezclan estilos). En la barra se usa el mismo
# SVG blanco original como máscara, pintado con los tokens --gn-hnav-icon-tint(-active):
# misma forma, sin dibujar ni inventar íconos.
HNAV_TINT = {"geagro", "geagro-cereales", "geagro-vid"}


def hnav_paths(ref: str) -> tuple[str | None, str | None]:
    """Íconos originales de la navegación horizontal para "producto:módulo" (o (None, None))."""
    product = ref.partition(":")[0]
    variants = HNAV_VARIANTS.get(product)
    if not variants:
        return None, None
    return tuple(static_path(ref, v) if v else None for v in variants)


def hnav_tint(ref: str) -> bool:
    """True si en la barra horizontal el ícono blanco se pinta con los colores del tema."""
    return ref.partition(":")[0] in HNAV_TINT


@lru_cache(maxsize=1)
def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def icons(product: str | None = None, status: str | None = None) -> list[dict]:
    out = manifest()["icons"]
    if product:
        out = [i for i in out if i["product"] in _chain(product)]
    if status:
        out = [i for i in out if i["status"] == status]
    return out


def _chain(product: str) -> tuple[str, ...]:
    """GEAGRO Cereales y Vid comparten los archivos de "geagro"."""
    if product in ("geagro-cereales", "geagro-vid"):
        return (product, "geagro")
    return (product,)


def is_product_ref(name: str | None) -> bool:
    """"gema:clientes" sí; "i-users" o un texto con dos puntos, no."""
    return bool(name) and re.fullmatch(r"[a-z]+(-[a-z]+)*:[a-z]+(-[a-z]+)*", name) is not None


def resolve(ref: str, variant: str = NAV_VARIANT, set_name: str | None = None) -> dict | None:
    """``"gema:clientes"`` → registro del manifiesto (o el registro pendiente).

    ``set_name`` restringe a un conjunto: en GEAGRO, "portal" (portal del productor)
    o "backoffice" (Jazzmin), que tienen íconos distintos para el mismo módulo.
    """
    product, _, module = ref.partition(":")
    chain = _chain(product)
    candidates = [i for i in manifest()["icons"]
                  if i["product"] in chain and i["module"] == module and i["variant"] == variant
                  and (set_name is None or i["set"] == set_name)]
    if not candidates:
        return None
    candidates.sort(key=lambda i: (i["status"] == "pendiente", chain.index(i["product"]), SET_PRIORITY.get(i["set"], 2)))
    return candidates[0]


def static_path(ref: str, variant: str = NAV_VARIANT, set_name: str | None = None) -> str | None:
    rec = resolve(ref, variant, set_name)
    return rec["file"] if rec else None
