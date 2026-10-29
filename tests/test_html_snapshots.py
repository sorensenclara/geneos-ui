"""El HTML que genera el paquete para los cuatro productos no cambia respecto
de la referencia (tests/snapshots/<versión>/), salvo lo que normaliza
``generate.normalize`` (parámetro de versión y marcas del catálogo)."""
import difflib
from pathlib import Path

import pytest

from tests.snapshots.generate import render_all

REFERENCE = "0.2.1"
REF_DIR = Path(__file__).resolve().parent / "snapshots" / REFERENCE


@pytest.fixture(scope="module")
def current():
    return render_all()


@pytest.mark.parametrize("name", sorted(p.stem for p in REF_DIR.glob("*.html")))
def test_html_igual_a_la_referencia(current, name):
    expected = (REF_DIR / f"{name}.html").read_text(encoding="utf-8")
    got = current[name]
    if got != expected:
        diff = "\n".join(list(difflib.unified_diff(expected.splitlines(), got.splitlines(), REFERENCE, "actual", lineterm="", n=1))[:60])
        pytest.fail(f"{name}: el HTML cambió respecto de {REFERENCE}\n{diff}")
