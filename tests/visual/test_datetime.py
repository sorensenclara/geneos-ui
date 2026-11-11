"""Selectores de fecha y hora (0.5.0) en el navegador, sobre el catálogo construido.

Comprueba con Chromium real: mejora progresiva (sin JS queda el control nativo),
teclado (Alt+↓, flechas, Enter, Escape), foco, ARIA, panel arriba/abajo,
hoja inferior en el celular, validación y modo oscuro.
Se saltea si no está Playwright o falta dist/ui-kit.html (python tools/build_catalog.py).
"""
from pathlib import Path

import pytest

sync_api = pytest.importorskip("playwright.sync_api")
DIST = Path(__file__).resolve().parents[2] / "dist" / "ui-kit.html"
pytestmark = pytest.mark.skipif(not DIST.exists(), reason="falta dist/ui-kit.html")

DT = "#gelectric-dt-cuando"
BTN = DT + " ~ .gn-datetime__btn"
ACTIVE = """() => { let a = document.activeElement; while (a && a.shadowRoot && a.shadowRoot.activeElement) a = a.shadowRoot.activeElement;
  return { tag: a.tagName, label: a.getAttribute('aria-label'), cls: a.className, pressed: a.getAttribute('aria-pressed') }; }"""


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as pw:
        try:
            b = pw.chromium.launch()
        except Exception as exc:  # sin Chromium instalado
            pytest.skip(f"Chromium no disponible: {exc}")
        yield b
        b.close()


def open_page(browser, width=1280, height=900, js=True, storage=None, **ctx_kw):
    ctx = browser.new_context(viewport={"width": width, "height": height}, java_script_enabled=js, **ctx_kw)
    if storage:
        ctx.add_init_script("(s => { for (const k in s) localStorage.setItem(k, s[k]); })(%s)" % __import__("json").dumps(storage))
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(DIST.as_uri() + "#fecha-hora")
    if js:
        page.wait_for_function(f"() => document.querySelector('{DT}').type === 'text'")
    return page, errors


def wait_day(page, label):
    page.wait_for_function(f"() => ({ACTIVE})().label === {label!r}")


def test_sin_javascript_quedan_los_controles_nativos_con_iso(browser):
    page, _ = open_page(browser, js=False)
    got = page.evaluate("""() => ['cuando', 'fecha', 'hora', 'acotada'].map(n => {
        const i = document.getElementById('gelectric-dt-' + n); return [i.type, i.value, i.name, i.min]; })""")
    assert got[0][:3] == ["datetime-local", "2026-11-12T09:30", "cuando"]
    assert got[1][:2] == ["date", "2026-10-28"]
    assert got[2][:2] == ["time", "08:00"]
    assert got[3][0] == "date" and got[3][3]  # min nativo
    assert page.locator(".gn-datetime__btn").count() == 0
    page.context.close()


def test_con_javascript_un_solo_input_con_formato_visible(browser):
    page, errors = open_page(browser)
    wrap = page.locator(DT).locator("xpath=..")
    assert wrap.locator("input").count() == 1  # sin campos ocultos duplicados
    assert page.input_value(DT) == "12/11/2026 09:30"
    assert page.input_value("#gelectric-dt-fecha") == "28/10/2026"
    assert page.input_value("#gelectric-dt-hora") == "08:00"
    assert page.get_attribute(DT, "name") == "cuando"
    btn = page.locator(BTN)
    assert btn.get_attribute("aria-label") == "Elegir fecha y hora"
    assert btn.get_attribute("aria-haspopup") == "dialog" and btn.get_attribute("aria-expanded") == "false"
    # el formato se anuncia y el error del servidor sigue vinculado
    assert "Formato" in page.evaluate(f"() => document.querySelector('{DT}').getAttribute('aria-describedby').split(' ').map(id => document.getElementById(id).textContent).join(' ')")
    assert page.get_attribute("#gelectric-dt-con_error", "aria-describedby").startswith("gelectric-dt-con_error-e")
    assert page.input_value("#gelectric-dt-con_error") == "31/02/2026 10:00"  # se conserva lo escrito
    assert page.locator("#gelectric-dt-deshabilitado ~ .gn-datetime__btn").is_disabled()
    assert not errors
    page.context.close()


