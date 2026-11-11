"""Filtros progresivos y padding en el catálogo generado."""
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

sync_api = pytest.importorskip("playwright.sync_api")
DIST = Path(__file__).resolve().parents[2] / "dist" / "ui-kit.html"
URL = "http://ui-kit.test/"
pytestmark = pytest.mark.skipif(not DIST.exists(), reason="falta dist/ui-kit.html")


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"Chromium no disponible: {exc}")
        yield browser
        browser.close()


@pytest.fixture
def open_kit(browser):
    contexts = []

    def open_page(width, *, js=True, applied=False):
        context = browser.new_context(viewport={"width": width, "height": 900}, java_script_enabled=js)
        contexts.append(context)
        html = DIST.read_text(encoding="utf-8")
        if applied:
            html = html.replace('name="desde" value=""', 'name="desde" value="2026-11-01"', 1)
        context.route("**/*", lambda route: route.fulfill(body=html, content_type="text/html")
                      if route.request.url.startswith(URL) else route.abort())
        page = context.new_page()
        if applied:
            page.add_init_script('sessionStorage.setItem("gn-filters:/:kit-prog-secondary", "0")')
        page.goto(URL + "#filtros-progresivos")
        form = page.get_by_role("form", name="Filtrar pedidos")
        return page, form

    yield open_page
    for context in contexts:
        context.close()


@pytest.mark.parametrize(("width", "collapsed"), [(1440, False), (992, False), (991, True), (390, True), (320, True)])
def test_puntos_de_corte_y_padding(open_kit, width, collapsed):
    page, form = open_kit(width)
    toggle = form.locator("[data-gn-filters-more]")
    assert toggle.is_visible() == collapsed
    assert form.get_by_label("Pedido", exact=True).is_visible()
    assert form.get_by_label("Canal").is_visible() != collapsed
    if collapsed:
        toggle.click()
    assert form.get_by_label("Canal").is_visible()
    assert page.evaluate("document.documentElement.scrollWidth === document.documentElement.clientWidth")
    assert form.evaluate("el => el.scrollWidth === el.clientWidth")

    field = form.get_by_label("Desde").locator("..")
    columns = field.evaluate("el => getComputedStyle(el).gridColumn")
    if width < 360:
        assert columns == "1 / -1"
    if 360 <= width < 992:
        pedido = form.get_by_label("Pedido", exact=True).bounding_box()
        estado = form.get_by_label("Estado").bounding_box()
        assert estado["x"] > pedido["x"]
    for card, padding in [(form, 20), (page.locator("#kit-card-padded"), 20),
                          (page.locator("#kit-card-compact"), 12), (page.locator("#kit-card-flush"), 0)]:
        assert card.evaluate("el => getComputedStyle(el).padding") == f"{padding}px"
    assert page.locator("#kit-card-padded .gn-card__body").evaluate("el => getComputedStyle(el).padding") == "0px"


def test_accesible_por_teclado_y_recuerda_estado(open_kit):
    page, form = open_kit(390)
    toggle = form.get_by_role("button", name="Más filtros")
    assert toggle.get_attribute("aria-controls") == "kit-prog-secondary"
    assert toggle.get_attribute("aria-expanded") == "false"
    toggle.focus()
    page.keyboard.press("Space")
    opened = form.get_by_role("button", name="Menos filtros")
    assert opened.get_attribute("aria-expanded") == "true"
    assert opened.evaluate("el => el === document.activeElement")
    page.keyboard.press("Tab")
    assert form.get_by_label("Canal").evaluate("el => el === document.activeElement")
    page.reload()
    opened = form.get_by_role("button", name="Menos filtros")
    assert opened.is_visible()
    opened.focus()
    page.keyboard.press("Enter")
    assert form.get_by_role("button", name="Más filtros").get_attribute("aria-expanded") == "false"
    page.keyboard.press("Tab")
    assert form.get_by_role("button", name="Filtrar", exact=True).evaluate("el => el === document.activeElement")
    page.reload()
    assert not form.get_by_label("Canal").is_visible()
    page.set_viewport_size({"width": 992, "height": 900})
    assert form.get_by_label("Canal").is_visible()
    page.set_viewport_size({"width": 991, "height": 900})
    assert not form.get_by_label("Canal").is_visible()


