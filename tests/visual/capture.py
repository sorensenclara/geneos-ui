"""Capturas del catálogo construido (dist/ui-kit.html) para comparar versiones.

    python tests/visual/capture.py <ui-kit.html> <carpeta de salida>

Se corre igual sobre el catálogo de la versión de referencia y sobre el
actual; ``compare.py`` mide la diferencia. Las marcas «Componente» / «HTML de
referencia» del catálogo se ocultan para que no cuenten como diferencia.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PRODUCTS = ("gelectric", "gema", "geagro-cereales", "geagro-vid")
FREEZE = "*{transition:none!important;animation:none!important;caret-color:transparent!important}.kit-kind{display:none!important}"


def shots(html, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    url = Path(html).resolve().as_uri()
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        def page(w=1440, h=900):
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
            pg = ctx.new_page()
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url)
            pg.wait_for_function("window.GN && GN.setNav")
            pg.add_style_tag(content=FREEZE)
            return pg

        def setup(pg, product, theme="light", nav=None):
            pg.click(f'[data-kit-switch="{product}"]')
            pg.evaluate("([t, n]) => { GN.setTheme(t); if (n) GN.setNav(n); }", [theme, nav])
            pg.evaluate("() => { window.dispatchEvent(new Event('resize')); window.scrollTo(0, 0); }")
            pg.wait_for_timeout(250)

        pg = page()
        for product in PRODUCTS:
            for theme in ("light", "dark"):
                for nav in ("horizontal", "vertical"):
                    setup(pg, product, theme, nav)
                    pg.screenshot(path=out / f"{product}-{theme}-{nav}.png")
        # sidebar contraído y panel de preferencias abierto
        setup(pg, "gelectric", "light", "vertical")
        pg.evaluate("() => GN.sidebar && GN.sidebar.collapse()")
        pg.wait_for_timeout(300)
        pg.screenshot(path=out / "gelectric-contraido.png")
        pg.evaluate("() => GN.sidebar && GN.sidebar.expand()")
        pg.wait_for_timeout(300)
        pg.click("[data-gn-prefs-toggle]")
        pg.screenshot(path=out / "gelectric-preferencias.png")
        pg.keyboard.press("Escape")
        setup(pg, "gema", "dark", "horizontal")
        pg.click("[data-gn-prefs-toggle]")
        pg.screenshot(path=out / "gema-preferencias-oscuro.png")
        pg.keyboard.press("Escape")
        # secciones de componentes
        setup(pg, "gema", "light", "vertical")
        for sec in ("identidad", "iconografia", "navegacion", "acciones", "formularios", "datos", "dashboard", "estados"):
            el = pg.query_selector(f"#{sec}")
            if el:
                el.scroll_into_view_if_needed()
                pg.wait_for_timeout(100)
                pg.screenshot(path=out / f"seccion-{sec}.png")
        pg.context.close()

        # desplegables y «Más»
        for w in (1280, 1024):
            pg = page(w, 760)
            setup(pg, "gelectric", "light", "horizontal")
            pg.evaluate("() => { const t = [...document.querySelectorAll('#gn-sidebar-gelectric [data-gn-group-toggle]')].filter(e => e.offsetParent).pop(); t.click(); }")
            pg.wait_for_timeout(150)
            pg.screenshot(path=out / f"gelectric-mas-{w}.png")
            pg.context.close()

        # celular: cerrado y con el menú abierto
        pg = page(390, 844)
        setup(pg, "geagro-vid", "light")
        pg.screenshot(path=out / "movil-cerrado.png")
        pg.click(".gn-topbar__menu")
        pg.wait_for_timeout(300)
        pg.screenshot(path=out / "movil-menu.png")
        pg.context.close()
        browser.close()
    (out / "errores.txt").write_text("\n".join(errors), encoding="utf-8")
    return errors


if __name__ == "__main__":
    errs = shots(sys.argv[1], sys.argv[2])
    print(sys.argv[2], "errores JS:", errs or "ninguno")