def test_teclado_completo_y_escape_devuelve_el_foco(browser):
    page, errors = open_page(browser)
    page.focus(DT)
    page.keyboard.press("Alt+ArrowDown")
    panel = page.locator("#" + page.get_attribute(BTN, "aria-controls"))
    assert panel.is_visible() and panel.get_attribute("role") == "dialog"
    assert page.get_attribute(BTN, "aria-expanded") == "true"
    wait_day(page, "12 de noviembre")
    assert page.evaluate(ACTIVE)["pressed"] == "true"
    assert panel.locator(".gn-calendar__heading").inner_text() == "Noviembre de 2026"
    page.keyboard.press("ArrowRight")
    wait_day(page, "13 de noviembre")
    page.keyboard.press("Enter")
    page.wait_for_function(f"() => document.querySelector('{DT}').value === '13/11/2026 09:30'")
    page.keyboard.press("PageDown")  # mes siguiente
    wait_day(page, "13 de diciembre")
    assert panel.locator(".gn-calendar__heading").inner_text() == "Diciembre de 2026"
    page.keyboard.press("Escape")
    assert panel.is_hidden()
    a = page.evaluate(ACTIVE)
    assert "gn-datetime__btn" in a["cls"]
    assert page.get_attribute(BTN, "aria-expanded") == "false"
    # al reabrir vuelve al mes del valor
    page.keyboard.press("Enter")
    wait_day(page, "13 de noviembre")
    page.keyboard.press("Escape")
    assert not errors
    page.context.close()


def test_hora_compacta_escritura_teclado_y_tab_fuera_cierra(browser):
    page, errors = open_page(browser)
    page.click(BTN)
    panel = page.locator("#" + page.get_attribute(BTN, "aria-controls"))
    hora = panel.get_by_role("spinbutton", name="Hora", exact=True)
    minutos = panel.get_by_role("spinbutton", name="Minutos")
    assert hora.get_attribute("aria-valuenow") == "9" and hora.get_attribute("aria-valuemax") == "23"
    assert hora.get_attribute("inputmode") == "numeric"
    # escritura directa: dos cifras confirman la hora y pasan solas a los minutos
    hora.focus()
    page.keyboard.type("18")
    assert page.evaluate("() => document.activeElement.getAttribute('aria-label')") == "Minutos"
    page.keyboard.type("45")
    assert page.input_value(DT) == "12/11/2026 18:45"
    # flechas: minutos de a 5 (paso del widget), Mayús de a 1; la hora da la vuelta a 00
    page.keyboard.press("ArrowUp")
    assert page.input_value(DT) == "12/11/2026 18:50"
    page.keyboard.press("Shift+ArrowDown")
    assert page.input_value(DT) == "12/11/2026 18:49"
    hora.focus()
    for _ in range(6):
        page.keyboard.press("ArrowUp")
    assert hora.input_value() == "00" and page.input_value(DT) == "12/11/2026 00:49"
    page.keyboard.press("End")
    assert hora.input_value() == "23"
    # fuera de rango (24 horas): se marca con un mensaje, no se corrige solo y el campo no cambia
    width = panel.bounding_box()["width"]
    hora.fill("27")
    error = panel.locator(".gn-time__error")
    assert abs(panel.bounding_box()["width"] - width) < 1  # el mensaje no ensancha el panel
    assert hora.get_attribute("aria-invalid") == "true"
    assert error.inner_text() == "La hora tiene que estar entre 00 y 23."
    minutos.focus()
    assert hora.input_value() == "27" and hora.get_attribute("aria-invalid") == "true"  # sigue a la vista
    assert error.get_attribute("id") in hora.get_attribute("aria-describedby")
    assert page.input_value(DT) == "12/11/2026 23:49"
    # «Listo» no cierra con la hora mal: lleva el foco al campo a corregir
    panel.get_by_role("button", name="Listo").click()
    assert panel.is_visible() and page.evaluate("() => document.activeElement.getAttribute('aria-label')") == "Hora"
    # vacío: también se avisa
    hora.fill("")
    minutos.focus()
    assert error.inner_text() == "Completá la hora (00 a 23)."
    # al corregirlo desaparece el mensaje
    hora.focus()
    page.keyboard.type("23")
    assert hora.get_attribute("aria-invalid") is None and error.is_hidden()
    # una cifra que no admite segunda (9) se confirma sola como 09
    hora.focus()
    page.keyboard.type("9")
    assert page.input_value(DT) == "12/11/2026 09:49"
    # flechas para mouse/touch, sin entrar en el orden de tabulación
    panel.locator('.gn-time__step[aria-label="Subir la hora"]').click()
    assert page.input_value(DT) == "12/11/2026 10:49"
    assert panel.locator(".gn-time__step").first.get_attribute("tabindex") == "-1"
    panel.get_by_role("button", name="Listo").click()
    assert panel.is_hidden()
    # Tab desde el último control del panel sale y lo cierra
    page.click(BTN)
    panel.get_by_role("button", name="Listo").focus()
    page.keyboard.press("Tab")
    assert panel.is_hidden()
    assert not errors
    page.context.close()


