"""Datos de ejemplo del catálogo (UI Kit).

Los menús reproducen la estructura real de cada producto según la auditoría
del 14/10/2026 (GELECTRIC core/modules_data.py, GEMA core/base.html, GEAGRO
partials/sidebar.html y JAZZMIN_SETTINGS). Los números son de muestra.
"""
from .navigation import NavItem, NavSection


def _children(base, labels):
    return [NavItem(label, url=f"#{base}-{i}") for i, label in enumerate(labels, 1)]


def nav_gelectric(request=None):
    return [
        NavItem("Inicio", url="#inicio", icon="i-home"),
        NavItem("Asociados y servicios", icon="gelectric:asociados", keywords="socios padrón", children=_children("asoc", [
            "Ficha del asociado", "ABM de asociado", "Cuota capital y excepciones", "Retorno de excedentes",
            "Reintegro al darse de baja", "Reportes societarios", "Reclamos", "Órdenes de trabajo"])),
        NavItem("Abastecimiento", icon="gelectric:abastecimiento", children=_children("abas", [
            "Órdenes de compra", "Proveedores", "Facturas de proveedor", "Retenciones (Ganancias, IIBB)",
            "Orden de pago a proveedores", "Inventario y almacenes", "Autorización ARCA"])),
        NavItem("Contabilidad y Finanzas", icon="gelectric:contabilidad", children=_children("cont", [
            "Caja", "Bancos y cheques", "Plan de cuentas", "Asientos automáticos", "Bienes de uso",
            "Ajuste por inflación (RECPAM)", "Flujo de fondos"])),
        NavItem("Comercial", icon="gelectric:comercial", children=[
            NavItem("Tarifas", url="#com-1"), NavItem("Facturación masiva", url="#com-2"),
            NavItem("Autorización de facturas electrónicas", url="#com-3"), NavItem("Cobranzas", url="#com-4"),
            NavItem("Deuda y totalizador", url="#com-5"), NavItem("Avisos de deuda y corte", url="#com-6"),
        ]),
        NavItem("Consumo", icon="gelectric:consumo", children=_children("cons", [
            "Medición y estado", "Estimación de consumo", "Cambios de medidor", "Cambio de titularidad"])),
        NavItem("Reportes", icon="gelectric:reportes", children=_children("rep", [
            "Contables clásicos", "Regulatorios AFIP/ARCA", "Impresión masiva de facturas"])),
        NavItem("Impuestos", icon="gelectric:impuestos", children=_children("imp", ["IVA", "Ingresos Brutos (IIBB)", "SUSS / cargas sociales"])),
        NavItem("Sueldos", icon="gelectric:sueldos", children=_children("sue", ["Liquidación mensual", "Vacaciones", "Libro de Sueldos Digital"])),
        NavItem("Integraciones", icon="gelectric:integraciones", children=_children("int", ["Telemedición", "Terminal posnet", "Exportador GIS"])),
        NavItem("Técnico", icon="gelectric:tecnico", children=_children("tec", ["Usuarios del sistema", "Parámetros generales", "Inmuebles"])),
    ]


def nav_gema(request=None):
    return [
        NavItem("Inicio", url="#inicio", icon="gema:inicio"),
        NavSection("Gestión"),
        NavItem("Clientes", url="#clientes", icon="gema:clientes"),
        NavItem("Matafuegos", icon="gema:matafuegos", keywords="extintores", children=[
            NavItem("Listado de matafuegos", url="#matafuegos"),
            NavItem("Panel de vencimientos", url="#vencimientos", keywords="vencidos por vencer avisos whatsapp"),
        ]),
        NavItem("Órdenes de trabajo", url="#ordenes", icon="gema:ordenes", keywords="ot recargas"),
        NavItem("Tareas", url="#tareas", icon="gema:tareas", badge="4"),
        NavSection("Administración"),
        NavItem("Usuarios", url="#usuarios", icon="gema:usuarios"),
        NavItem("Mi compañía", url="#compania", icon="gema:compania"),
    ]


