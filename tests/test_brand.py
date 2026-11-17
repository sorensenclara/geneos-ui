"""0.9.0: marca dinámica del sidebar (GENEOS_UI["BRAND"])."""
import re

import pytest
from django.core.checks import run_checks
from django.template import Context, Template
from django.test import RequestFactory

from geneos_ui.brand import Brand, initials_of, resolve_brand, safe_url
from geneos_ui.context_processors import geneos_ui

rf = RequestFactory()
LLAMADAS = []


def marca_completa(request):
    return Brand(name="Institución Ejemplo", logo_url="/media/logo.png", mark_url="/media/iso.png",
                 home_url="/panel/", footer=["Plataforma X", "Desarrollado por Y"])


def marca_dict(request):
    return {"name": "Club de Prueba", "mark_url": "/media/iso.png"}


def marca_nada(request):
    return None


def marca_rota(request):
    raise RuntimeError("falla")


def sidebar(settings, brand=None, **cfg):
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "LOGO_FULL": "x/full.svg", "LOGO_ICON": "x/icon.svg", **cfg}
    if brand:
        settings.GENEOS_UI["BRAND"] = brand
    gn = geneos_ui(rf.get("/"))["gn"]
    html = Template("{% load geneos_ui %}{% gn_sidebar %}").render(Context({"gn": gn}))
    top = Template('{% include "geneos_ui/components/topbar_brand.html" %}').render(Context({"gn": gn}))
    return gn, html, top


# --- compatibilidad ---------------------------------------------------------
def test_sin_brand_queda_la_identidad_estatica(settings):
    gn, html, top = sidebar(settings)
    assert gn["brand"] is None
    assert "gn-sidebar__logo-full" in html and "gn-brand" not in html
    assert "gn-sidebar__meta--lines" not in html and "gn-brand" not in top


@pytest.mark.parametrize("fn", ["tests.test_brand.marca_nada"])
def test_si_la_funcion_devuelve_none_tambien(settings, fn):
    gn, html, _ = sidebar(settings, fn)
    assert gn["brand"] is None and "gn-sidebar__logo-full" in html


def test_un_error_en_la_marca_no_tira_la_pagina_en_produccion(settings):
    settings.DEBUG = False
    gn, html, _ = sidebar(settings, "tests.test_brand.marca_rota")
    assert gn["brand"] is None and "gn-sidebar__logo-full" in html


def test_en_debug_el_error_se_ve(settings):
    settings.DEBUG = True
    with pytest.raises(RuntimeError):
        sidebar(settings, "tests.test_brand.marca_rota")


# --- prioridad ----------------------------------------------------------------
def test_logotipo_horizontal_con_isotipo_para_el_menu_contraido(settings):
    gn, html, top = sidebar(settings, "tests.test_brand.marca_completa")
    assert "gn-sidebar__logo-full" not in html
    assert 'class="gn-brand gn-brand--logo"' in html
    assert 'src="/media/logo.png"' in html and 'src="/media/iso.png"' in html
    assert "gn-brand__name" not in html                      # el logotipo ya lleva el nombre
    assert 'aria-label="Institución Ejemplo: inicio"' in html and 'href="/panel/"' in html
    assert re.search(r'gn-sidebar__meta--lines"><span>Plataforma X</span><span>Desarrollado por Y</span>', html)
    assert 'src="/media/logo.png"' in top


def test_isotipo_y_nombre(settings):
    _, html, top = sidebar(settings, "tests.test_brand.marca_dict")
    assert "gn-brand--logo" not in html and 'src="/media/iso.png"' in html
    assert '<span class="gn-brand__name">Club de Prueba</span>' in html
    assert "Club de Prueba" in top
    assert 'class="gn-sidebar__meta"' in html                # sin footer propio, el pie de siempre


def test_iniciales_y_nombre_sin_imagenes():
    b = resolve_brand({"name": "Club Atlético de la Villa"})
    assert b["initials"] == "CA" and b["logo_url"] is None and b["mark_url"] is None
    html = Template("{% load geneos_ui %}{% gn_sidebar %}").render(Context({"gn": {"brand": b, "home_url": "/", "product_name": "P"}, "sidebar_id": "s"}))
    assert "gn-brand__mark--initials" in html and ">CA<" in html and "Club Atlético de la Villa" in html


# --- seguridad ------------------------------------------------------------------
@pytest.mark.parametrize("url", ["javascript:alert(1)", "data:image/png;base64,AAA", "//evil.example/x.png",
                                 "media/rel.png", '/x.png" onerror="alert(1)', " ", None, 12])
def test_urls_rechazadas(url):
    assert safe_url(url) is None


@pytest.mark.parametrize("url", ["/media/clubes/escudo.png", "https://cdn.example.com/a.svg", "http://x.test/a%20b.png"])
def test_urls_aceptadas(url):
    assert safe_url(url) == url


def test_url_invalida_pasa_al_siguiente_nivel():
    b = resolve_brand({"name": "X", "logo_url": "javascript:alert(1)", "mark_url": "/iso.png"})
    assert b["logo_url"] is None and b["mark_url"] == "/iso.png"


def test_nombre_y_pie_escapados():
    b = resolve_brand({"name": "<script>alert(1)</script>", "footer": ["<b>x</b>"]})
    html = Template("{% load geneos_ui %}{% gn_sidebar %}").render(Context({"gn": {"brand": b, "home_url": "/", "product_name": "P"}, "sidebar_id": "s"}))
    assert "<script>" not in html and "&lt;script&gt;" in html and "&lt;b&gt;x&lt;/b&gt;" in html


def test_normalizacion():
    assert resolve_brand({"name": "   "}) is None
    assert resolve_brand("no es una marca") is None
    b = resolve_brand({"name": "A" * 200, "initials": "abcd", "footer": ["uno", "", "dos", "tres", "cuatro"]})
    assert len(b["name"]) == 80 and b["initials"] == "ABC" and b["footer"] == ["uno", "dos", "tres"]
    assert resolve_brand({"name": "Solo", "footer": "una línea"})["footer"] == ["una línea"]
    assert initials_of("Centro de Jubilados") == "CJ" and initials_of("El") == "E"


# --- verificación -----------------------------------------------------------------
def test_check_brand_no_importable(settings):
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "BRAND": "no.existe.funcion"}
    assert "geneos_ui.E008" in [e.id for e in run_checks()]


def test_check_brand_valido(settings):
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "BRAND": "tests.test_brand.marca_dict"}
    assert "geneos_ui.E008" not in [e.id for e in run_checks()]