def test_minutos_invalidos_y_hora_sola(browser):
    page, _ = open_page(browser)
    sel = "#gelectric-dt-hora"
    page.click(sel + " ~ .gn-datetime__btn")
    panel = page.locator("#" + page.get_attribute(sel + " ~ .gn-datetime__btn", "aria-controls"))
    minutos = panel.get_by_role("spinbutton", name="Minutos")
    minutos.fill("75")
    assert panel.locator(".gn-time__error").inner_text() == "Los minutos tienen que estar entre 00 y 59."
    assert page.input_value(sel) == "08:00"  # el campo principal no cambia
    page.keyboard.press("ArrowUp")  # ajustar con el teclado parte del último válido y lo corrige
    assert page.input_value(sel) == "08:15" and panel.locator(".gn-time__error").is_hidden()
    page.context.close()


def test_panel_acompana_al_campo_al_desplazar(browser):
    page, _ = open_page(browser, width=1280, height=900)
    assert abs(page.evaluate(SETTLE, [DT, 350]) - 350) <= 1
    click_real(page, BTN)
    page.wait_for_timeout(150)
    gap = f"""() => {{ const p = document.getElementById(document.querySelector('{BTN}').getAttribute('aria-controls')).getBoundingClientRect();
        const f = document.querySelector('{DT}').getBoundingClientRect(); return [Math.round(p.top - f.bottom), Math.round(p.left - f.left)]; }}"""
    before = page.evaluate(gap)
    page.mouse.move(1270, 300)
    for dy in (120, -60, 200, -260):
        target = page.evaluate("() => Math.round(scrollY)") + dy
        page.mouse.wheel(0, dy)
        page.wait_for_function("target => Math.round(scrollY) === target", arg=target)
        page.wait_for_function(f"expected => JSON.stringify(({gap})()) === JSON.stringify(expected)", arg=before)
        assert page.evaluate(gap) == before  # sigue pegado al campo, del mismo lado
    # la página no se desplaza sola mientras el usuario scrollea (sin saltos)
    y1 = page.evaluate("() => scrollY")
    page.wait_for_timeout(200)
    assert page.evaluate("() => scrollY") == y1
    page.context.close()


def test_selector_de_hora_solo(browser):
    page, _ = open_page(browser)
    sel = "#gelectric-dt-hora"
    page.click(sel + " ~ .gn-datetime__btn")
    panel = page.locator("#" + page.get_attribute(sel + " ~ .gn-datetime__btn", "aria-controls"))
    assert page.evaluate("() => document.activeElement.getAttribute('aria-label')") == "Hora"
    page.keyboard.type("0730")
    assert page.input_value(sel) == "07:30"
    page.keyboard.press("ArrowUp")  # paso de 15 en este ejemplo
    assert page.input_value(sel) == "07:45"
    page.keyboard.press("Escape")
    assert panel.is_hidden()
    page.context.close()