def _geagro_portal(product, field_label, extra):
    """Sidebar del portal del productor (templates/partials/sidebar.html de cada rama).

    Operaciones, Acopio, Ventas, Productores y Parámetros son del backoffice
    (Jazzmin) y no van en este menú: ver BACKOFFICE en catalog_examples.py.
    """
    return [
        NavSection(field_label),
        NavItem("Dashboard", url="#inicio", icon=f"{product}:dashboard"),
        NavItem("Plan técnico", url=f"#{product}-plan", icon=f"{product}:plan-tecnico", badge="Nuevo", keywords="labores"),
        NavItem("Calendario", url=f"#{product}-cal", icon=f"{product}:calendario"),
        NavItem("Alertas y avisos", url=f"#{product}-alertas", icon=f"{product}:alertas", badge="Atención", keywords="alertas avisos"),
        NavItem("Clima", url=f"#{product}-clima", icon=f"{product}:clima", keywords="lluvia pronóstico"),
        *extra,
    ]


def nav_geagro_cereales(request=None):
    return _geagro_portal("geagro-cereales", "Campo actual", [
        NavItem("Mis campos", url="#cer-campos", icon="geagro-cereales:campos", keywords="lotes"),
        # el portal usa mdi-package-variant; se usa el SVG propio del backoffice (decisión del 27/10/2026)
        NavItem("Insumos", url="#cer-insumos", icon="geagro-cereales:insumos"),
    ])


def nav_geagro_vid(request=None):
    return _geagro_portal("geagro-vid", "Viñedo actual", [
        NavItem("Fenología", url="#vid-feno", icon="geagro-vid:fenologia", keywords="brotación floración envero"),
        NavItem("Informes", url="#vid-inf", icon="geagro-vid:informes", keywords="comparación de campañas"),
        NavItem("Mis viñedos", url="#vid-vin", icon="geagro-vid:vinedos", keywords="lotes"),
    ])


