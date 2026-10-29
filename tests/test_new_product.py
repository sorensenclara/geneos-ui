"""GEFLOTA (producto ficticio del sandbox) se incorpora solo desde sus settings.

Usa exactamente el GENEOS_UI de sandbox/sandbox/settings_geflota.py y la app
sandbox/geflota/. Si algún test de este archivo necesitara tocar geneos_ui/
para pasar, la 0.3.0 no cumpliría su objetivo.
"""
import re

import pytest
from django.contrib.staticfiles import finders

from geneos_ui.checks import check_geneos_ui
from sandbox.settings_geflota import GENEOS_UI as GEFLOTA


@pytest.fixture
def geflota(settings):
    settings.GENEOS_UI = dict(GEFLOTA)
    settings.DEBUG = True
    return settings


def test_chequeos_sin_problemas(geflota):
    assert check_geneos_ui(None) == []


def test_estaticos_del_producto_existen():
    for key in ("LOGO_FULL", "LOGO_ICON", "LOGO_TOPBAR"):
        assert finders.find(GEFLOTA[key]), key
    assert all(finders.find(p) for p in GEFLOTA["THEME_CSS"])


def test_layout_con_su_identidad(geflota, client):
    html = client.get("/geflota/").content.decode()
    assert 'data-gn-product="geflota"' in html
    assert "/static/geflota/css/tema-geflota.css" in html and "themes/geflota.css" not in html
    assert "geflota/logos/geflota-blanco.svg" in html and "geflota/logos/geflota-color.svg" in html
    assert 'data-gn-nav="vertical"' in html and 'data-gn-default="expanded"' in html
    assert "data-gn-prefs-toggle" in html and "data-gn-legacy-key" not in html
    assert "Tu flota en orden" in html


def test_menu_permisos_y_activo(geflota, client):
    html = client.get("/geflota/vehiculos/").content.decode()
    labels = re.findall(r'<span class="gn-nav__label">([^<]+)</span>', html)
    assert labels[:5] == ["Inicio", "Vehículos", "Mantenimiento", "Choferes", "Combustible"]
    assert "Costos" not in html               # perms=("geflota.view_costos",): el anónimo no lo ve
    assert "Configuración" in html
    assert re.search(r'<a class="gn-nav__item"[^>]*href="/geflota/vehiculos/"[^>]*aria-current="page"', html)


def test_iconos_propios_tenidos_en_la_barra_clara(geflota, client):
    html = client.get("/geflota/").content.decode()
    assert html.count('class="gn-nav__icon-tint"') >= 5
    assert "--gn-icon-src: url(&quot;/static/geflota/iconos/vehiculos.svg&quot;)" in html


def test_variante_clara_propia_por_item(geflota, client):
    from geneos_ui.navigation import NavItem, build_nav
    item = NavItem("Vehículos", url="/v/", icon_static="geflota/iconos/vehiculos.svg",
                   icon_static_h="geflota/logos/geflota-iso.svg")
    entry = build_nav([item], None)[0]
    assert entry["icon_h"] == "geflota/logos/geflota-iso.svg" and not entry["icon_h_tint"]


def test_componentes_de_pantalla(geflota, client):
    html = client.get("/geflota/vehiculos/?page=2&o=-patente").content.decode()
    assert 'aria-sort="descending"' in html and "gn-pagination" in html and "gn-badge--" in html
    assert 'data-th="Patente"' in html


def test_puente_bootstrap_con_sus_colores(geflota):
    from django.template import Context, Template
    geflota.GENEOS_UI = {**GEFLOTA, "BRIDGES": ["bootstrap5"]}
    html = Template("{% load geneos_ui %}{% gn_css %}").render(Context())
    assert ':root[data-gn-product="geflota"] { --bs-primary-rgb: 179, 86, 9; }' in html