def test_selector_de_fecha_cierra_al_elegir_y_respeta_min_max(browser):
    page, _ = open_page(browser)
    sel = "#gelectric-dt-acotada"
    btn = page.locator(sel + " ~ .gn-datetime__btn")
    btn.click()
    disabled = page.evaluate("""(sel) => {
        const cal = document.getElementById(document.querySelector(sel + ' ~ .gn-datetime__btn').getAttribute('aria-controls')).querySelector('calendar-month');
        return [...cal.shadowRoot.querySelectorAll('button')].filter(b => b.disabled).length; }""", sel)
    assert disabled > 0  # los días fuera de rango no se pueden elegir
    page.keyboard.press("Enter")  # hoy (el día enfocado)
    page.wait_for_function(f"() => document.querySelector('{sel}').value !== ''")
    assert btn.get_attribute("aria-expanded") == "false"
    assert "gn-datetime__btn" in page.evaluate(ACTIVE)["cls"]
    # fuera de rango a mano
    page.fill(sel, "01/01/2020")
    page.keyboard.press("Tab")
    err = page.locator(sel + "-wrap-err, .gn-datetime__error:visible").first
    assert "Elegí una fecha desde" in err.inner_text()
    assert page.get_attribute(sel, "aria-invalid") == "true"
    page.context.close()


def test_texto_escrito_se_normaliza_o_marca_error(browser):
    page, _ = open_page(browser)
    page.fill(DT, "5/1/27 9")
    page.keyboard.press("Tab")
    assert page.input_value(DT) == "05/01/2027 09:00"
    page.fill(DT, "30/02/2027 10:00")
    page.keyboard.press("Tab")
    assert page.get_attribute(DT, "aria-invalid") == "true"
    assert page.evaluate(f"() => document.querySelector('{DT}').validationMessage") == "Ingresá una fecha y hora válidas"
    page.fill(DT, "28/02/2027 10:00")
    page.keyboard.press("Tab")
    assert page.get_attribute(DT, "aria-invalid") is None
    assert page.evaluate(f"() => GN.datetime.value(document.querySelector('{DT}'))") == "2027-02-28T10:00"
    page.context.close()


def test_panel_se_abre_hacia_arriba_si_la_pagina_no_puede_bajar(browser):
    page, _ = open_page(browser, height=700)
    # el campo en una barra fija abajo: desplazar no le hace lugar, se abre arriba
    page.evaluate(f"""() => {{ const box = document.createElement('div');
        box.style.cssText = 'position:fixed;left:24px;bottom:24px;width:320px;z-index:5';
        box.appendChild(document.querySelector('{DT}').closest('.gn-field')); document.body.appendChild(box); }}""")
    page.click(BTN)
    box = page.evaluate(f"""() => {{ const p = document.getElementById(document.querySelector('{BTN}').getAttribute('aria-controls'));
        const i = document.querySelector('{DT}').getBoundingClientRect(), r = p.getBoundingClientRect();
        const label = document.querySelector('{DT}').closest('.gn-field').querySelector('label').getBoundingClientRect();
        return {{ above: r.bottom <= i.top, inside: r.top >= 0 && r.bottom <= innerHeight, label: r.bottom <= label.top }}; }}""")
    assert box == {"above": True, "inside": True, "label": True}  # no tapa la etiqueta
    page.context.close()


SHEET_METRICS = """(id) => { const p = document.getElementById(id), m = p.querySelector('calendar-month');
  const days = [...m.shadowRoot.querySelectorAll('button')].map(b => b.getBoundingClientRect());
  const r = p.getBoundingClientRect(), foot = p.querySelector('.gn-popover__foot').getBoundingClientRect();
  const time = p.querySelector('.gn-time').getBoundingClientRect();
  return { top: r.top, bottom: r.bottom, left: r.left, width: r.width, dayH: Math.max(...days.map(d => d.height)),
    footBottom: foot.bottom, timeBottom: time.bottom, vh: innerHeight, scrollW: document.documentElement.scrollWidth, scrollH: p.scrollHeight, clientH: p.clientHeight }; }"""


