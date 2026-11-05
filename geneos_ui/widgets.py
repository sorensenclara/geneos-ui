"""Widgets de fecha y hora (0.5.0): GnDateTimeInput, GnDateInput y GnTimeInput.

Un solo <input> con el ``name`` del campo, sin campos ocultos:

- Sin JavaScript es un control nativo (``datetime-local``, ``date`` o ``time``)
  con el valor en formato ISO, ``min`` y ``max``: funciona y se envía igual.
- Con JavaScript (``geneos_ui/js/datetime.js``) el mismo input pasa a texto
  con el formato visible ``dd/mm/aaaa HH:mm`` y suma el botón que abre el
  calendario (``gn-popover`` + ``gn-calendar`` + ``gn-time``). Lo que se ve es
  exactamente lo que se envía.

``value_from_datadict`` acepta los dos formatos y le entrega al campo de Django
el valor en ISO, así que funciona con ``DateTimeField``, ``DateField`` y
``TimeField`` sin tocar sus ``input_formats``. Un texto que no se puede leer
llega tal cual y el campo lo rechaza con su mensaje ``invalid``.

Los scripts se declaran en ``Media``: en el template hay que incluir
``{{ form.media }}`` (o ``{% gn_datetime_js %}``).
"""
import re
from datetime import date, datetime, time

from django import forms
from django.conf import settings
from django.utils import timezone

from .conf import get_config

CALLY_JS = "geneos_ui/vendor/cally/cally.js"
DATETIME_JS = "geneos_ui/js/datetime.js"

_DATE_DMY = re.compile(r"^\s*(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2}|\d{4})\s*$")
_DATE_ISO = re.compile(r"^\s*(\d{4})-(\d{1,2})-(\d{1,2})\s*$")
_TIME = re.compile(r"^\s*(\d{1,2})(?:[:.h](\d{2}))?(?::(\d{2}))?\s*(?:hs?)?\s*$", re.I)
_TIME_COMPACT = re.compile(r"^\s*(\d{2})(\d{2})\s*$")


def parse_date(value):
    """``dd/mm/aaaa`` (también con - o . y año de dos cifras) o ISO. None si no es válida."""
    if not isinstance(value, str):
        return None
    m = _DATE_DMY.match(value)
    if m:
        d, mo, y = (int(x) for x in m.groups())
        if len(m.group(3)) == 2:
            y += 2000
    else:
        m = _DATE_ISO.match(value)
        if not m:
            return None
        y, mo, d = (int(x) for x in m.groups())
    try:
        return date(y, mo, d)
    except ValueError:
        return None


def parse_time(value):
    """``HH:mm`` (también ``9``, ``9.30``, ``0930``, ``9:30 hs`` o con segundos). None si no es válida."""
    if not isinstance(value, str):
        return None
    m = _TIME.match(value) or _TIME_COMPACT.match(value)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2) or 0)
    if h > 23 or mi > 59:
        return None
    return time(h, mi)


def parse_datetime(value):
    """``dd/mm/aaaa HH:mm`` o ISO (``aaaa-mm-ddTHH:mm``, con o sin segundos). None si no es válida."""
    if not isinstance(value, str):
        return None
    parts = re.split(r"\s*(?:T|,|\s)\s*", value.strip(), maxsplit=1)
    if len(parts) != 2:
        return None
    d, t = parse_date(parts[0]), parse_time(parts[1])
    if d is None or t is None:
        return None
    return datetime.combine(d, t)


def _asset_url(path):
    from .templatetags.geneos_ui import _asset  # import tardío: los tags importan este módulo

    return _asset(path, get_config())


def datetime_media():
    """Cally (módulo ES) y el comportamiento de los selectores, con ``?v=`` si está configurado."""
    return forms.Media(js=[
        forms.Script(_asset_url(CALLY_JS), type="module"),
        forms.Script(_asset_url(DATETIME_JS), defer=True),
    ])


class _GnTemporalInput(forms.widgets.Input):
    template_name = "geneos_ui/widgets/datetime.html"
    kind = ""
    iso_format = ""
    display = ""
    parser = None

    def __init__(self, attrs=None, *, minute_step=5, default_time=None, invalid_message=None, picker_label=None):
        """
        minute_step: paso de la lista de minutos del selector (el texto acepta cualquier minuto).
        default_time: hora que se completa al elegir solo el día ("09:00"); por defecto 00:00.
        invalid_message: texto del error en el navegador cuando lo escrito no es una fecha válida.
        picker_label: nombre accesible del botón y del diálogo ("Elegir fecha de inicio").
        """
        super().__init__({"class": "gn-input", "autocomplete": "off", **(attrs or {})})
        self.minute_step = int(minute_step)
        self.default_time = default_time
        self.invalid_message = invalid_message
        self.picker_label = picker_label

    @property
    def media(self):
        return datetime_media()

    def _to_python(self, value):
        if isinstance(value, str):
            return type(self).parser(value)
        return value

    def format_value(self, value):
        if value in (None, ""):
            return None
        parsed = self._to_python(value)
        if parsed is None:
            return None  # el texto original viaja en data-gn-raw (ver get_context)
        if isinstance(parsed, datetime) and settings.USE_TZ and timezone.is_aware(parsed):
            parsed = timezone.localtime(parsed)
        return parsed.strftime(self.iso_format)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        raw = value if isinstance(value, str) and value.strip() and self._to_python(value) is None else ""
        context["widget"].update({
            "kind": self.kind,
            "raw": raw,
            "display": self.display,
            "minute_step": self.minute_step,
            "default_time": self.default_time or "",
            "invalid_message": self.invalid_message or "",
            "picker_label": self.picker_label or "",
        })
        return context

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if not isinstance(value, str) or not value.strip():
            return value
        parsed = type(self).parser(value)
        return parsed.strftime(self.iso_format) if parsed is not None else value


class GnDateTimeInput(_GnTemporalInput):
    """Fecha y hora. Se ve y se envía como ``dd/mm/aaaa HH:mm``; sin JS, ``datetime-local``."""
    input_type = "datetime-local"
    kind = "datetime"
    iso_format = "%Y-%m-%dT%H:%M"
    display = "dd/mm/aaaa HH:mm"
    parser = staticmethod(parse_datetime)


class GnDateInput(_GnTemporalInput):
    """Fecha. Se ve y se envía como ``dd/mm/aaaa``; sin JS, ``date``."""
    input_type = "date"
    kind = "date"
    iso_format = "%Y-%m-%d"
    display = "dd/mm/aaaa"
    parser = staticmethod(parse_date)


class GnTimeInput(_GnTemporalInput):
    """Hora. Se ve y se envía como ``HH:mm``; sin JS, ``time``."""
    input_type = "time"
    kind = "time"
    iso_format = "%H:%M"
    display = "HH:mm"
    parser = staticmethod(parse_time)