PRODUCTS = [
    {
        "key": "gelectric", "name": "GELECTRIC", "nav": nav_gelectric,
        "mini_nav": [("Inicio", "i-home"), ("Asociados", "gelectric:asociados"), ("Comercial", "gelectric:comercial")],
        "logo_full": "demo/logos/gelectric-full.svg", "logo_icon": "demo/logos/gelectric-icon.svg",
        "tagline": "Energía que nos une", "version_label": "v1.0.0",
        "identity": "Verde por defecto, con la variante azul disponible.",
        "swatches": [("Sidebar", "#1b6b4c", "dashboard.css:84"), ("Marca / activo", "#0d4530", "dashboard.css:85"), ("Acento", "#17a672", "dashboard.css:23"), ("Texto de marca", "#0d7a53", "dashboard.css:24"), ("Variante azul", "#244c97", "dashboard.css:14")],
        "fonts": "Titillium Web 400 · 600 · 700 (dashboard.css)",
        "eyebrow": "Cooperativa eléctrica de ejemplo", "title": "Asociados", "desc": "Padrón de asociados, suministros y estado de cuenta.",
        "kpis": [
            ("Asociados activos", "4.812", "", "gelectric:asociados@tile", "+38 este mes", "up:good"),
            ("Suministros", "6.204", "", "i-plug", "+0,6 %", "up:good"),
            ("Consumo del mes", "2.418", "MWh", "gelectric:consumo@tile", "−3,2 % vs. sept.", "down:neutral"),
            ("Deuda vencida", "$ 12,4", "M", "gelectric:comercial@tile", "214 cuentas", "flat"),
        ],
        "series_title": "Consumo de energía, últimos 6 meses (MWh)", "unit": "MWh",
        "series": [("May", 2580), ("Jun", 2795), ("Jul", 2910), ("Ago", 2702), ("Sep", 2498), ("Oct", 2418)],
        "donut_title": "Estado de cuenta", "donut": [("Al día", 3912, "var(--gn-good)"), ("Con deuda", 686, "var(--gn-warning)"), ("En corte", 214, "var(--gn-critical)")], "num": [4, 5],
        "table_title": "Asociados", "cols": ["Asociado", "N.º socio", "Categoría", "Suministros", "Saldo", "Estado"],
        "rows": [
            ("Mariela Quiroga", "10482", "Residencial", 1, "0,00", ("Al día", "good")),
            ("Taller Rossi SRL", "07731", "Comercial", 3, "184.320,50", ("Con deuda", "warning")),
            ("Héctor Ibáñez", "11903", "Rural", 2, "0,00", ("Al día", "good")),
            ("Escuela N.º 14", "00212", "Oficial", 1, "0,00", ("Al día", "good")),
            ("Ramiro Benítez", "09618", "Residencial", 1, "62.115,00", ("Aviso de corte", "critical")),
        ],
    },
    {
        "key": "gema", "name": "GEMA", "nav": nav_gema,
        "mini_nav": [("Inicio", "gema:inicio"), ("Clientes", "gema:clientes"), ("Órdenes", "gema:ordenes")],
        "logo_full": "demo/logos/gema-full.svg", "logo_icon": "demo/logos/gema-icon.svg",
        "tagline": "Gestión de matafuegos", "version_label": "",
        "identity": "Azul GEMA en el sidebar y naranja para la acción principal.",
        "swatches": [("Sidebar (navy)", "#1B4B8D", "theme.css:269"), ("Marca / activo", "#123b6e", "panel_base.html:11"), ("Naranja", "#EC6C05", "theme.css:147"), ("Naranja oscuro", "#c65a03", "panel_base.html:14"), ("Texto naranja", "#b0530a", "theme.css:714"), ("Rojo GEMA", "#c62828", "theme.css:25")],
        "fonts": "Titillium Web 300 · 400 · 600 · 700 (theme.css)",
        "eyebrow": "Matafuegos del Sur", "title": "Matafuegos", "desc": "Vencimientos, recargas y avisos a clientes.",
        "kpis": [
            ("Matafuegos", "1.946", "", "gema:matafuegos@white", "+52 este mes", "up:good"),
            ("Por vencer (30 días)", "128", "", "i-clock", "41 sin avisar", "flat"),
            ("Vencidos", "37", "", "gema:vencimientos@white", "+6 vs. sept.", "up:bad"),
            ("Órdenes abiertas", "23", "", "gema:ordenes@white", "9 para hoy", "flat"),
        ],
        "series_title": "Recargas por mes, últimos 6 meses", "unit": "recargas",
        "series": [("May", 212), ("Jun", 198), ("Jul", 245), ("Ago", 231), ("Sep", 268), ("Oct", 254)],
        "donut_title": "Órdenes de trabajo por estado", "donut": [("Terminadas", 61, "var(--gn-good)"), ("En taller", 23, "var(--gn-info)"), ("Pendientes", 14, "var(--gn-warning)")], "num": [4],
        "table_title": "Matafuegos", "cols": ["Cliente", "N.º de serie", "Tipo", "Capacidad (kg)", "Vence", "Estado"],
        "rows": [
            ("Panadería La Espiga", "AB-22018", "ABC polvo", 5, "12/11/2026", ("Por vencer", "warning")),
            ("Club Atlético Unión", "AB-19244", "CO₂", 3.5, "03/10/2026", ("Vencido", "critical")),
            ("Ferretería Norte", "HL-08871", "ABC polvo", 10, "28/03/2027", ("Vigente", "good")),
            ("Consorcio Belgrano 455", "AB-30117", "Agua", 10, "15/12/2026", ("Avisado", "info")),
            ("Estación de servicio Ruta 3", "HL-11502", "ABC polvo", 50, "09/02/2027", ("Vigente", "good")),
        ],
    },
    {
        "key": "geagro-cereales", "name": "GEAGRO Cereales", "nav": nav_geagro_cereales,
        "mini_nav": [("Dashboard", "geagro-cereales:dashboard"), ("Mis campos", "geagro-cereales:campos"), ("Plan técnico", "geagro-cereales:plan-tecnico")],
        "logo_full": "demo/logos/geagro-cereales-full.svg", "logo_icon": "demo/logos/geagro-cereales-icon.svg",
        "tagline": "Campaña 2025/26", "version_label": "",
        "identity": "Verde campo con acentos amarillos del logo.",
        "swatches": [("Sidebar", "#113f2a", "custom.css:15"), ("Activo", "#0b3422", "custom.css:13"), ("Amarillo", "#c6a400", "custom.css:10"), ("Amarillo claro", "#f3c600", "custom.css:11"), ("Texto amarillo", "#816d09", "custom.css:9"), ("Texto sobre amarillo", "#2b2f24", "jazzmin_custom.css:26"), ("Verde", "#22b24c", "custom.css:18")],
        "fonts": "Titillium Web 300 · 400 · 600 · 700 (custom.css)",
        "eyebrow": "Establecimiento La Aurora · Campaña 2025/26", "title": "Plan técnico", "desc": "Labores por lote, avance de la campaña y alertas.",
        "kpis": [
            ("Superficie sembrada", "1.240", "ha", "geagro-cereales:campos@white", "Soja 62 %, maíz 38 %", "flat"),
            ("Labores del mes", "48", "", "geagro-cereales:plan-tecnico@white", "12 pendientes", "flat"),
            ("Lluvia acumulada", "312", "mm", "geagro-cereales:clima@white", "+18 % vs. promedio", "up:neutral"),
            ("Alertas activas", "2", "", "geagro-cereales:alertas@white", "Granizo y malezas", "flat"),
        ],
        "series_title": "Lluvia mensual, últimos 6 meses (mm)", "unit": "mm",
        "series": [("May", 38), ("Jun", 12), ("Jul", 9), ("Ago", 21), ("Sep", 64), ("Oct", 88)],
        "donut_title": "Superficie por cultivo", "donut": [("Soja", 768), ("Maíz", 472)], "num": [4],
        "table_title": "Labores de la campaña", "cols": ["Lote", "Labor", "Cultivo", "Superficie (ha)", "Fecha", "Estado"],
        "rows": [
            ("Lote 7 · El Bajo", "Siembra", "Soja", 86, "21/10/2026", ("En curso", "info")),
            ("Lote 3 · La Loma", "Pulverización", "Maíz", 120, "18/10/2026", ("Terminada", "good")),
            ("Lote 12 · Ruta 5", "Fertilización", "Maíz", 64, "24/10/2026", ("Pendiente", "warning")),
            ("Lote 1 · Casco", "Siembra", "Soja", 140, "15/10/2026", ("Terminada", "good")),
            ("Lote 9 · Laguna", "Control de malezas", "Soja", 72, "11/10/2026", ("Atrasada", "critical")),
        ],
    },
    {
        "key": "geagro-vid", "name": "GEAGRO Vid", "nav": nav_geagro_vid,
        "mini_nav": [("Dashboard", "geagro-vid:dashboard"), ("Mis viñedos", "geagro-vid:vinedos"), ("Plan técnico", "geagro-vid:plan-tecnico")],
        "logo_full": "demo/logos/geagro-vid-full.svg", "logo_icon": "demo/logos/geagro-vid-icon.svg",
        "tagline": "Campaña 2026/27", "version_label": "",
        "identity": "Violeta vid con verde como acento de estado activo.",
        "swatches": [("Sidebar", "#3F2642", "custom.css:9"), ("Activo", "#2c1830", "custom.css:77"), ("Violeta", "#6b3f6e", "custom.css:10"), ("Hover violeta", "#5a345d", "custom.css:634"), ("Violeta claro", "#906693", "custom.css:11"), ("Verde", "#22b24c", "jazzmin_custom.css:34")],
        "fonts": "Titillium Web 300 · 400 · 600 · 700 (custom.css)",
        "eyebrow": "Finca Los Álamos · Campaña 2026/27", "title": "Lotes", "desc": "Fenología, alertas sanitarias y labores por lote.",
        "kpis": [
            ("Superficie en producción", "86", "ha", "geagro-vid:vinedos@white", "14 lotes", "flat"),
            ("Alertas sanitarias", "3", "", "geagro-vid:alertas@white", "Peronospora: riesgo medio", "flat"),
            ("Grados día acumulados", "412", "GDD", "geagro-vid:clima@white", "+6 % vs. campaña anterior", "up:neutral"),
            ("Labores de la semana", "17", "", "geagro-vid:plan-tecnico@white", "5 pendientes", "flat"),
        ],
        "series_title": "Grados día acumulados por mes (GDD)", "unit": "GDD",
        "series": [("May", 0), ("Jun", 0), ("Jul", 0), ("Ago", 46), ("Sep", 158), ("Oct", 412)],
        "donut_title": "Estado fenológico", "donut": [("Brotación", 9), ("Hojas extendidas", 4), ("Dormancia", 1)], "num": [4],
        "table_title": "Lotes", "cols": ["Lote", "Variedad", "Conducción", "Superficie (ha)", "Fenología", "Sanidad"],
        "rows": [
            ("Lote 4 · Norte", "Malbec", "Espaldero", 6.2, "Brotación", ("Sin riesgo", "good")),
            ("Lote 7 · Río", "Cabernet Sauvignon", "Espaldero", 8.4, "Hojas extendidas", ("Riesgo medio", "warning")),
            ("Lote 11 · Alto", "Torrontés", "Parral", 5.1, "Brotación", ("Riesgo alto", "critical")),
            ("Lote 2 · Casa", "Malbec", "Parral", 7.8, "Brotación", ("Sin riesgo", "good")),
            ("Lote 15 · Oeste", "Bonarda", "Espaldero", 4.6, "Dormancia", ("En monitoreo", "info")),
        ],
    },
]