@pytest.mark.parametrize("size", [(375, 667), (390, 844), (320, 568)])
def test_celular_hoja_inferior_compacta(browser, size):
    w, h = size
    page, errors = open_page(browser, width=w, height=h, is_mobile=True, has_touch=True)
    # a 320 px el propio catálogo ya desborda unos píxeles: se mide contra la página sin el panel
    base_w = page.evaluate("() => document.documentElement.scrollWidth")
    page.locator(BTN).tap()
    pid = page.get_attribute(BTN, "aria-controls")
    panel = page.locator("#" + pid)
    page.wait_for_timeout(400)  # fin de la animación de entrada
    m = page.evaluate(SHEET_METRICS, pid)
    assert "gn-popover--sheet" in panel.get_attribute("class")
    assert m["left"] == 0 and abs(m["width"] - base_w) < 1 and abs(m["bottom"] - m["vh"]) < 2
    assert m["dayH"] <= 37  # semanas compactas
    assert m["scrollW"] <= base_w  # el panel no agrega desplazamiento horizontal
    if h >= 667:
        assert m["scrollH"] <= m["clientH"] + 1  # entra entera, sin scroll interno
        assert m["top"] > h * 0.25  # no ocupa más altura de la necesaria
    # hora y acciones siempre visibles (el pie queda fijo abajo)
    assert m["footBottom"] <= m["vh"] + 1
    assert panel.get_by_role("button", name="Listo").is_visible()
    # el tap fuera cierra
    page.mouse.click(w // 2, 20)
    assert panel.is_hidden()
    assert not errors
    page.context.close()


def test_escritorio_junto_al_campo_y_sin_recortes(browser):
    page, _ = open_page(browser, width=1280, height=900)
    assert abs(page.evaluate(SETTLE, [DT, 120]) - 120) <= 1
    click_real(page, BTN)
    pos = page.evaluate(f"""() => {{ const p = document.getElementById(document.querySelector('{BTN}').getAttribute('aria-controls')).getBoundingClientRect();
        const f = document.querySelector('{DT}').closest('.gn-datetime').getBoundingClientRect();
        return {{ gap: p.top - f.bottom, left: p.left - f.left, inside: p.bottom <= innerHeight && p.top >= 0 }}; }}""")
    assert 0 <= pos["gap"] <= 8 and pos["left"] == 0 and pos["inside"]
    page.keyboard.press("Escape")
    # campo pegado al borde derecho: se alinea con el borde derecho del campo
    page.set_viewport_size({"width": 700, "height": 900})
    sel = "#gelectric-dt-acotada"
    page.evaluate(f"() => document.querySelector('{sel}').scrollIntoView({{block: 'center'}})")
    page.click(sel + " ~ .gn-datetime__btn")
    r = page.evaluate(f"""() => {{ const p = document.getElementById(document.querySelector('{sel} ~ .gn-datetime__btn').getAttribute('aria-controls')).getBoundingClientRect();
        return [p.left >= 0, p.right <= document.documentElement.clientWidth]; }}""")
    assert r == [True, True]
    page.context.close()


# ---------------------------------------------------------------- ubicación en escritorio
# Mide el panel abierto: entero en la ventana (debajo de la barra superior), sin
# scroll interno, «Ahora» y «Listo» visibles y sin tapar el campo ni su etiqueta.
FIT = """(sel) => {
  const btn = document.querySelector(sel + ' ~ .gn-datetime__btn');
  const p = document.getElementById(btn.getAttribute('aria-controls'));
  const r = p.getBoundingClientRect(), f = document.querySelector(sel).getBoundingClientRect();
  const label = document.querySelector(sel).closest('.gn-field').querySelector('label').getBoundingClientRect();
  const bar = document.querySelector('.gn-topbar').getBoundingClientRect().bottom;
  const buttons = [...p.querySelectorAll('.gn-popover__foot button')].map(b => b.getBoundingClientRect());
  const overlaps = (a, b) => a.left < b.right && b.left < a.right && a.top < b.bottom && b.top < a.bottom;
  return {
    mode: p.getAttribute('data-gn-place'),
    inside: r.top >= bar - 1 && r.bottom <= innerHeight + 0.5 && r.left >= 0 && r.right <= document.documentElement.clientWidth,
    noInnerScroll: p.scrollHeight <= p.clientHeight + 1,
    buttonsVisible: buttons.length === 2 && buttons.every(b => b.top >= r.top && b.bottom <= Math.min(r.bottom, innerHeight)),
    coversField: overlaps(r, f) || overlaps(r, label),
  };
}"""
OK = {"inside": True, "noInnerScroll": True, "buttonsVisible": True, "coversField": False}


def open_at(page, sel, block):
    page.evaluate(f"() => document.querySelector('{sel}').scrollIntoView({{block: '{block}'}})")
    page.wait_for_timeout(80)
    page.click(sel + " ~ .gn-datetime__btn")
    page.wait_for_timeout(250)  # el calendario termina de dibujarse y el panel se reubica
    return page.evaluate(FIT, sel)


@pytest.mark.parametrize("size", [(1536, 960), (1536, 830), (1280, 720)])
@pytest.mark.parametrize("block", ["start", "center", "end"])
def test_escritorio_entero_y_con_botones_visibles(browser, size, block):
    """Regresión: el panel quedaba con scroll interno y «Listo» fuera de la ventana."""
    page, errors = open_page(browser, width=size[0], height=size[1])
    for sel in (DT, "#gelectric-dt-hora", "#gelectric-dt-acotada"):
        got = open_at(page, sel, block)
        assert {k: got[k] for k in OK} == OK, (sel, got)
        page.keyboard.press("Escape")
    assert not errors
    page.context.close()


# Ubica el campo a `top` px del borde superior y espera a que no se mueva (dos cuadros seguidos en
# el mismo lugar). Con un solo scrollBy, test_abajo_si_entra falló de forma intermitente en la
# suite completa (nunca aislado): ver docs/pruebas.md.
SETTLE = """async ([sel, top]) => {
  const frame = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  await document.fonts.ready;
  let last = null;
  for (let i = 0; i < 10; i++) {
    const r = document.querySelector(sel).getBoundingClientRect();
    if (Math.abs(r.top - top) > 0.5) window.scrollBy(0, r.top - top);
    await frame();
    const now = Math.round(document.querySelector(sel).getBoundingClientRect().top);
    if (now === last && Math.abs(now - top) <= 1) return now;
    last = now;
  }
  return last;
}"""
STATE = """(sel) => { const btn = document.querySelector(sel + ' ~ .gn-datetime__btn');
  const p = document.getElementById(btn.getAttribute('aria-controls'));
  return { campo: Math.round(document.querySelector(sel).getBoundingClientRect().top), scrollY: Math.round(scrollY),
           panel: p.offsetHeight, alto: innerHeight }; }"""


def click_real(page, sel):
    """Clic real del mouse en el centro del elemento, sin el desplazamiento automático de Playwright.

    Solo para las pruebas de ubicación, que necesitan el campo quieto donde se lo dejó: page.click()
    puede volver a desplazar la página antes del clic y el panel se abriría, con razón, del otro lado
    (ver docs/pruebas.md). Abrir el panel con page.click() y con el teclado se prueba en las demás pruebas.
    """
    box = page.locator(sel).bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)


