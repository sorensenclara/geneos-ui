"""Formulario de demostración de la sección «Fecha y hora» del catálogo.

Usa los widgets reales (geneos_ui.widgets), así el catálogo muestra el HTML
que reciben los productos.
"""
from datetime import date, timedelta

from django import forms

from .catalog_examples import DATETIME
from .widgets import GnDateInput, GnDateTimeInput, GnTimeInput


def datetime_demo_form(product):
    ex = DATETIME[product]
    today = date.today()

    class DateTimeDemoForm(forms.Form):
        cuando = forms.DateTimeField(label=ex["datetime"][0], help_text=ex["datetime"][1],
                                     widget=GnDateTimeInput(default_time="09:00"))
        fecha = forms.DateField(label=ex["date"][0], required=False, widget=GnDateInput())
        hora = forms.TimeField(label=ex["time"][0], required=False, widget=GnTimeInput(minute_step=15))
        acotada = forms.DateField(label=ex["bounded"][0], help_text=ex["bounded"][1], required=False,
                                  widget=GnDateInput(attrs={"min": today.isoformat(), "max": (today + timedelta(days=30)).isoformat()}))
        con_error = forms.DateTimeField(label="Con error del servidor", required=False, widget=GnDateTimeInput())
        deshabilitado = forms.DateTimeField(label="Deshabilitado", required=False, disabled=True, widget=GnDateTimeInput())

    form = DateTimeDemoForm(
        initial={"cuando": ex["values"]["datetime"], "fecha": ex["values"]["date"], "hora": ex["values"]["time"],
                 "con_error": "31/02/2026 10:00", "deshabilitado": ex["values"]["datetime"]},
        auto_id=f"{product}-dt-%s",
    )
    # ayuda y error vinculados al input, como en ex/dt_field.html
    for name, field in form.fields.items():
        if field.help_text:
            field.widget.attrs["aria-describedby"] = f"{product}-dt-{name}-h"
    form.fields["con_error"].widget.attrs.update({"aria-invalid": "true", "aria-describedby": f"{product}-dt-con_error-e"})
    return form
