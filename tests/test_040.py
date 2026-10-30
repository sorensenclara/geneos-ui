"""0.4.0: variantes, lista de funcionalidades, encabezado con ícono, accesos directos,
pie del menú, menú del usuario, CSS existente y modo oscuro progresivo."""
import re

import pytest
from django.template import Context, Template
from django.test import RequestFactory

from geneos_ui.navigation import NavItem, NavLink, build_links, build_nav

rf = RequestFactory()


def render(tpl, **ctx):
    return Template("{% load geneos_ui %}" + tpl).render(Context(ctx))


# --- variantes de color ---------------------------------------------------
def test_gelectric_ofrece_verde_y_azul_y_migra_su_clave_vieja(settings):
    settings.GENEOS_UI = {"PRODUCT": "gelectric"}
    html = render("{% gn_theme_boot %}{% gn_prefs %}")
    assert "'gn-variant:'" in html and '"lk": "geletric-brand-color"' in html
    assert '"lv": {"green": "", "blue": "blue"}' in html
    assert 'data-gn-variant-switch data-gn-variant-product="gelectric"' in html
    assert re.findall(r'data-gn-variant-value="([^"]*)"', html) == ["", "blue"]


@pytest.mark.parametrize("product", ["gema", "geagro-cereales", "geagro-vid"])
def test_sin_variantes_no_cambia_nada(settings, product):
    settings.GENEOS_UI = {"PRODUCT": product}
    html = render("{% gn_theme_boot %}{% gn_prefs %}")
    assert "gn-variant" not in html and "data-gn-variant-switch" not in html


def test_variantes_declaradas_por_un_producto_nuevo(settings):
    settings.GENEOS_UI = {"PRODUCT": "geflota", "THEME_CSS": ["t.css"], "VARIANTS": {"": "Petróleo", "noche": "Noche"}}
    html = render("{% gn_prefs %}")
    assert "Petróleo" in html and 'data-gn-variant-value="noche"' in html


# --- lista de funcionalidades y encabezado --------------------------------
def test_lista_dos_columnas_nombre_completo_y_estado():
    items = [{"label": "Comprobantes internos (plantillas) con un nombre bastante largo"}, {"label": "Caja", "href": "/caja/"}]
    html = render('{% gn_link_list items=items empty_status="En definición" %}', items=items)
    assert "gn-link-list--cols-2" in html
    assert 'title="Comprobantes internos (plantillas) con un nombre bastante largo"' in html
    assert html.count("En definición") == 1 and 'href="/caja/"' in html
    assert "gn-link-list__icon" not in html  # sin ícono propio no se inventa ninguno


def test_lista_con_icono_descripcion_enlace_y_estado():
    html = render('{% gn_link_list columns=1 %}{% gn_link_item label="Ficha" href="/f/" icon="i-idcard" description="Consulta" %}'
                  '{% gn_link_item label="Cuota" status="En definición" status_kind="warning" %}{% endgn_link_list %}')
    assert "gn-link-list--cols-1" in html and "#i-idcard" in html and "Consulta" in html
    assert 'gn-badge--warning">En definición' in html and "is-static" in html


def test_encabezado_con_icono_original_o_sin_icono():
    html = render('{% gn_page_head title="Contabilidad" icon="gelectric:contabilidad" only %}')
    assert "gn-page-head--icon" in html and "icon%20-%20Contabilidad.svg" in html
    # GEAGRO no tiene variante para fondo claro: no se dibuja ningún ícono
    html = render('{% gn_page_head title="Dashboard" icon="geagro-vid:dashboard" %}<a>Volver</a>{% endgn_page_head %}')
    assert "gn-page-head--icon" not in html and "gn-page-head__actions" in html


# --- accesos directos del buscador ----------------------------------------
def test_accesos_directos_respetan_permisos():
    req = rf.get("/")
    req.user = type("U", (), {"has_perms": lambda self, p: False, "is_authenticated": True})()
    nav = build_nav([NavItem("Asociados", url="/asociados/", search_links=[
        NavLink("Cuota capital", url="/asociados/cuota/", keywords="aportes"),
        NavLink("Padrón", url="/asociados/padron/", perms=("core.view_padron",)),
        NavLink("Sin destino"),
    ])], req)
    assert [d["label"] for d in nav[0]["search_links"]] == ["Cuota capital"]


