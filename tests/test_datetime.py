"""0.5.0: widgets de fecha y hora (GnDateTimeInput, GnDateInput, GnTimeInput)."""
import hashlib
import re
from datetime import date, datetime, time
from pathlib import Path

import pytest
from django import forms
from django.contrib.staticfiles import finders
from django.template import Context, Template
from django.utils import timezone

from geneos_ui import __version__
from geneos_ui.widgets import GnDateInput, GnDateTimeInput, GnTimeInput, parse_date, parse_datetime, parse_time

STATIC = Path(__file__).resolve().parents[1] / "geneos_ui" / "static" / "geneos_ui"
CALLY_SHA256 = "4dcba6a3b8ec63b66ff2fbfc6cf47b7dee1eb4896eac89fe7487d82e28e15870"


def naive(dt):
    """Hora local sin zona (el sandbox usa USE_TZ)."""
    return timezone.localtime(dt).replace(tzinfo=None) if timezone.is_aware(dt) else dt


class Agenda(forms.Form):
    inicio = forms.DateTimeField(widget=GnDateTimeInput(default_time="09:00"),
                                 error_messages={"invalid": "Ingresá una fecha y hora válidas"})
    dia = forms.DateField(required=False, widget=GnDateInput(attrs={"min": "2026-01-01"}))
    hora = forms.TimeField(required=False, widget=GnTimeInput(minute_step=15))


# --- lectura ----------------------------------------------------------------
@pytest.mark.parametrize("text, expected", [
    ("05/11/2026", date(2026, 11, 5)), ("5/11/26", date(2026, 11, 5)), ("05-11-2026", date(2026, 11, 5)),
    ("05.11.2026", date(2026, 11, 5)), ("2026-11-05", date(2026, 11, 5)), (" 29/02/2028 ", date(2028, 2, 29)),
])
def test_parse_date_validas(text, expected):
    assert parse_date(text) == expected


@pytest.mark.parametrize("text", ["", "31/02/2026", "29/02/2027", "13/13/2026", "hoy", "2026/11/05", "05/11", None, 20261105])
def test_parse_date_invalidas(text):
    assert parse_date(text) is None


@pytest.mark.parametrize("text, expected", [
    ("09:30", time(9, 30)), ("9:30", time(9, 30)), ("9", time(9, 0)), ("9.30", time(9, 30)), ("0930", time(9, 30)),
    ("9:30 hs", time(9, 30)), ("23:59:59", time(23, 59)), ("9h30", time(9, 30)),
])
def test_parse_time_validas(text, expected):
    assert parse_time(text) == expected


@pytest.mark.parametrize("text", ["24:00", "10:60", "930", "diez", ""])
def test_parse_time_invalidas(text):
    assert parse_time(text) is None


@pytest.mark.parametrize("text, expected", [
    ("05/11/2026 09:30", datetime(2026, 11, 5, 9, 30)), ("5/11/26 9", datetime(2026, 11, 5, 9, 0)),
    ("2026-11-05T09:30", datetime(2026, 11, 5, 9, 30)), ("2026-11-05T09:30:00", datetime(2026, 11, 5, 9, 30)),
    ("05/11/2026, 09:30", datetime(2026, 11, 5, 9, 30)),
])
def test_parse_datetime_validas(text, expected):
    assert parse_datetime(text) == expected


@pytest.mark.parametrize("text", ["05/11/2026", "31/02/2026 10:00", "05/11/2026 25:00", "mañana 10:00"])
def test_parse_datetime_invalidas(text):
    assert parse_datetime(text) is None


# --- render -------------------------------------------------------------------
def test_render_un_solo_input_nativo_con_iso():
    html = str(Agenda(initial={"inicio": datetime(2026, 11, 5, 9, 30), "dia": date(2026, 3, 1), "hora": time(18, 0)}))
    assert len(re.findall(r'name="inicio"', html)) == 1  # sin campos ocultos
    assert 'type="datetime-local" name="inicio" value="2026-11-05T09:30"' in html
    assert 'type="date" name="dia" value="2026-03-01"' in html and 'min="2026-01-01"' in html
    assert 'type="time" name="hora" value="18:00"' in html
    assert 'data-gn-datetime="datetime"' in html and 'data-gn-default-time="09:00"' in html
    assert 'data-gn-datetime="time"' in html and 'data-gn-minute-step="15"' in html
    assert 'class="gn-input"' in html and 'autocomplete="off"' in html


