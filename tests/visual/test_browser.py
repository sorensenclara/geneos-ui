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


TAB_OVERLAP = r"""
() => {
  const tab = document.querySelector('[data-gn-prefs-toggle]');
  const sel = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  const out = [], step = Math.max(200, innerHeight - 100);
  for (let y = 0; y <= document.documentElement.scrollHeight; y += step) {
    window.scrollTo(0, y);
    const t = tab.getBoundingClientRect();
    document.querySelectorAll(sel).forEach(el => {
      if (el.closest('[data-gn-prefs]')) return;
      const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
      if (Math.min(r.right, t.right) > Math.max(r.left, t.left) && Math.min(r.bottom, t.bottom) > Math.max(r.top, t.top))
        out.push((el.textContent || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30));
    });
  }
  return out;
}"""


@pytest.mark.parametrize("width", [1024, 1280, 1440, 1920])
@pytest.mark.parametrize("layout", ["vertical", "contraido", "horizontal"])
def test_solapa_de_preferencias_no_tapa_controles_en_escritorio(browser, width, layout):
    page, errors = open_page(browser, width=width)
    page.add_style_tag(content="*{transition:none!important}")
    page.evaluate("n => { GN.setNav(n === 'horizontal' ? 'horizontal' : 'vertical'); if (n === 'contraido') GN.sidebar.collapse(); }", layout)
    page.wait_for_timeout(100)
    assert page.evaluate(TAB_OVERLAP) == []
    tab = page.locator("[data-gn-prefs-toggle]")
    box = tab.bounding_box()
    assert box["width"] >= 22 and box["height"] >= 44  # WCAG 2.5.8: 44 px de alto y nada más en 24 px a la redonda
    assert tab.get_attribute("aria-label") and tab.get_attribute("aria-expanded") == "false"
    assert not errors
    page.context.close()


def test_solapa_se_maneja_con_teclado(browser):
    page, _ = open_page(browser)
    page.focus("[data-gn-prefs-toggle]")
    page.keyboard.press("Enter")
    assert page.evaluate("() => document.activeElement.id") == "gn-prefs-panel"
    page.keyboard.press("Tab")
    assert page.evaluate("() => document.activeElement.hasAttribute('data-gn-prefs-close')")
    page.keyboard.press("Escape")
    assert page.evaluate("() => document.getElementById('gn-prefs-panel').hidden && document.activeElement.hasAttribute('data-gn-prefs-toggle')")
    page.context.close()
