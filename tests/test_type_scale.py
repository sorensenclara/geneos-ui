"""Escala tipográfica (0.6.0): compacta por defecto, legible opcional.

GENEOS_UI["TYPE_SCALE"] = "legible" agrega data-gn-type="legible" en <html>;
sin esa clave el HTML es el mismo de la 0.5.0. Los componentes toman los
tamaños de tokens, así que la escala se cambia en un solo lugar.
"""
import re
from pathlib import Path

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings

from geneos_ui.checks import check_geneos_ui
from geneos_ui.conf import get_config
from geneos_ui.context_processors import geneos_ui as gn_context

CSS = Path(__file__).resolve().parents[1] / "geneos_ui" / "static" / "geneos_ui" / "css"
rf = RequestFactory()

# valores de la escala compacta: no cambian respecto de la 0.5.0
COMPACTA = {
    "--gn-fs-2xs": "10.5px", "--gn-fs-xs": "11.5px", "--gn-fs-sm": "12.5px", "--gn-fs-base": "13.5px",
    "--gn-fs-md": "15px", "--gn-fs-lg": "18px", "--gn-fs-xl": "20px", "--gn-fs-2xl": "26px",
    "--gn-control-sm": "28px", "--gn-control": "32px", "--gn-control-lg": "40px", "--gn-lh-base": "1.45",
}


def bloque(css, selector):
    i = css.index(selector)
    return css[css.index("{", i) + 1:css.index("}", i)]


def tokens(texto):
    return dict(re.findall(r"(--gn-[\w-]+):\s*([^;]+);", texto))


def layout(name="app"):
    request = rf.get("/")
    request.user = None
    ctx = gn_context(request)
    return render_to_string(f"geneos_ui/layouts/{name}.html", ctx, request=request)


def test_predeterminada_es_compacta():
    assert get_config()["TYPE_SCALE"] == "compacta"


@pytest.mark.parametrize("name", ["app", "auth"])
def test_compacta_no_agrega_atributo(name):
    with override_settings(GENEOS_UI={"PRODUCT": "gema"}):
        assert "data-gn-type" not in layout(name)


@pytest.mark.parametrize("name", ["app", "auth"])
def test_legible_marca_el_html(name):
    with override_settings(GENEOS_UI={"PRODUCT": "gema", "TYPE_SCALE": "legible"}):
        html = layout(name)
    assert re.search(r'<html [^>]*data-gn-type="legible"', html)


def test_valor_invalido_avisa_y_usa_la_compacta(settings):
    settings.GENEOS_UI = {"PRODUCT": "gema", "TYPE_SCALE": "grande"}
    assert get_config()["TYPE_SCALE"] == "compacta"
    assert [e.id for e in check_geneos_ui(None)] == ["geneos_ui.E007"]
    settings.GENEOS_UI = {"PRODUCT": "gema", "TYPE_SCALE": "legible"}
    assert [e.id for e in check_geneos_ui(None)] == []


def test_valores_compactos_sin_cambios():
    base = tokens(bloque((CSS / "tokens.css").read_text(), ":root,\n  [data-gn-product] {"))
    for k, v in COMPACTA.items():
        assert base[k] == v, k


def test_componentes_sin_tamanos_fijos():
    css = (CSS / "geneos-ui.css").read_text()
    fijos = re.findall(r"([^{}]+)\{[^{}]*font-size:\s*[\d.]+px", css)
    fijos = sorted({" ".join(s.split()) for s in fijos})
    # iniciales del avatar grande (decorativas) y el campo de fecha a 16 px en el celular (iOS)
    assert fijos == [".gn-avatar--lg", ".gn-datetime > .gn-input"]


def test_legible_cumple_los_minimos():
    css = (CSS / "tokens.css").read_text()
    sel = ':root[data-gn-type="legible"],'
    escritorio = tokens(bloque(css, sel))
    movil = tokens(bloque(css, '@media (max-width: 860px) {\n    ' + sel))
    px = {k: float(v[:-2]) for k, v in escritorio.items() if k.startswith("--gn-fs-") and v.endswith("px")}
    assert min(v for k, v in px.items() if k not in ("--gn-fs-donut-label",)) >= 12
    assert px["--gn-fs-donut-label"] * 1.25 >= 12       # viewBox de 120 dibujado a 150 px
    assert px["--gn-fs-base"] == 15
    assert px["--gn-fs-control"] == px["--gn-fs-sm"] == 14   # tablas y secundarios
    assert px["--gn-fs-meta"] == px["--gn-fs-xs"] == 13      # ayudas
    assert escritorio["--gn-control"] == "36px"
    assert movil["--gn-control"] == movil["--gn-control-sm"] == movil["--gn-field-h"] == "40px"
    assert movil["--gn-choice-pad"] == "9px"
    assert px["--gn-fs-kpi-trend"] == 14                    # descripción secundaria del KPI
    assert movil["--gn-fs-input"] == movil["--gn-fs-input-sm"] == movil["--gn-fs-input-xs"] == "16px"


def test_todos_los_tokens_usados_estan_definidos():
    definidos = set(tokens((CSS / "tokens.css").read_text()))
    usados = set(re.findall(r"var\((--gn-(?:fs|lh|size)-[\w-]+)\)", (CSS / "geneos-ui.css").read_text()))
    assert usados <= definidos, usados - definidos


def test_tokens_sin_nombres_repetidos():
    # un token de tamaño con el nombre de un color pisaría el color (pasó con --gn-field)
    texto = bloque((CSS / "tokens.css").read_text(), ":root,\n  [data-gn-product] {")
    nombres = re.findall(r"(--gn-[\w-]+):", re.sub(r"/\*.*?\*/", "", texto, flags=re.S))
    assert len(nombres) == len(set(nombres)), [n for n in set(nombres) if nombres.count(n) > 1]