def test_render_con_hora_local_si_usa_zonas_horarias(settings):
    settings.USE_TZ = True
    settings.TIME_ZONE = "America/Argentina/Buenos_Aires"
    aware = timezone.make_aware(datetime(2026, 11, 5, 12, 0), timezone.get_fixed_timezone(0))  # 12:00 UTC
    assert GnDateTimeInput().format_value(aware) == "2026-11-05T09:00"


def test_lo_enviado_con_formato_visible_se_convierte_a_iso():
    f = Agenda(data={"inicio": "05/11/2026 09:30", "dia": "1/3/2026", "hora": "18:15"})
    assert f.is_valid(), f.errors
    data = {**f.cleaned_data, "inicio": naive(f.cleaned_data["inicio"])}
    assert data == {"inicio": datetime(2026, 11, 5, 9, 30), "dia": date(2026, 3, 1), "hora": time(18, 15)}


def test_lo_enviado_sin_javascript_iso_tambien_se_acepta():
    f = Agenda(data={"inicio": "2026-11-05T09:30", "dia": "2026-03-01", "hora": "18:15"})
    assert f.is_valid(), f.errors
    assert naive(f.cleaned_data["inicio"]) == datetime(2026, 11, 5, 9, 30)


def test_texto_invalido_llega_al_campo_y_se_vuelve_a_mostrar():
    f = Agenda(data={"inicio": "31/02/2026 10:00", "dia": "", "hora": ""})
    assert not f.is_valid()
    assert f.errors["inicio"] == ["Ingresá una fecha y hora válidas"]
    html = str(f["inicio"])
    assert 'data-gn-raw="31/02/2026 10:00"' in html  # el JS lo muestra tal cual
    assert "value=" not in html  # el input nativo no recibe un valor que no es ISO


def test_valor_vuelve_normalizado_al_redibujar_con_error_en_otro_campo():
    f = Agenda(data={"inicio": "5/11/26 9", "dia": "", "hora": "99:00"})
    assert not f.is_valid() and "hora" in f.errors
    assert 'value="2026-11-05T09:00"' in str(f["inicio"])


def test_vacio_y_requerido():
    f = Agenda(data={"inicio": "  "})
    assert not f.is_valid() and "inicio" in f.errors


# --- media y estáticos --------------------------------------------------------
def test_media_cally_como_modulo_y_datetime_js(settings):
    media = str(Agenda().media)
    assert re.search(r'<script src="/static/geneos_ui/vendor/cally/cally\.js\?v=[0-9.]+" type="module"></script>', media)
    assert re.search(r'<script src="/static/geneos_ui/js/datetime\.js\?v=[0-9.]+" defer></script>', media)
    assert media.count("cally.js") == 1  # tres widgets, un solo script


def test_tag_gn_datetime_js_sin_formulario():
    html = Template("{% load geneos_ui %}{% gn_datetime_js %}").render(Context())
    assert "cally.js" in html and "datetime.js" in html


def test_cally_vendorizado_sin_cambios_y_con_licencia():
    js = STATIC / "vendor" / "cally" / "cally.js"
    assert hashlib.sha256(js.read_bytes()).hexdigest() == CALLY_SHA256
    assert "MIT" in (STATIC / "vendor" / "cally" / "README.md").read_text(encoding="utf-8")
    assert "Permission is hereby granted" in (STATIC / "vendor" / "cally" / "LICENSE").read_text(encoding="utf-8")
    for path in ("geneos_ui/vendor/cally/cally.js", "geneos_ui/js/datetime.js"):
        assert finders.find(path)


def test_css_de_fecha_y_hora_solo_con_tokens():
    css = (STATIC / "css" / "geneos-ui.css").read_text(encoding="utf-8")
    block = css[css.index("Fecha y hora (0.5.0)"):css.index("} /* @layer geneos-ui */")]
    for cls in (".gn-popover", ".gn-calendar", ".gn-time", ".gn-datetime"):
        assert cls in block
    sin_comentarios = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
    assert not re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", sin_comentarios), "colores fijos en lugar de tokens"


def test_version_del_js_coincide():
    assert f'window.GN.version = "{__version__}"' in (STATIC / "js" / "geneos-ui.js").read_text(encoding="utf-8")
    assert __version__ == "0.5.0"


def test_catalogo_muestra_la_seccion(client, settings):
    settings.DEBUG = True
    html = client.get("/").content.decode()
    assert 'id="fecha-hora"' in html and 'href="#fecha-hora"' in html
    assert html.count('data-gn-datetime="datetime"') >= 4 and "calendar-date data-gn-calendar" in html
    assert "cally.js" in html and "datetime.js" in html
