"""Comportamiento en el navegador sobre el catálogo construido (dist/ui-kit.html).

Se saltea si no está Playwright o si no se construyó el catálogo
(``python tools/build_catalog.py``). En CI lo corre el job de capturas.
"""
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")
DIST = Path(__file__).resolve().parents[2] / "dist" / "ui-kit.html"
pytestmark = pytest.mark.skipif(not DIST.exists(), reason="falta dist/ui-kit.html")


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as pw:
        try:
            b = pw.chromium.launch()
        except Exception as exc:  # sin Chromium instalado
            pytest.skip(f"Chromium no disponible: {exc}")
        yield b
        b.close()


def open_page(browser, storage=None, width=1440):
    ctx = browser.new_context(viewport={"width": width, "height": 900})
    if storage:
        ctx.add_init_script("(s => { for (const k in s) localStorage.setItem(k, s[k]); })(%s)" % __import__("json").dumps(storage))
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(DIST.as_uri())
    page.wait_for_function("() => !!(window.GN && window.GN.setNav)")
    return page, errors


def expanded(page, product):
    return page.evaluate(f"() => !document.getElementById('gn-sidebar-{product}').classList.contains('is-collapsed')")


def test_clave_vieja_de_gelectric_se_migra(browser):
    page, errors = open_page(browser, {"geletric-sidebar-pinned": "1"})
    page.evaluate("() => GN.setNav('vertical')")
    assert expanded(page, "gelectric")  # sin la clave vieja arrancaría contraído
    assert page.evaluate("() => localStorage.getItem('gn-sidebar-expanded:gelectric')") == "1"
    assert not errors
    page.context.close()


def test_sin_clave_vieja_gelectric_arranca_contraido(browser):
    page, _ = open_page(browser)
    page.evaluate("() => GN.setNav('vertical')")
    assert not expanded(page, "gelectric")
    page.context.close()


def test_preferencias_se_guardan_con_las_mismas_claves(browser):
    page, errors = open_page(browser)
    page.click("[data-gn-prefs-toggle]")
    page.click('#gn-prefs-panel [data-gn-theme-value="dark"]')
    page.click('#gn-prefs-panel [data-gn-nav-value="horizontal"]')
    assert page.evaluate("() => [localStorage.getItem('gn-theme'), localStorage.getItem('gn-nav')]") == ["dark", "horizontal"]
    page.reload()
    page.wait_for_function("() => !!(window.GN && window.GN.setNav)")
    assert page.evaluate("() => [document.documentElement.dataset.gnTheme, document.documentElement.dataset.gnNav]") == ["dark", "horizontal"]
    assert not errors
    page.context.close()
