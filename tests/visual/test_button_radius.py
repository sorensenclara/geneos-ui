"""Radio y estilos compartidos por acciones de página, modales y confirmaciones."""
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")
DIST = Path(__file__).resolve().parents[2] / "dist" / "ui-kit.html"
pytestmark = pytest.mark.skipif(not DIST.exists(), reason="falta dist/ui-kit.html")
PRODUCTS = ("gelectric", "gema", "geagro-cereales", "geagro-vid")
STYLE = """el => {
    const css = getComputedStyle(el);
    return ["borderRadius", "borderTopWidth", "borderTopColor", "backgroundColor",
            "color", "fontSize", "fontWeight", "lineHeight", "height", "padding"]
        .map(key => css[key]);
}"""


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
def open_catalog(browser):
    contexts = []

    def open_page(width):
        context = browser.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce")
        contexts.append(context)
        context.route("https://**/*", lambda route: route.abort())
        page = context.new_page()
        page.goto(DIST.as_uri() + "#acciones")
        page.add_style_tag(content=".gn-btn { transition: none !important; }")
        return page

    yield open_page
    for context in contexts:
        context.close()


@pytest.mark.parametrize(("width", "scale"), [(1440, "compacta"), (1440, "legible"), (390, "legible"), (320, "legible")])
def test_radio_y_estilo_modal_en_cada_tema(open_catalog, width, scale):
    page = open_catalog(width)
    page.get_by_label("Escala tipográfica").select_option(scale)
    for product in PRODUCTS:
        page.locator(f'[data-kit-switch="{product}"]').click()
        page.mouse.move(0, 0)
        assert page.locator(".gn-btn:visible").evaluate_all(
            "buttons => [...new Set(buttons.map(button => getComputedStyle(button).borderRadius))]"
        ) == ["32px"]

        examples = page.locator(f'#acciones [data-kit-product="{product}"]')
        tertiary = examples.locator(".gn-btn--tertiary").first.evaluate(STYLE)
        destructive = examples.locator(".gn-btn--danger.gn-btn--solid").evaluate(STYLE)
        primary = examples.locator(".gn-btn--primary").first.evaluate(STYLE)

        examples.get_by_role("button", name="Eliminar", exact=True).click()
        confirm = page.locator(f"#{product}-confirm")
        assert confirm.is_visible()
        page.mouse.move(0, 0)
        assert confirm.locator(".gn-btn--tertiary").evaluate(STYLE) == tertiary
        assert confirm.locator(".gn-btn--danger.gn-btn--solid").evaluate(STYLE) == destructive
        close = confirm.get_by_role("button", name="Cerrar", exact=True)
        assert close.evaluate("el => getComputedStyle(el).borderRadius") == "32px"
        assert confirm.evaluate("el => el.scrollWidth <= el.clientWidth")
        close.click()
        assert confirm.is_hidden()

        page.locator(f'[data-gn-modal-open="{product}-form-modal"]').click()
        form = page.locator(f"#{product}-form-modal")
        assert form.is_visible()
        page.mouse.move(0, 0)
        assert form.locator(".gn-btn--primary").evaluate(STYLE) == primary
        assert form.locator(".gn-btn--tertiary").evaluate(STYLE) == tertiary
        assert form.evaluate("el => el.scrollWidth <= el.clientWidth")
        page.keyboard.press("Escape")
        assert form.is_hidden()


def test_colores_del_producto_y_radio_del_toast(open_catalog):
    page = open_catalog(390)
    page.add_style_tag(content=":root { --gn-c-brand: #224466; --gn-on-critical: #fff8ee; }")
    outside = page.locator("#acciones [data-kit-product]:visible")
    assert outside.locator(".gn-btn--primary").first.evaluate(
        "el => getComputedStyle(el).backgroundColor"
    ) == "rgb(34, 68, 102)"
    outside.get_by_role("button", name="Eliminar", exact=True).click()
    confirm = page.locator("#gelectric-confirm")
    assert confirm.locator(".gn-btn--solid").evaluate("el => getComputedStyle(el).color") == "rgb(255, 248, 238)"
    page.keyboard.press("Escape")
    page.evaluate('GN.toast("Ejemplo", { kind: "good" })')
    toast = page.locator(".gn-toast")
    assert toast.evaluate("el => getComputedStyle(el).borderRadius") == "9px"
    assert toast.get_by_role("button", name="Cerrar notificación").evaluate("el => el.className") == "gn-alert__close"
