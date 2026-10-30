"""Menú de GEFLOTA: el producto define sus ítems, íconos y permisos; GENEOS UI lo dibuja."""
from geneos_ui.navigation import NavItem, NavLink, NavSection

ICON = "geflota/iconos/{}.svg"   # SVG blancos propios: en la barra clara los tiñe NAV_ICONS = "tint"


def get_nav(request):
    return [
        NavItem("Inicio", url="geflota:inicio", icon_static=ICON.format("inicio")),
        NavSection("Operación"),
        NavItem("Vehículos", url="geflota:vehiculos", icon_static=ICON.format("vehiculos"),
                keywords="patente dominio unidad camión",
                # accesos directos: aparecen solo al buscar en el menú
                search_links=[
                    NavLink("Alta de vehículo", url="geflota:pendiente", url_kwargs={"seccion": "alta-vehiculo"}, keywords="nuevo agregar"),
                    NavLink("Vehículos en taller", url="geflota:vehiculos", keywords="reparación"),
                ]),
        NavItem("Mantenimiento", url="geflota:mantenimiento", icon_static=ICON.format("mantenimiento"), children=[
            NavItem("Órdenes de servicio", url="geflota:pendiente", url_kwargs={"seccion": "ordenes"}),
            NavItem("Vencimientos", url="geflota:pendiente", url_kwargs={"seccion": "vencimientos"}, badge="3",
                    keywords="VTV seguro patente"),
        ]),
        NavItem("Choferes", url="geflota:pendiente", url_kwargs={"seccion": "choferes"}, icon_static=ICON.format("choferes"),
                search_links=[NavLink("Licencias por vencer", url="geflota:pendiente", url_kwargs={"seccion": "licencias"}, keywords="carnet registro")]),
        NavItem("Combustible", url="geflota:pendiente", url_kwargs={"seccion": "combustible"}, icon_static=ICON.format("combustible")),
        NavSection("Administración"),
        # solo para quien tenga el permiso: un usuario anónimo no lo ve
        NavItem("Costos", url="geflota:pendiente", url_kwargs={"seccion": "costos"}, icon="i-coins",
                perms=("geflota.view_costos",)),
        NavItem("Configuración", url="geflota:pendiente", url_kwargs={"seccion": "configuracion"}, icon="i-gear"),
    ]


def get_footer(request):
    """Pie del menú: «Ayuda y soporte» lleva a una página real. Sin URL, no se mostraría."""
    return [NavItem("Ayuda y soporte", url="geflota:ayuda", icon="i-help")]