def test_abajo_si_entra(browser):
    page, _ = open_page(browser, width=1536, height=960)
    assert abs(page.evaluate(SETTLE, [DT, 120]) - 120) <= 1
    click_real(page, BTN)
    page.wait_for_timeout(250)
    got = page.evaluate(FIT, DT)
    assert got["mode"] == "below" and {k: got[k] for k in OK} == OK, (got, page.evaluate(STATE, DT))
    page.context.close()


def test_arriba_si_abajo_no_entra(browser):
    page, _ = open_page(browser, width=1536, height=960)
    assert abs(page.evaluate(SETTLE, [DT, 960 - 120]) - (960 - 120)) <= 1
    y = page.evaluate("() => scrollY")
    click_real(page, BTN)
    page.wait_for_timeout(250)
    got = page.evaluate(FIT, DT)
    assert got["mode"] == "above" and {k: got[k] for k in OK} == OK, (got, page.evaluate(STATE, DT))
    assert page.evaluate("() => scrollY") == y  # entraba arriba: no hacía falta mover la página
    page.context.close()


def test_sin_lugar_arriba_ni_abajo_queda_entero_al_costado(browser):
    """El caso de la captura: campo en el medio de una ventana baja, sin poder desplazar."""
    page, _ = open_page(browser, width=1536, height=600)
    page.evaluate(f"""() => {{ const box = document.createElement('div');
        box.style.cssText = 'position:fixed;left:300px;top:calc(50% - 40px);width:320px;z-index:5;background:var(--gn-surface)';
        box.appendChild(document.querySelector('{DT}').closest('.gn-field')); document.body.appendChild(box); }}""")
    page.click(BTN)
    page.wait_for_timeout(250)
    got = page.evaluate(FIT, DT)
    assert got["mode"] == "side" and {k: got[k] for k in OK} == OK
    page.context.close()


