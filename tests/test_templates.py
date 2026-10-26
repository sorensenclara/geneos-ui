import re

from django.core.paginator import Paginator
from django.template import Context, Template
from django.test import RequestFactory, override_settings

rf = RequestFactory()


def render(tpl, **ctx):
    return Template("{% load geneos_ui %}" + tpl).render(Context(ctx))


def test_gn_css_carga_tokens_tema_y_puentes():
    html = render('{% gn_css "gema" "bootstrap5" %}')
    assert "tokens.css" in html and "themes/gema.css" in html and "geneos-ui.css" in html and "bridges/bootstrap5.css" in html


def test_badge_con_tipo_desconocido_cae_en_neutral():
    assert 'gn-badge--neutral' in render('{% gn_badge "X" "rojo" %}')
    assert 'gn-badge--critical gn-badge--dot' in render('{% gn_badge "Vencido" "critical" True %}')


def test_sort_th_alterna_y_marca_aria_sort():
    request = rf.get("/x/", {"o": "nombre", "q": "rossi", "page": "3"})
    html = render('{% gn_sort_th "Nombre" "nombre" %}', request=request)
    assert 'aria-sort="ascending"' in html
    assert "o=-nombre" in html and "q=rossi" in html and "page=" not in html


def test_cell_agrega_data_th():
    html = render('{% gn_cell "Saldo" "is-num" %}10{% endgn_cell %}')
    assert html == '<td data-th="Saldo" class="is-num">10</td>'


def test_paginacion_conserva_filtros_y_ventana():
    request = rf.get("/x/", {"q": "abc", "page": "7"})
    page = Paginator(list(range(250)), 10).get_page(7)
    html = render("{% gn_pagination page %}", request=request, page=page)
    assert 'aria-current="page"' in html
    assert "q=abc&amp;page=8" in html
    nums = re.findall(r'aria-label="Página (\d+)', html)
    assert nums[0] == "1" and nums[-1] == "25" and "7" in nums


@override_settings(DEBUG=True)
def test_layout_y_catalogo(client):
    r = client.get("/demo/")
    assert r.status_code == 200
    html = r.content.decode()
    assert 'data-gn-product="gelectric"' in html and "data-gn-sidebar" in html and "gn-pagination" in html
    r = client.get("/?product=gema")
    assert r.status_code == 200 and 'data-gn-product="gema"' in r.content.decode()


@override_settings(DEBUG=False)
def test_catalogo_restringido_sin_debug(client):
    assert client.get("/").status_code == 403


def test_check_producto_invalido(settings):
    from geneos_ui.checks import check_geneos_ui
    settings.GENEOS_UI = {"PRODUCT": "otro"}
    assert [e.id for e in check_geneos_ui(None)] == ["geneos_ui.E001"]


def test_sidebar_inicial_por_producto(settings):
    from geneos_ui.conf import get_config
    settings.GENEOS_UI = {"PRODUCT": "gelectric"}
    assert get_config()["SIDEBAR_DEFAULT"] == "collapsed"
    settings.GENEOS_UI = {"PRODUCT": "gema"}
    assert get_config()["SIDEBAR_DEFAULT"] == "expanded"
    settings.GENEOS_UI = {"PRODUCT": "gelectric", "SIDEBAR_DEFAULT": "expanded"}
    assert get_config()["SIDEBAR_DEFAULT"] == "expanded"


@override_settings(DEBUG=True)
def test_catalogo_marca_estado_inicial_y_clave_por_producto(client):
    html = client.get("/").content.decode()
    assert 'id="gn-sidebar-gelectric" data-gn-sidebar data-gn-default="collapsed" data-gn-storage-key="gn-sidebar-expanded:gelectric"' in html
    assert 'id="gn-sidebar-gema" data-gn-sidebar data-gn-default="expanded"' in html
