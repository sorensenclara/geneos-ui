"""Layout gn-auth (geneos_ui/layouts/auth.html): solo presentación.

Sin bloques sobrescritos arma la pantalla completa (logo, título, descripción,
usuario, contraseña con «mostrar», recordarme, recuperar contraseña y botón);
los productos cambian textos con bloques o contexto y los colores del fondo
con GENEOS_UI["AUTH_BACKGROUND"].
"""
import re
from pathlib import Path

import pytest
from django import forms
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings

from geneos_ui.checks import check_geneos_ui
from geneos_ui.conf import get_config
from geneos_ui.context_processors import geneos_ui as gn_context

ROOT = Path(__file__).resolve().parents[1] / "geneos_ui" / "static" / "geneos_ui"
rf = RequestFactory()


def render(extra=None, product="gema", **cfg):
    with override_settings(GENEOS_UI={"PRODUCT": product, **cfg}):
        request = rf.get("/")
        request.user = None
        ctx = {**gn_context(request), **(extra or {})}
        return render_to_string("geneos_ui/layouts/auth.html", ctx, request=request)


def test_pantalla_completa_por_defecto():
    html = render({"auth_forgot_url": "/recuperar/"})
    assert '<main class="gn-auth">' in html
    assert re.search(r'<h1 class="gn-auth__title" id="gn-auth-title">GEMA</h1>', html)
    assert 'name="username"' in html and 'autocomplete="username"' in html
    assert 'type="password" name="password" autocomplete="current-password"' in html
    assert 'data-gn-password-toggle="gn-auth-password"' in html and 'aria-pressed="false"' in html
    assert 'name="remember"' in html
    assert '<a class="gn-auth__link" href="/recuperar/">¿Olvidaste tu contraseña?</a>' in html
    assert 'class="gn-btn gn-btn--primary gn-btn--lg gn-btn--block gn-auth__submit" type="submit">Ingresar<' in html
    assert 'name="csrfmiddlewaretoken"' in html


def test_labels_asociados_y_boton_mostrar_oculto_sin_js():
    html = render()
    for id_ in ("gn-auth-username", "gn-auth-password"):
        assert f'for="{id_}"' in html and f'id="{id_}"' in html
    btn = re.search(r"<button[^>]*data-gn-password-toggle[^>]*>", html).group(0)
    assert " hidden" in btn and 'aria-label="Mostrar contraseña"' in btn and 'type="button"' in btn


def test_sin_url_de_recuperacion_no_hay_enlace():
    assert "gn-auth__link" not in render()


def test_bloques_personalizables():
    t = Template(
        '{% extends "geneos_ui/layouts/auth.html" %}'
        '{% block auth_title %}GENEOS Web Admin{% endblock %}'
        '{% block auth_description %}Iniciá sesión para administrar las webs.{% endblock %}'
        '{% block auth_footer %}<p class="pie">v1</p>{% endblock %}'
    )
    with override_settings(GENEOS_UI={"PRODUCT": "gema"}):
        request = rf.get("/")
        request.user = None
        html = t.render(Context({**gn_context(request), "request": request, "auth_submit_label": "Entrar"}))
    assert ">GENEOS Web Admin</h1>" in html
    assert '<p class="gn-auth__sub">Iniciá sesión para administrar las webs.</p>' in html
    assert '<p class="pie">v1</p>' in html and ">Entrar</button>" in html


def test_auth_content_reemplaza_todo_como_antes():
    t = Template('{% extends "geneos_ui/layouts/auth.html" %}{% block auth_content %}<h1>Ingresar</h1>{% endblock %}')
    with override_settings(GENEOS_UI={"PRODUCT": "gema"}):
        request = rf.get("/")
        request.user = None
        html = t.render(Context({**gn_context(request), "request": request}))
    assert "gn-auth__form" not in html and "<h1>Ingresar</h1>" in html


class LoginForm(forms.Form):
    username = forms.CharField(label="Correo")
    password = forms.CharField(label="Clave")

    def clean(self):
        raise forms.ValidationError("Usuario o contraseña incorrectos.")


def test_errores_del_formulario():
    form = LoginForm({"username": "ana", "password": ""})
    form.is_valid()
    html = render({"form": form})
    assert 'role="alert"' in html and "Usuario o contraseña incorrectos." in html
    assert ">Correo</label>" in html and ">Clave</label>" in html
    assert 'value="ana"' in html
    assert 'aria-invalid="true" aria-describedby="gn-auth-password-err"' in html
    assert 'id="gn-auth-password-err"' in html


def test_logo_auth_y_respaldo_en_logo_topbar():
    assert 'class="gn-auth__logo"' not in render(product="nuevo", THEME_CSS=["geneos_ui/css/tokens.css"])
    html = render(product="nuevo", THEME_CSS=["geneos_ui/css/tokens.css"], LOGO_TOPBAR="x/claro.svg")
    assert re.search(r'<img class="gn-auth__logo" src="[^"]*x/claro\.svg" alt="nuevo">', html)
    html = render(product="nuevo", THEME_CSS=["geneos_ui/css/tokens.css"], LOGO_TOPBAR="x/claro.svg", LOGO_AUTH="x/auth.svg")
    assert "x/auth.svg" in html


def test_fondo_configurable():
    html = render(AUTH_BACKGROUND=("#1f4fa0", "#1f7a4d"))
    assert '<main class="gn-auth" style="--gn-auth-from: #1f4fa0; --gn-auth-to: #1f7a4d;">' in html


@pytest.mark.parametrize("valor", [("#fff",), "#fff", ("#fff", "red;}body{x"), ("#fff", "</style>")])
def test_fondo_invalido_se_ignora_y_avisa(settings, valor):
    settings.GENEOS_UI = {"PRODUCT": "gema", "AUTH_BACKGROUND": valor}
    assert get_config()["AUTH_BACKGROUND"] is None
    assert "geneos_ui.E009" in [e.id for e in check_geneos_ui(None)]
    assert "style=" not in render(AUTH_BACKGROUND=valor).split('<main class="gn-auth"')[1].split(">")[0]


@pytest.mark.parametrize("valor", [("#1f4fa0", "#1f7a4d"), ["rgb(31, 79, 160)", "var(--gn-c-accent)"], ("navy", "oklch(0.5 0.1 150)")])
def test_fondo_valido(settings, valor):
    settings.GENEOS_UI = {"PRODUCT": "gema", "AUTH_BACKGROUND": valor}
    assert "geneos_ui.E008" not in [e.id for e in check_geneos_ui(None)]


def test_css_usa_tokens_y_variables_de_fondo():
    css = (ROOT / "css" / "geneos-ui.css").read_text()
    assert "var(--gn-auth-from, var(--gn-c-sidebar))" in css and "var(--gn-auth-to, var(--gn-c-sidebar-deep))" in css
    bloque = css[css.index(".gn-auth {"):css.index("0.4.0 · Lista de funcionalidades")]
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", bloque), "los colores salen de tokens"


def test_js_alterna_la_contrasena():
    js = (ROOT / "js" / "geneos-ui.js").read_text()
    assert "function initPasswordToggles(root)" in js and "initPasswordToggles(root);" in js