def test_contenedor_con_overflow_y_transform_no_lo_recorta(browser):
    page, _ = open_page(browser, width=1536, height=960)
    # un contenedor bajo, con overflow: hidden y transform (que cambia la referencia de position: fixed)
    page.evaluate(f"""() => {{ const f = document.querySelector('{DT}').closest('.gn-field');
        const box = document.createElement('div'); box.style.cssText = 'overflow:hidden;height:90px;transform:translateZ(0)';
        f.parentNode.insertBefore(box, f); box.appendChild(f); }}""")
    got = open_at(page, DT, "center")
    assert {k: got[k] for k in OK} == OK
    panel = page.locator("#" + page.get_attribute(BTN, "aria-controls"))
    assert page.evaluate("(id) => document.getElementById(id).parentElement === document.body", panel.get_attribute("id"))
    panel.get_by_role("button", name="Listo").click()  # se puede usar: no quedó recortado
    assert panel.is_hidden()
    # al cerrarse vuelve a su lugar en el formulario
    assert page.evaluate(f"(id) => document.querySelector('{DT}').closest('.gn-datetime').contains(document.getElementById(id))", panel.get_attribute("id"))
    page.context.close()


def test_se_recalcula_al_cambiar_el_tamano_de_la_ventana(browser):
    page, _ = open_page(browser, width=1536, height=960)
    open_at(page, DT, "center")
    for size in ((1536, 700), (1100, 640), (1536, 960)):
        page.set_viewport_size({"width": size[0], "height": size[1]})
        page.wait_for_timeout(200)
        got = page.evaluate(FIT, DT)
        assert got["inside"] and got["buttonsVisible"], (size, got)
    page.context.close()


def test_ventana_mas_baja_que_el_panel_scroll_interno_con_botones_fijos(browser):
    page, _ = open_page(browser, width=1536, height=420)
    page.click(BTN)
    page.wait_for_timeout(250)
    got = page.evaluate(FIT, DT)
    assert got["mode"] == "clamped" and got["inside"] and got["buttonsVisible"]
    page.context.close()


def test_modo_oscuro_usa_tokens(browser):
    page, _ = open_page(browser, storage={"gn-theme": "dark"})
    page.click(BTN)
    colors = page.evaluate(f"""() => {{ const p = document.getElementById(document.querySelector('{BTN}').getAttribute('aria-controls'));
        const s = getComputedStyle(document.documentElement);
        return [getComputedStyle(p).backgroundColor, s.getPropertyValue('--gn-elevated').trim()]; }}""")
    assert colors[0] != "rgb(255, 255, 255)"
    page.context.close()


def test_calendario_suelto_en_espanol(browser):
    page, _ = open_page(browser)
    heads = page.evaluate("""() => { const m = document.querySelector('#fecha-hora [data-kit-product="gelectric"] calendar-date[data-gn-calendar] calendar-month');
        return [...m.shadowRoot.querySelectorAll('th span[aria-hidden]')].map(s => s.textContent).join(''); }""")
    assert heads == "LMMJVSD"
    page.context.close()


def test_popover_generico(browser):
    page, _ = open_page(browser)
    btn = page.locator('[data-gn-popover="gelectric-pop"]')
    btn.click()
    pop = page.locator("#gelectric-pop")
    assert pop.is_visible() and btn.get_attribute("aria-expanded") == "true"
    page.keyboard.press("Escape")
    assert pop.is_hidden() and page.evaluate("() => document.activeElement.dataset.gnPopover") == "gelectric-pop"
    page.context.close()