@pytest.mark.parametrize("action", ["Filtrar", "Exportar"])
def test_contador_y_envio_con_secundarios_contraidos(open_kit, action):
    page, form = open_kit(390)
    form.get_by_role("button", name="Más filtros").click()
    assert not form.locator("[data-gn-filters-more-count]").is_visible()
    form.get_by_label("Canal").select_option("tienda")
    form.get_by_label("Desde").fill("2026-11-01")
    assert form.get_by_role("button", name="Menos filtros, 2 en uso").is_visible()
    form.get_by_label("Canal").select_option("todos")
    form.get_by_role("button", name="Menos filtros, 1 en uso").click()
    assert not form.get_by_label("Desde").is_visible()
    assert form.get_by_label("Desde").input_value() == "2026-11-01"
    with page.expect_navigation():
        form.get_by_role("button", name=action, exact=True).click()
    query = parse_qs(urlsplit(page.url).query)
    assert query["desde"] == ["2026-11-01"]
    assert query["canal"] == ["todos"]
    assert query.get("formato") == (["csv"] if action == "Exportar" else None)
    assert form.get_by_role("button", name="Menos filtros, 1 en uso").is_visible()
    assert form.get_by_label("Desde").input_value() == "2026-11-01"


def test_aplicados_prevalecen_sobre_sesion_contraida(open_kit):
    _, form = open_kit(390, applied=True)
    assert form.get_by_role("button", name="Menos filtros, 1 en uso").is_visible()
    assert form.get_by_label("Desde").is_visible()


def test_sin_javascript(open_kit):
    _, form = open_kit(320, js=False)
    assert not form.locator("[data-gn-filters-more]").is_visible()
    assert form.get_by_label("Pedido", exact=True).is_visible()
    assert form.get_by_label("Canal").is_visible()
    assert form.get_by_label("Desde").is_visible()


def test_validacion_nativa_revela_un_secundario_invalido(open_kit):
    _, form = open_kit(390)
    date = form.get_by_label("Desde")
    date.evaluate("el => el.required = true")
    form.get_by_role("button", name="Filtrar", exact=True).click()
    assert form.get_by_role("button", name="Menos filtros").is_visible()
    assert date.evaluate("el => el === document.activeElement")


def test_filtros_combinados_y_ficha_anterior_conservan_su_comportamiento(open_kit):
    page, _ = open_kit(390)
    card = page.locator("[data-kit-filters-card]:visible")
    panel = card.locator(".gn-filters__panel")
    toggle = card.locator("[data-gn-filters-toggle]")
    assert card.locator(".gn-card__body").evaluate("el => getComputedStyle(el).padding") == "16px 18px"
    assert not panel.is_visible()
    toggle.click()
    assert panel.is_visible()
    assert toggle.get_attribute("aria-expanded") == "true"
    assert panel.get_by_role("button", name="Agregar filtro").is_visible()


def test_rango_de_fechas_apilado_cuenta_como_un_filtro(open_kit):
    _, form = open_kit(320)
    form.get_by_role("button", name="Más filtros").click()
    start, end = form.get_by_label("Desde"), form.get_by_label("Hasta")
    form.evaluate("""form => {
      const start = form.querySelector('#kit-prog-from');
      const end = form.querySelector('#kit-prog-to');
      const range = document.createElement('div');
      range.className = 'gn-filter__range';
      start.parentElement.append(range);
      range.append(start, end);
      form.querySelector('label[for="kit-prog-to"]').parentElement.remove();
      end.setAttribute('aria-label', 'Hasta');
    }""")
    start.fill("2026-11-01")
    end.fill("2026-11-30")
    first, last = start.bounding_box(), end.bounding_box()
    assert last["y"] > first["y"] and first["width"] == last["width"] >= 200
    assert form.get_by_role("button", name="Menos filtros, 1 en uso").is_visible()
