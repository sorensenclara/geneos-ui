"""Escala legible (0.6.0) en Chromium, sobre el catálogo construido con data-gn-type="legible".

Tamaños por función, ningún texto de componente por debajo de 12 px, controles
de 36 px en escritorio y 40 en el celular, campos a 16 px en el celular y sin
scroll horizontal. Se saltea si no está Playwright o falta dist/ui-kit.html.
"""
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")
DIST = Path(__file__).resolve().parents[2] / "dist" / "ui-kit.html"
pytestmark = pytest.mark.skipif(not DIST.exists(), reason="falta dist/ui-kit.html")

SIZES = """(sel) => [...document.querySelectorAll(sel)].filter(e => e.getClientRects().length)
  .map(e => parseFloat(getComputedStyle(e).fontSize))"""
HEIGHTS = """(sel) => [...document.querySelectorAll(sel)].filter(e => e.getClientRects().length)
  .map(e => Math.round(e.getBoundingClientRect().height))"""
# textos de componentes gn-*, sin la documentación del catálogo (kit-*, código, listas de notas)
MINIMO = """() => { const r = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const e = w.currentNode.parentElement; if (!w.currentNode.textContent.trim()) continue;
    if (!e.closest('[class^="gn-"], [class*=" gn-"]') || e.closest('[class*="kit-"], code, pre, .gn-card__body > ul, small')) continue;
    if (!e.getClientRects().length) continue;
    const fs = parseFloat(getComputedStyle(e).fontSize) * (e.closest('svg') ? e.closest('svg').getBoundingClientRect().width / e.closest('svg').viewBox.baseVal.width : 1);
    if (fs < 12) r.push([fs, e.tagName + '.' + (e.getAttribute('class') || '')]); }
  return r; }"""


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as pw:
        try:
            b = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"Chromium no disponible: {exc}")
        yield b
        b.close()


@pytest.fixture(autouse=True)
def close_pages(browser):
    yield
    for context in browser.contexts:
        context.close()


def open_page(browser, width, section="", legible=True):
    page = browser.new_page(viewport={"width": width, "height": 900})
    page.route("https://**/*", lambda route: route.abort())
    page.goto(DIST.as_uri() + section)
    if legible:
        page.get_by_label("Escala tipográfica").select_option("legible")
    return page


@pytest.mark.parametrize("sel,px", [
    (".gn-content", 15), (".gn-table td", 14), (".gn-table th", 13), (".gn-field__help", 13),
    (".gn-input:not(.gn-input--sm):not(.gn-time__input)", 15), (".gn-btn:not(.gn-btn--sm):not(.gn-btn--lg)", 14),
    (".gn-badge", 13), (".gn-card__title", 18), (".gn-alert__body", 15),
])
def test_tamanos_por_funcion(browser, sel, px):
    page = open_page(browser, 1440)
    sizes = page.evaluate(SIZES, sel)
    assert sizes and set(sizes) == {px}, (sel, set(sizes))


@pytest.mark.parametrize("width", [1440, 390])
def test_ningun_texto_de_componente_menor_a_12(browser, width):
    page = open_page(browser, width)
    assert page.evaluate(MINIMO) == []


def test_controles_36_en_escritorio_y_40_en_el_celular(browser):
    sel = ".gn-btn:not(.gn-btn--lg)"
    assert set(open_page(browser, 1440).evaluate(HEIGHTS, sel + ":not(.gn-btn--sm)")) == {36}
    movil = open_page(browser, 390)
    assert set(movil.evaluate(HEIGHTS, sel)) == {40}     # también los chicos: acciones de tarjetas y tablas
    assert set(movil.evaluate(HEIGHTS, ".gn-topbar__menu, .gn-user-chip")) <= {40}
    # casillas e interruptores: área táctil de 40 px o más sin cambiar el alto de la fila
    assert min(movil.evaluate(HEIGHTS, ".gn-check, .gn-switch")) >= 40
    assert set(movil.evaluate(SIZES, ".gn-input, .gn-select, .gn-textarea")) == {16}
    assert set(movil.evaluate(HEIGHTS, ".gn-input:not(.gn-input--sm):not(.gn-time__input), .gn-select:not(.gn-select--sm):not(.gn-pagination__size *)")) == {40}


@pytest.mark.parametrize("width", [1440, 390, 320])
def test_sin_scroll_horizontal(browser, width):
    page = open_page(browser, width)
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")


def test_compacta_sin_atributo_mantiene_los_valores(browser):
    page = open_page(browser, 1440, legible=False)
    assert set(page.evaluate(SIZES, ".gn-table td")) == {13}
    assert set(page.evaluate(SIZES, ".gn-content")) == {13.5}


@pytest.mark.parametrize("width", [1440, 390])
def test_selector_alterna_y_recuerda_la_escala(browser, width):
    page = open_page(browser, width, legible=False)
    selector = page.get_by_label("Escala tipográfica")
    assert selector.input_value() == "compacta"
    selector.select_option("legible")
    assert page.locator("html").get_attribute("data-gn-type") == "legible"
    page.reload()
    assert selector.input_value() == "legible"
    assert page.locator("html").get_attribute("data-gn-type") == "legible"
    selector.select_option("compacta")
    assert page.locator("html").get_attribute("data-gn-type") is None
    page.reload()
    assert selector.input_value() == "compacta"
    assert page.locator("html").get_attribute("data-gn-type") is None