def test_accesos_directos_en_el_sidebar(settings, client):
    settings.DEBUG = True
    html = client.get("/").content.decode()
    # el catálogo no los usa: el HTML de los cuatro productos no cambia
    assert "gn-nav__direct" not in html


# --- pie del menú y menú del usuario --------------------------------------
def test_pie_solo_con_destino_real():
    links = build_links([NavItem("Ayuda y soporte", url=None, icon="i-help"), NavItem("Ayuda", url="#"),
                         NavItem("Soporte", url="mailto:soporte@geneos.com.ar", icon="i-help")], rf.get("/"))
    assert [l["label"] for l in links] == ["Soporte"]


def test_layout_con_pie_menu_de_usuario_y_cierre_de_sesion(settings, client, django_user_model):
    settings.GENEOS_UI = {**settings.GENEOS_UI, "NAV_FOOTER": "tests.test_040.footer", "USER_MENU": "tests.test_040.user_menu",
                          "LOGOUT_URL": "/salir/"}
    user = django_user_model.objects.create_user("clara", password="x")
    client.force_login(user)
    html = client.get("/demo/").content.decode()
    assert 'class="gn-nav gn-nav--foot"' in html and ">Ayuda y soporte<" in html
    assert 'gn-dropdown__item--hnav' in html  # en horizontal, la ayuda pasa al menú del usuario
    assert 'href="/perfil/"' in html
    assert '<form method="post" action="/salir/" class="gn-dropdown__form">' in html and "csrfmiddlewaretoken" in html


def footer(request):
    return [NavItem("Ayuda y soporte", url="https://www.geneos.com.ar/soporte/", icon="i-help"), NavItem("Manual", url=None)]


def user_menu(request):
    return [NavItem("Mi perfil", url="/perfil/", icon="i-user")]


# --- CSS existente y modo oscuro progresivo -------------------------------
def test_css_existente_en_su_capa(settings):
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "LEGACY_CSS": ["core/css/dashboard.css", "core/css/puente.css"]}
    html = render("{% gn_css %}")
    assert html.index("geneos-ui.css") < html.index("@layer geneos-ui, legacy;")
    assert '@import url("/static/core/css/dashboard.css") layer(legacy);' in html
    assert '@import url("/static/core/css/puente.css") layer(legacy);' in html
    assert "body.gn-root {" in html
    settings.GENEOS_UI = {"PRODUCT": "gelectric"}
    assert "layer(legacy)" not in render("{% gn_css %}")


def test_bloque_para_marcar_pantallas_existentes():
    from pathlib import Path
    layout = (Path(__file__).resolve().parent.parent / "geneos_ui/templates/geneos_ui/layouts/app.html").read_text()
    assert '<main class="gn-content" id="gn-main-content" tabindex="-1"{% block content_attrs %}{% endblock %}>' in layout


def test_iconos_del_sidebar_pintados_solo_si_se_pide(settings):
    entry = build_nav([NavItem("Contabilidad", url="/c/", icon_static="core/i.svg")], None)[0]
    assert "gn-nav__icon-stint" not in render("{% gn_nav_icon e %}", e=entry, gn={"sidebar_icons": "as-is"})
    assert "gn-nav__icon-stint" in render("{% gn_nav_icon e %}", e=entry, gn={"sidebar_icons": "tint"})


def test_chequeos_de_las_claves_nuevas(settings):
    from geneos_ui.checks import check_geneos_ui
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "SIDEBAR_ICONS": "color", "LEGACY_CSS": "no/existe.css"}
    ids = {p.id for p in check_geneos_ui(None)}
    assert {"geneos_ui.E006", "geneos_ui.W004"} <= ids
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "SIDEBAR_ICONS": "tint"}
    ids = {p.id for p in check_geneos_ui(None)}
    assert not ids & {"geneos_ui.E006", "geneos_ui.W004"}


def test_grupo_con_url_propia_queda_activo_y_no_el_inicio(rf):
    from geneos_ui.navigation import NavItem, build_nav
    nav = [NavItem("Inicio", url="/flota/"),
           NavItem("Mantenimiento", url="/flota/mantenimiento/", children=[NavItem("Órdenes", url="/flota/ordenes/")])]
    out = build_nav(nav, rf.get("/flota/mantenimiento/"))
    assert out[0]["active"] is False
    assert out[1]["has_active"] is True and not any(c["active"] for c in out[1]["children"])
    out = build_nav(nav, rf.get("/flota/"))
    assert out[0]["active"] is True and out[1]["has_active"] is False
