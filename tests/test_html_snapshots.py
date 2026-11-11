"""El HTML que genera el paquete para los cuatro productos no cambia respecto
de la referencia (tests/snapshots/<versión>/), salvo lo que normaliza
``generate.normalize`` (parámetro de versión y marcas del catálogo)."""
import difflib
import re
from pathlib import Path

import pytest

from tests.snapshots.generate import render_all

REFERENCE = "0.7.0"
REF_DIR = Path(__file__).resolve().parent / "snapshots" / REFERENCE


# Texto del catálogo que cambia con cada versión (no es diseño): se normaliza en los dos lados.
NORMALIZAR_AMBOS = [
    (r"geneos-ui @ git\+https://\S+?\.git@v[0-9.]+", "geneos-ui @ <repositorio>@vX"),  # línea de instalación (GitHub desde la 0.3.0)
]


def both(html):
    for pattern, repl in NORMALIZAR_AMBOS:
        html = re.sub(pattern, repl, html)
    return re.sub(r"\n[ \t]*(?=\n)", "", html)  # líneas en blanco que dejan los {% if %}


@pytest.fixture(scope="module")
def current():
    return render_all()


@pytest.mark.parametrize("name", sorted(p.stem for p in REF_DIR.glob("*.html")))
def test_html_igual_a_la_referencia(current, name):
    expected = both((REF_DIR / f"{name}.html").read_text(encoding="utf-8"))
    got = both(current[name])
    if got != expected:
        diff = "\n".join(list(difflib.unified_diff(expected.splitlines(), got.splitlines(), REFERENCE, "actual", lineterm="", n=1))[:60])
        pytest.fail(f"{name}: el HTML cambió respecto de {REFERENCE}\n{diff}")
