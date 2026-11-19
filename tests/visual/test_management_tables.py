"""Densidad, sticky, edición y acordeones sobre el UI Kit real."""
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")
DIST = Path(__file__).resolve().parents[2] / "dist" / "ui-kit.html"
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

    def open_page(width):
        context = browser.new_context(viewport={"width": width, "height": 900})
        contexts.append(context)
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        page.goto(DIST.as_uri() + "#datos")
        page.get_by_label("Escala tipográfica").select_option("legible")
        return page

    yield open_page
    for context in contexts:
        context.close()


def test_densidad_y_variantes_independientes(open_kit):
    page = open_kit(1440)
    standard = page.locator("#datos .gn-table:not(.gn-table--compact):visible")
    compact = page.get_by_role("table", name="Inventario compacto")
    editable = page.get_by_role("table", name="Líneas editables de un pedido")
    assert standard.locator("tbody tr").first.bounding_box()["height"] > 36
    for table in (compact, editable):
        assert table.locator("tbody tr").evaluate_all(
            "rows => [...new Set(rows.map(row => row.getBoundingClientRect().height))]"
        ) == [36]
    field = editable.get_by_label("Cantidad de producto A")
    assert field.bounding_box()["height"] == 28
    assert field.evaluate("el => getComputedStyle(el).textAlign") == "right"
    editable.evaluate("table => table.classList.remove('gn-table--compact')")
    assert editable.locator("tbody tr").first.bounding_box()["height"] > 36
    assert field.bounding_box()["height"] == 28
    compact.evaluate("table => table.style.width = '300px'")
    assert compact.locator(".gn-table__truncate").first.evaluate(
        "el => el.scrollWidth > el.clientWidth && getComputedStyle(el).textOverflow === 'ellipsis'"
    )
    assert compact.get_by_text("Disponible", exact=True).count() == 2
    standard.locator(".gn-table__sort").first.click()
    assert standard.locator("thead th").first.get_attribute("aria-sort") == "ascending"


def test_cabecera_y_totales_siguen_visibles_al_desplazar(open_kit):
    page = open_kit(1440)
    region = page.get_by_role("region", name="Editable compacta")
    metrics = """el => {
      const box = el.getBoundingClientRect();
      return [el.scrollTop, el.querySelector('th').getBoundingClientRect().top - box.top,
              box.bottom - el.querySelector('tfoot td').getBoundingClientRect().bottom];
    }"""
    start = region.evaluate(metrics)
    region.evaluate("el => el.scrollTop = el.scrollHeight")
    end = region.evaluate(metrics)
    assert start[0] == 0 < end[0]
    for _, head, total in (start, end):
        assert 0 <= head <= 2
        assert 0 <= total <= 2


def test_teclado_salta_no_editables_y_respeta_validacion(open_kit):
    page = open_kit(1440)
    table = page.get_by_role("table", name="Líneas editables de un pedido")
    a, b, c = [table.get_by_label(f"Cantidad de producto {code}") for code in "ABC"]
    b.evaluate("el => el.disabled = true")
    a.fill("5")
    a.press("Enter")
    assert c.evaluate("el => el === document.activeElement")
    c.press("Enter")
    d = table.get_by_label("Cantidad de producto D")
    assert d.evaluate("el => el === document.activeElement")
    d_box = d.bounding_box()
    assert d_box["y"] + d_box["height"] <= table.locator("tfoot td").bounding_box()["y"]
    d.press("Shift+Enter")
    c.press("Shift+Enter")
    assert a.evaluate("el => el === document.activeElement")
    a.press("Tab")
    assert table.get_by_role("button", name="Restablecer producto A").evaluate("el => el === document.activeElement")
    a.fill("0")
    assert a.get_attribute("aria-invalid") == "true"
    assert a.locator("xpath=ancestor::tr").get_attribute("data-gn-row-state") == "invalid"
    a.press("Enter")
    assert a.evaluate("el => el === document.activeElement")
    table.get_by_role("button", name="Restablecer producto A").click()
    assert a.input_value() == "1"
    assert a.locator("xpath=ancestor::tr").get_attribute("data-gn-row-state") is None


@pytest.mark.parametrize("width", [390, 320])
def test_acordeon_responsive_abre_sin_desbordar(open_kit, width):
    page = open_kit(width)
    table = page.get_by_role("table", name="Líneas editables de un pedido")
    assert page.evaluate("document.documentElement.scrollWidth === document.documentElement.clientWidth")
    assert table.locator("tfoot td").evaluate("el => getComputedStyle(el).position") == "static"
    assert table.get_by_text("Líneas del pedido: 6").is_visible()
    badges = page.get_by_role("table", name="Inventario compacto").locator(".gn-badge")
    assert badges.evaluate_all("""els => els.every(el => el.getBoundingClientRect().right <=
      el.closest('td').getBoundingClientRect().right)""")
    standard = page.locator("#datos .gn-table:not(.gn-table--compact):visible")
    summary = standard.locator(".gn-row-summary__btn").first
    summary.click()
    assert summary.get_attribute("aria-expanded") == "true"
    a, b, c = [table.get_by_label(f"Cantidad de producto {code}") for code in "ABC"]
    assert a.is_visible() and not b.is_visible()
    table.get_by_role("button", name="Producto C", exact=True).click()
    a.press("Enter")
    assert c.evaluate("el => el === document.activeElement")
    assert c.bounding_box()["height"] == 28
    b.evaluate("el => { el.value = '0'; el.reportValidity(); }")
    assert table.get_by_role("button", name="Producto B", exact=True).get_attribute("aria-expanded") == "true"
    assert b.is_visible()
