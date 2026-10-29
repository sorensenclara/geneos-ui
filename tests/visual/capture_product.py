"""Capturas de una página de producto construida (no del catálogo).

    python tests/visual/capture_product.py <pagina.html> <carpeta> [prefijo]

Toma la página en claro y oscuro, con menú vertical y horizontal, el panel de
preferencias abierto, el sidebar contraído y el celular con el menú abierto.
Se usa con el producto de prueba GEFLOTA (sandbox/geflota).
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

FREEZE = "*{transition:none!important;animation:none!important;caret-color:transparent!important}"


def shots(html, out, prefix="pagina"):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    url = Path(html).resolve().as_uri()
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        def page(w=1440, h=900):
            pg = browser.new_context(viewport={"width": w, "height": h}).new_page()
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url)
            pg.wait_for_function("() => !!(window.GN && window.GN.setNav)")
            pg.add_style_tag(content=FREEZE)
            return pg

        pg = page()
        for theme in ("light", "dark"):
            for nav in ("vertical", "horizontal"):
                pg.evaluate("([t, n]) => { GN.setTheme(t); GN.setNav(n); window.dispatchEvent(new Event('resize')); }", [theme, nav])
                pg.wait_for_timeout(250)
                pg.screenshot(path=out / f"{prefix}-{theme}-{nav}.png")
                pg.click("[data-gn-prefs-toggle]")
                pg.screenshot(path=out / f"{prefix}-{theme}-{nav}-preferencias.png")
                pg.keyboard.press("Escape")
        pg.evaluate("() => { GN.setTheme('light'); GN.setNav('vertical'); GN.sidebar && GN.sidebar.collapse(); }")
        pg.wait_for_timeout(300)
        pg.screenshot(path=out / f"{prefix}-contraido.png")
        pg.context.close()
        pg = page(390, 844)
        pg.screenshot(path=out / f"{prefix}-movil.png")
        pg.click(".gn-topbar__menu")
        pg.wait_for_timeout(300)
        pg.screenshot(path=out / f"{prefix}-movil-menu.png")
        pg.context.close()
        browser.close()
    return errors


if __name__ == "__main__":
    errs = shots(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "pagina")
    print(sys.argv[2], "errores JS:", errs or "ninguno")
