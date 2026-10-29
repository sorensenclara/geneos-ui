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

from . import conf

MANIFEST = Path(__file__).with_name("product_icons.json")

# en el sidebar se usa la variante blanca; el set del portal tiene prioridad sobre el del backoffice
NAV_VARIANT = "white"
SET_PRIORITY = {"portal": 0, "modulos": 0, "menu": 0, "backoffice": 1}
# Barra horizontal clara: cada producto declara en GENEOS_UI["NAV_ICONS"] (o en su
# preset, ver presets.py) cómo se ven ahí sus íconos originales:
#   {"rest": variante, "active": variante}  variantes del manifiesto para fondo claro
#   "tint"                                   el SVG blanco original como máscara,
#                                            pintado con --gn-hnav-icon-tint(-active)
#   "as-is"                                  el mismo archivo que en el sidebar


def hnav_paths(ref: str) -> tuple[str | None, str | None]:
    """Íconos originales de la navegación horizontal para "producto:módulo" (o (None, None))."""
    mode = conf.nav_icons_for(ref.partition(":")[0])
    if not isinstance(mode, dict):
        return None, None
    return tuple(static_path(ref, mode.get(k)) if mode.get(k) else None for k in ("rest", "active"))


def hnav_tint(ref: str) -> bool:
    """True si en la barra horizontal el ícono blanco se pinta con los colores del tema."""
    return conf.nav_icons_for(ref.partition(":")[0]) == "tint"


@lru_cache(maxsize=8)
def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def manifest() -> dict:
    """Manifiesto del paquete más el del producto (GENEOS_UI["ICON_MANIFEST"]), si lo declara."""
    base = _load(str(MANIFEST))
    extra = conf.get_config().get("ICON_MANIFEST")
    if not extra:
        return base
    return {**base, "icons": base["icons"] + _load(str(extra))["icons"]}


def icons(product: str | None = None, status: str | None = None) -> list[dict]:
    out = manifest()["icons"]
    if product:
        out = [i for i in out if i["product"] in _chain(product)]
    if status:
        out = [i for i in out if i["status"] == status]
    return out


def _chain(product: str) -> tuple[str, ...]:
    """El producto y los conjuntos que comparte (``ICON_FAMILY``: Cereales y Vid usan "geagro")."""
    return conf.icon_family(product)


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


def __getattr__(name):  # compatibilidad con la 0.2.x: se quita en la 0.4.0
    if name in ("HNAV_VARIANTS", "HNAV_TINT"):
        import warnings
        from . import presets
        warnings.warn(f"geneos_ui.product_icons.{name} está deprecado: usar GENEOS_UI['NAV_ICONS'].", DeprecationWarning, stacklevel=2)
        modes = {k: v.get("NAV_ICONS") for k, v in presets.PRESETS.items()}
        if name == "HNAV_VARIANTS":
            return {k: (m["rest"], m["active"]) for k, m in modes.items() if isinstance(m, dict)}
        return {k for k, m in {**modes, **{k: v["NAV_ICONS"] for k, v in presets.ICON_SETS.items()}}.items() if m == "tint"}
    raise AttributeError(name)
