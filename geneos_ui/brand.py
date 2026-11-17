"""Identidad dinámica del menú lateral (0.9.0).

Un producto puede mostrar en el encabezado y el pie del sidebar la marca de la
institución con la que se está trabajando (un club, una cooperativa, un municipio…),
en lugar de su logo estático. Se declara con una función::

    GENEOS_UI = {..., "BRAND": "miapp.marca.brand"}

    def brand(request):            # -> Brand | dict | None
        return Brand(name="…", logo_url="…", mark_url="…", footer=["…", "…"])

Prioridad con el menú abierto: logotipo horizontal → isotipo y nombre → iniciales y
nombre. Con el menú contraído: isotipo → iniciales. Sin función, o si devuelve None,
el sidebar queda exactamente como con LOGO_FULL / LOGO_ICON.

Las URL se validan (solo rutas absolutas del sitio o http/https): un valor que no
cumple se descarta y se pasa al siguiente nivel de la prioridad. Los textos se
escapan al dibujarse; acá solo se recortan.
"""
from dataclasses import dataclass, field
import re
from typing import Optional, Sequence

_URL_OK = re.compile(r"^(https?://[^\s/$.?#][^\s]*|/(?!/)[^\s]*)$", re.I)
_PROHIBIDOS = set('<>"\'`\\') | {"\x00"}
_CONECTORES = {"de", "del", "la", "las", "los", "el", "y", "e", "the", "of", "and"}

MAX_NAME = 80
MAX_FOOTER_LINES = 3
MAX_FOOTER_LEN = 90


@dataclass
class Brand:
    name: str                            # nombre de la institución (obligatorio)
    logo_url: Optional[str] = None       # logotipo horizontal
    mark_url: Optional[str] = None       # escudo / isotipo (espacios reducidos)
    initials: Optional[str] = None       # sin isotipo; si falta se calcula del nombre
    home_url: Optional[str] = None       # destino al tocar la marca; si falta, HOME_URL
    footer: Sequence[str] = field(default_factory=tuple)   # 1 a 3 líneas discretas para el pie


def safe_url(value):
    """La URL si es una ruta absoluta del sitio o http(s); None en cualquier otro caso."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or any(c in _PROHIBIDOS for c in value) or not _URL_OK.match(value):
        return None
    return value


def initials_of(name, n=2):
    palabras = [p for p in re.split(r"[\s\-_/.]+", name or "") if p and p[0].isalnum()]
    utiles = [p for p in palabras if p.lower() not in _CONECTORES] or palabras
    return "".join(p[0] for p in utiles[:n]).upper()


def resolve_brand(value):
    """Normaliza lo que devuelve la función BRAND. None si no hay marca utilizable."""
    if value is None:
        return None
    if isinstance(value, Brand):
        value = value.__dict__
    if not isinstance(value, dict):
        return None
    name = " ".join(str(value.get("name") or "").split())[:MAX_NAME]
    if not name:
        return None
    initials = "".join(str(value.get("initials") or "").split())[:3].upper() or initials_of(name)
    footer = value.get("footer") or ()
    if isinstance(footer, str):
        footer = [footer]
    lines = [" ".join(str(l).split())[:MAX_FOOTER_LEN] for l in footer]
    return {
        "name": name,
        "logo_url": safe_url(value.get("logo_url")),
        "mark_url": safe_url(value.get("mark_url")),
        "initials": initials,
        "home_url": safe_url(value.get("home_url")),
        "footer": [l for l in lines if l][:MAX_FOOTER_LINES],
    }
