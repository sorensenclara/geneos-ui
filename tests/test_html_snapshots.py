"""El HTML que genera el paquete para los cuatro productos no cambia respecto
de la referencia (tests/snapshots/<versión>/), salvo lo que normaliza
``generate.normalize`` (parámetro de versión y marcas del catálogo)."""
import difflib
import re
from pathlib import Path

import pytest

from tests.snapshots.generate import render_all

REFERENCE = "0.2.1"
REF_DIR = Path(__file__).resolve().parent / "snapshots" / REFERENCE


# Cambios de HTML hechos a propósito en la 0.3.0, sin efecto visual ni de comportamiento.
# Se quitan del HTML actual antes de comparar; cada uno tiene su propio test.
CAMBIOS_INTENCIONALES = [
    # la clave vieja del sidebar de GELECTRIC pasó del JS (/gelectric$/) a un atributo del sidebar
    (r' data-gn-legacy-key="[^"]*"', ""),
    # los tripletes --bs-*-rgb pasaron de bridges/bootstrap5.css a un <style> que escribe gn_css
    (r'\n<style>:root\[data-gn-product="[a-z-]+"\] \{[^<]*\}</style>', ""),
]


@pytest.fixture(scope="module")
def current():
    out = render_all()
    for pattern, repl in CAMBIOS_INTENCIONALES:
        out = {k: re.sub(pattern, repl, v) for k, v in out.items()}
    return out


@pytest.mark.parametrize("name", sorted(p.stem for p in REF_DIR.glob("*.html")))
def test_html_igual_a_la_referencia(current, name):
    expected = (REF_DIR / f"{name}.html").read_text(encoding="utf-8")
    got = current[name]
    if got != expected:
        diff = "\n".join(list(difflib.unified_diff(expected.splitlines(), got.splitlines(), REFERENCE, "actual", lineterm="", n=1))[:60])
        pytest.fail(f"{name}: el HTML cambió respecto de {REFERENCE}\n{diff}")
