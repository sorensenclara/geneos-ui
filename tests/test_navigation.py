from types import SimpleNamespace

from geneos_ui.navigation import NavItem, NavSection, build_nav, search_index


def req(path="/", perms=(), **user_attrs):
    user = SimpleNamespace(has_perms=lambda ps: set(ps) <= set(perms), **user_attrs)
    return SimpleNamespace(path=path, user=user)


def test_filtra_por_permisos_y_condiciones():
    nav = [
        NavItem("Inicio", url="/"),
        NavItem("Usuarios", url="/usuarios/", perms=("auth.view_user",)),
        NavItem("Clientes", url="/clientes/", visible=lambda r: r.user.is_operador),
    ]
    labels = [e["label"] for e in build_nav(nav, req(is_operador=False))]
    assert labels == ["Inicio"]
    labels = [e["label"] for e in build_nav(nav, req(perms=("auth.view_user",), is_operador=True))]
    assert labels == ["Inicio", "Usuarios", "Clientes"]


def test_regla_que_falla_oculta_el_item_sin_romper_el_menu():
    def rota(r):
        raise AttributeError("no existe")
    out = build_nav([NavItem("A", url="/a/", visible=rota), NavItem("B", url="/b/")], req())
    assert [e["label"] for e in out] == ["B"]


def test_activo_y_grupo_abierto():
    nav = [
        NavItem("Inicio", url="/"),
        NavItem("Matafuegos", children=[NavItem("Listado", url="/matafuegos/"), NavItem("Vencimientos", url="/matafuegos/vencimientos/")]),
    ]
    out = build_nav(nav, req(path="/matafuegos/vencimientos/"))
    inicio, grupo = out
    assert inicio["active"] is False  # "/" solo coincide con la raíz exacta
    assert grupo["type"] == "group" and grupo["has_active"] is True
    activos = [c["label"] for c in grupo["children"] if c["active"]]
    assert "Vencimientos" in activos


def test_grupo_sin_hijos_visibles_desaparece_y_seccion_vacia_tambien():
    nav = [
        NavItem("Inicio", url="/"),
        NavSection("Administración"),
        NavItem("Config", children=[NavItem("Usuarios", url="/u/", perms=("x.y",))]),
    ]
    out = build_nav(nav, req())
    assert [e["label"] for e in out] == ["Inicio"]


def test_url_inexistente_se_omite():
    out = build_nav([NavItem("Roto", url="app:no_existe"), NavItem("Ok", url="/ok/")], req())
    assert [e["label"] for e in out] == ["Ok"]


def test_ids_unicos_y_indice_de_busqueda():
    nav = [NavItem("Reportes", children=[NavItem("A", url="/a/")]), NavItem("Reportes", children=[NavItem("B", url="/b/")])]
    out = build_nav(nav, req())
    assert out[0]["id"] != out[1]["id"]
    idx = search_index(out)
    assert {"label": "B", "parent": "Reportes", "href": "/b/", "keywords": ""} in idx
