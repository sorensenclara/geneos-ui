"""Contenido de ejemplo del catálogo, separado por producto.

Los componentes son los mismos; los textos, datos y procesos son los de cada
sistema. No se mezclan términos entre productos: GELECTRIC (cooperativa
eléctrica), GEMA (matafuegos), GEAGRO Cereales (campañas agrícolas) y GEAGRO Vid
(viñedos). En GEAGRO los ejemplos corresponden al portal del productor; el
backoffice (Jazzmin) aparece solo como referencia en la sección de navegación.

Íconos: ``i-*`` son acciones comunes del sprite; ``producto:módulo`` son los
íconos originales del producto (ver ``product_icons.py``).
"""

# --------------------------------------------------------------------------- formularios
# Cada campo: id, label, kind (input | search | select | date | number | textarea),
# value, options, required, error, help, readonly, full, placeholder.


def _f(id, label, kind="input", **kw):
    return {"id": id, "label": label, "kind": kind, **kw}


EXAMPLES = {
    # ===================================================================== GELECTRIC
    "gelectric": {
        "search_global": "Buscar asociado, suministro o reclamo…",
        "notifications": [
            ("critical", "i-alert", "12 avisos de corte sin notificar", "Hace 12 minutos · Comercial", True),
            ("warning", "i-clock", "5 órdenes de trabajo atrasadas", "Hace 1 hora · Técnico", True),
            ("good", "i-check", "Facturación masiva de octubre terminada", "Hoy 08:40 · Comercial", True),
            ("", "i-user-plus", "Nueva asociada: Laura Méndez", "Ayer · Asociados", False),
        ],
        "type": {
            "page": "Padrón de asociados", "module": "Órdenes de trabajo", "card": "Reclamos abiertos",
            "body": "El suministro 07731-01 tiene un reclamo por baja tensión abierto desde el 21/10/2026.",
            "small": "Fecha de la última lectura", "eyebrow": "Comercial · Facturación",
            "nums": ["$ 184.320,50", "$ 62.115,00"],
        },
        "states": [("Al día", "good"), ("Con deuda", "warning"), ("Aviso de corte", "critical"),
                   ("Reclamo en curso", "info"), ("Dado de baja", "neutral"), ("Residencial", "brand")],
        "breadcrumbs": ["Inicio", "Asociados", "Taller Rossi SRL"],
        "tabs": {
            "label": "Ficha del asociado",
            "dl": [("Titular", "Taller Rossi SRL"), ("N.º de socio", "07731"), ("Categoría", "Comercial"), ("Alta", "14/03/2011")],
            "items": [
                ("Suministros", "3", "3 suministros activos: Av. San Martín 812, Ruta 5 km 3 y depósito Calle 9."),
                ("Cuota capital", "", "Aporte integrado: $ 48.000,00. Quedan 2 cuotas de $ 4.000,00."),
                ("Reclamos", "1", "RC-2026-01452 · Baja tensión · en curso desde el 21/10/2026."),
            ],
        },
        "export": "asociados",
        "buttons": {"primary": "Nuevo asociado", "secondary": "Editar", "ghost": "Configurar",
                    "ok": "Aprobar", "warn": "Revisar", "loading": "Exportando padrón…",
                    "icon_tips": ["Editar asociado", "Ver ficha", "Descargar factura", "Dar de baja"]},
        "form": {
            "title": "Alta de reclamo técnico", "submit": "Guardar reclamo",
            "errors": [("medidor", "N.º de medidor", "no coincide con el suministro elegido."),
                       ("visita", "Fecha de visita", "no puede ser anterior al reclamo.")],
            "fields": [
                _f("asociado", "Asociado", "search", value="Taller Rossi SRL", required=True, full=True, help="Buscá por nombre, N.º de socio o CUIT."),
                _f("suministro", "Suministro", "select", options=["07731-01 · Av. San Martín 812", "07731-02 · Ruta 5 km 3", "07731-03 · Calle 9"], required=True),
                _f("tipo", "Tipo de reclamo", "select", options=["Baja tensión", "Sin suministro", "Medidor dañado", "Poste inclinado"]),
                _f("medidor", "N.º de medidor", value="EM-55120", required=True, error="No coincide con el suministro 07731-01."),
                _f("fecha", "Fecha del reclamo", "date", value="2026-10-21"),
                _f("visita", "Fecha de visita", "date", value="2026-10-19", required=True, error="Es anterior a la fecha del reclamo."),
                _f("numero", "N.º de reclamo", value="RC-2026-01452", readonly=True, help="Se genera automáticamente."),
                _f("obs", "Descripción", "textarea", full=True, placeholder="Qué se observa, desde cuándo, acceso al medidor…"),
            ],
            "checks": ("Avisos al asociado", [("Correo electrónico al titular", "Se envía al confirmar la visita.", True, False),
                                              ("Aviso en la próxima factura", "", False, False),
                                              ("SMS (no disponible)", "", False, True)]),
            "radios": ("Origen", ["Teléfono", "Oficina"]),
            "switch": ("Corte de servicio", "Requiere corte"),
        },
        "search": ("Buscar asociado", "Buscar por nombre, N.º de socio o CUIT"),
        "filters": {
            "pills": [("Todos", 5, ""), ("Con deuda", 1, "warning"), ("Aviso de corte", 1, "critical"), ("Al día", 3, "good")],
            "search": "Buscar asociado o N.º de socio",
            "fields": [("localidad", "Localidad", ["Todas", "Tandil", "Azul"], "Tandil"),
                       ("categoria", "Categoría", ["Todas", "Residencial", "Comercial", "Rural", "Oficial"], "Comercial")],
            "add": [("localidad", "Localidad"), ("categoria", "Categoría"), ("alta", "Fecha de alta"), ("cuit", "CUIT")],
            "defs": [
                {"key": "localidad", "label": "Localidad", "type": "select", "options": [{"value": "tandil", "label": "Tandil"}, {"value": "azul", "label": "Azul"}]},
                {"key": "categoria", "label": "Categoría", "type": "select", "options": [{"value": "res", "label": "Residencial"}, {"value": "com", "label": "Comercial"}, {"value": "rur", "label": "Rural"}]},
                {"key": "alta", "label": "Fecha de alta", "type": "daterange", "params": ["alta_desde", "alta_hasta"]},
                {"key": "cuit", "label": "CUIT", "type": "text", "placeholder": "30-00000000-0"},
            ],
        },
        "empty": ("No hay asociados con estos filtros", "Probá quitar algún filtro o buscar por CUIT o por la dirección del suministro."),
        "row_action": ("i-file-out", "Descargar factura"),
        "attention": [("critical", "i-alert", "Avisos de corte sin notificar", "Comercial", "12"),
                      ("warning", "i-clock", "Órdenes de trabajo atrasadas", "Técnico", "5"),
                      ("good", "i-check", "Retornos de excedentes listos para acreditar", "Asociados", "3")],
        "bars": ("Avance del mes", [("Facturación", 92), ("Cobranzas", 71), ("Lecturas", 58), ("Reclamos resueltos", 34)]),
        "link_card": ("gelectric:asociados", "tile", "Ficha del asociado", "Datos, suministros, cuota capital y reclamos en 8 solapas."),
        "alerts": {
            "good": "Los cambios en la ficha se guardaron correctamente.",
            "warning": ("214 cuentas con deuda vencida", "Revisalas antes de emitir los avisos de corte del viernes."),
            "critical": "No se pudo autorizar la factura B 0003-00012458 en ARCA. Volvé a intentarlo en unos minutos.",
            "info": "Estás viendo la ficha en modo consulta. Para editar, usá el botón Editar.",
        },
        "toasts": [("good", "Orden guardada", "La orden OT-2291 quedó asignada a la cuadrilla Norte."),
                   ("warning", "", "Hay 18 medidores sin lectura en la ruta 4."),
                   ("critical", "Error de conexión", "No se pudo conectar con ARCA."),
                   ("info", "", "La exportación del padrón va a llegar a tu correo en unos minutos.")],
        "confirm": {"button": "Dar de baja asociado", "title": "¿Dar de baja a Taller Rossi SRL?",
                    "text": "Se van a dar de baja también sus 3 suministros. La cuota capital queda pendiente de reintegro.",
                    "action": "Dar de baja", "toast": "Asociado dado de baja."},
        "modal_form": {"button": "Registrar lectura", "title": "Registrar lectura", "submit": "Registrar",
                       "toast": "Lectura registrada: 412 kWh en el período.",
                       "fields": [_f("m-sum", "Suministro", value="07731-01 · Av. San Martín 812", full=True),
                                  _f("m-fecha", "Fecha", "date", value="2026-10-26"),
                                  _f("m-lect", "Lectura (kWh)", value="48.213")]},
        "tooltips": (("i-file", "Imprimir factura"), "Saldo", "Incluye intereses por mora al día de hoy."),
        "steps": ["Datos del titular", "Suministro", "Cuota capital", "Confirmación"],
        "faq": [("¿Cómo se calcula la cuota capital?", "Es el aporte por suministro que define la asamblea. Se factura en cuotas junto con el consumo."),
                ("¿Cuándo se emite un aviso de corte?", "Cuando la deuda supera dos facturas vencidas. El aviso se imprime en la factura siguiente."),
                ("¿Puedo reabrir un reclamo cerrado?", "Sí, durante 15 días desde Reclamos → Cerrados recientes.")],
        "compare": {"tabs": ["Datos", "Suministros"], "badges": [("Al día", "good"), ("Residencial", "brand")],
                    "primary": "Guardar", "secondary": "Editar", "check": "Factura por correo"},
    },

    # ========================================================================== GEMA
    "gema": {
        "search_global": "Buscar cliente, matafuego u orden…",
        "notifications": [
            ("critical", "i-alert", "Vencieron 6 matafuegos sin aviso", "Hace 12 minutos · Vencimientos", True),
            ("warning", "i-clock", "4 pruebas hidráulicas vencen esta semana", "Hace 1 hora · Matafuegos", True),
            ("good", "i-check", "Orden OT-1184 terminada en taller", "Hoy 08:40 · Órdenes de trabajo", True),
            ("", "i-user-plus", "Nuevo cliente: Hotel Del Lago", "Ayer · Clientes", False),
        ],
        "type": {
            "page": "Matafuegos", "module": "Órdenes de trabajo", "card": "Vencimientos del mes",
            "body": "El matafuego AB-22018 vence el 12/11/2026. El cliente todavía no fue avisado.",
            "small": "Fecha de la última recarga", "eyebrow": "Taller · Recargas",
            "nums": ["$ 18.450,00", "$ 6.200,00"],
        },
        "states": [("Vigente", "good"), ("Por vencer", "warning"), ("Vencido", "critical"),
                   ("Avisado", "info"), ("Dado de baja", "neutral"), ("ABC polvo", "brand")],
        "breadcrumbs": ["Inicio", "Matafuegos", "AB-22018"],
        "tabs": {
            "label": "Ficha del matafuego",
            "dl": [("Cliente", "Panadería La Espiga"), ("N.º de serie", "AB-22018"), ("Agente", "ABC polvo · 5 kg"), ("Ubicación", "Interior, salón")],
            "items": [
                ("Recargas", "4", "Última recarga: 12/11/2025. Próximo vencimiento: 12/11/2026."),
                ("Pruebas hidráulicas", "", "Última prueba hidráulica: 15/06/2022. Vence el 15/06/2027."),
                ("Órdenes", "1", "OT-1184 en taller desde el 22/10/2026."),
            ],
        },
        "export": "matafuegos",
        "buttons": {"primary": "Nuevo matafuego", "secondary": "Editar", "ghost": "Configurar",
                    "ok": "Aprobar", "warn": "Revisar", "loading": "Exportando vencimientos…",
                    "icon_tips": ["Editar matafuego", "Ver ficha", "Descargar oblea", "Dar de baja"]},
        "form": {
            "title": "Alta de matafuego", "submit": "Guardar matafuego",
            "errors": [("serie", "Número de serie", "ya existe en otro cliente."),
                       ("vence", "Vencimiento", "no puede ser anterior a la recarga.")],
            "fields": [
                _f("cliente", "Cliente", "search", value="Panadería La Espiga", required=True, full=True, help="Buscá por nombre, CUIT o dirección."),
                _f("serie", "Número de serie", value="AB-19244", required=True, error="Ya existe en Club Atlético Unión."),
                _f("tipo", "Tipo de agente", "select", options=["ABC polvo", "CO₂", "Agua", "Espuma AFFF"]),
                _f("recarga", "Última recarga", "date", value="2026-10-03"),
                _f("vence", "Vencimiento", "date", value="2026-09-30", required=True, error="Es anterior a la última recarga."),
                _f("ph", "Última prueba hidráulica", "date", value="2022-06-15"),
                _f("codigo", "Código interno", value="GEMA-00412", readonly=True, help="Se genera automáticamente."),
                _f("obs", "Observaciones", "textarea", full=True, placeholder="Ubicación en el local, accesos, horario de atención…"),
            ],
            "checks": ("Avisos al cliente", [("WhatsApp 30 días antes", "Se prepara el mensaje; el envío es manual.", True, False),
                                             ("Correo electrónico", "", False, False),
                                             ("SMS (no disponible)", "", False, True)]),
            "radios": ("Ubicación", ["Interior", "Exterior"]),
            "switch": ("Estado", "Activo"),
        },
        "search": ("Buscar matafuego", "Buscar por cliente, N.º de serie o dirección"),
        "filters": {
            "pills": [("Todos", 5, ""), ("Por vencer", 1, "warning"), ("Vencidos", 1, "critical"), ("Vigentes", 2, "good")],
            "search": "Buscar cliente o número de serie",
            "fields": [("localidad", "Localidad", ["Todas", "Tandil", "Azul"], "Tandil"),
                       ("tipo", "Tipo de agente", ["Todos", "ABC polvo", "CO₂", "Agua"], "ABC polvo")],
            "add": [("localidad", "Localidad"), ("tipo", "Tipo de agente"), ("vence", "Fecha de vencimiento"), ("cuit", "CUIT del cliente")],
            "defs": [
                {"key": "localidad", "label": "Localidad", "type": "select", "options": [{"value": "tandil", "label": "Tandil"}, {"value": "azul", "label": "Azul"}]},
                {"key": "tipo", "label": "Tipo de agente", "type": "select", "options": [{"value": "abc", "label": "ABC polvo"}, {"value": "co2", "label": "CO₂"}]},
                {"key": "vence", "label": "Fecha de vencimiento", "type": "daterange", "params": ["vence_desde", "vence_hasta"]},
                {"key": "cuit", "label": "CUIT del cliente", "type": "text", "placeholder": "30-00000000-0"},
            ],
        },
        "empty": ("No hay matafuegos con estos filtros", "Probá quitar algún filtro o buscar por el CUIT o la dirección del cliente."),
        "row_action": ("i-file", "Imprimir oblea"),
        "attention": [("critical", "i-alert", "Matafuegos vencidos sin aviso", "Vencimientos", "6"),
                      ("warning", "i-clock", "Pruebas hidráulicas por vencer", "Matafuegos", "4"),
                      ("good", "i-check", "Recargas terminadas para entregar", "Órdenes de trabajo", "9")],
        "bars": ("Órdenes de la semana", [("Recargas", 82), ("Pruebas hidráulicas", 45), ("Mantenimiento", 63), ("Entregas", 70)]),
        "link_card": ("gema:vencimientos", "base", "Panel de vencimientos", "Matafuegos vencidos y por vencer, con avisos por WhatsApp."),
        "alerts": {
            "good": "La recarga se registró correctamente.",
            "warning": ("41 matafuegos por vencer sin aviso", "Revisalos en el panel de vencimientos antes del viernes."),
            "critical": "No se pudo generar la oblea del matafuego AB-19244. Volvé a intentarlo en unos minutos.",
            "info": "Estás viendo el matafuego en modo consulta. Para editar, usá el botón Editar.",
        },
        "toasts": [("good", "Recarga registrada", "El nuevo vencimiento de AB-22018 es 26/10/2027."),
                   ("warning", "", "Hay 3 matafuegos sin prueba hidráulica cargada."),
                   ("critical", "No se preparó el aviso", "No se pudo armar el mensaje de WhatsApp."),
                   ("info", "", "El listado de vencimientos va a llegar a tu correo en unos minutos.")],
        "confirm": {"button": "Eliminar cliente", "title": "¿Eliminar a Club Atlético Unión?",
                    "text": "Se van a dar de baja también sus 12 matafuegos y el historial de recargas. Esta acción no se puede deshacer.",
                    "action": "Eliminar cliente", "toast": "Cliente eliminado."},
        "modal_form": {"button": "Registrar recarga", "title": "Registrar recarga", "submit": "Registrar",
                       "toast": "Recarga registrada. El nuevo vencimiento es 26/10/2027.",
                       "fields": [_f("m-serie", "Matafuego", value="AB-22018 · Panadería La Espiga", full=True),
                                  _f("m-fecha", "Fecha", "date", value="2026-10-26"),
                                  _f("m-tec", "Técnico", "select", options=["Julián Pereyra", "Marta Ocampo"])]},
        "tooltips": (("i-file", "Imprimir oblea"), "Vence", "Un año desde la última recarga, salvo que la prueba hidráulica venza antes."),
        "steps": ["Cliente", "Matafuego", "Recarga", "Entrega"],
        "faq": [("¿Cómo se calcula el vencimiento?", "Se suma un año a la fecha de la última recarga. Si la prueba hidráulica vence antes, se toma esa fecha."),
                ("¿Quién recibe los avisos?", "El contacto principal del cliente. El mensaje se prepara en el sistema y el envío por WhatsApp es manual."),
                ("¿Cada cuánto se hace la prueba hidráulica?", "Cada cinco años. El sistema avisa 60 días antes.")],
        "compare": {"tabs": ["Datos", "Recargas"], "badges": [("Vigente", "good"), ("ABC polvo", "brand")],
                    "primary": "Guardar", "secondary": "Editar", "check": "Avisar por WhatsApp"},
    },

    # =============================================================== GEAGRO CEREALES
    "geagro-cereales": {
        "search_global": "Buscar lote, labor o alerta…",
        "notifications": [
            ("warning", "i-alert", "Pronóstico de granizo para mañana", "Hace 1 hora · Clima", True),
            ("critical", "i-clock", "Lote 9 · Laguna: control de malezas atrasado", "Hace 3 horas · Plan técnico", True),
            ("good", "i-check", "Siembra terminada en Lote 1 · Casco", "Hoy 08:40 · Calendario", True),
            ("info", "i-info", "Campaña 2026/27 lista para planificar", "Ayer · Campañas", False),
        ],
        "type": {
            "page": "Plan técnico", "module": "Labores de la campaña", "card": "Lotes con alertas",
            "body": "La siembra de soja en el Lote 7 · El Bajo está al 60 %. Faltan 34 ha.",
            "small": "Fecha de siembra", "eyebrow": "Campaña 2025/26 · Soja de primera",
            "nums": ["US$ 1.180,50", "US$   214,00"],
        },
        "states": [("Terminada", "good"), ("Pendiente", "warning"), ("Atrasada", "critical"),
                   ("En curso", "info"), ("Cancelada", "neutral"), ("Soja", "brand")],
        "breadcrumbs": ["Inicio", "Mis campos", "Lote 7 · El Bajo"],
        "tabs": {
            "label": "Ficha del lote",
            "dl": [("Campo", "Establecimiento La Aurora"), ("Superficie", "86 ha"), ("Cultivo", "Soja de primera"), ("Campaña", "2025/26")],
            "items": [
                ("Labores", "6", "6 labores planificadas: 2 terminadas, 1 en curso y 3 pendientes."),
                ("Alertas", "1", "Riesgo de granizo para el 28/10/2026. Sin daños registrados."),
                ("Clima", "", "Lluvia acumulada de la campaña: 312 mm."),
            ],
        },
        "export": "labores-campana-2025-26",
        "buttons": {"primary": "Nueva labor", "secondary": "Editar", "ghost": "Configurar",
                    "ok": "Confirmar labor", "warn": "Revisar", "loading": "Exportando plan…",
                    "icon_tips": ["Editar labor", "Ver lote", "Descargar plan técnico", "Eliminar labor"]},
        "form": {
            "title": "Registrar labor", "submit": "Guardar labor",
            "errors": [("superficie", "Superficie", "supera la del lote."),
                       ("realizada", "Fecha de realización", "no puede ser anterior a la siembra.")],
            "fields": [
                _f("lote", "Lote", "search", value="Lote 12 · Ruta 5", required=True, full=True, help="Buscá por nombre del lote o del campo."),
                _f("labor", "Labor", "select", options=["Fertilización", "Siembra", "Pulverización", "Control de malezas", "Cosecha"], required=True),
                _f("cultivo", "Cultivo", "select", options=["Maíz tardío", "Soja de primera"]),
                _f("superficie", "Superficie (ha)", value="70", required=True, error="El lote tiene 64 ha."),
                _f("planificada", "Fecha planificada", "date", value="2026-10-24"),
                _f("realizada", "Fecha de realización", "date", value="2026-10-02", error="Es anterior a la siembra (15/10/2026)."),
                _f("codigo", "Código de labor", value="LAB-2026-0388", readonly=True, help="Se genera automáticamente."),
                _f("obs", "Observaciones", "textarea", full=True, placeholder="Estado del lote, maquinaria, contratista…"),
            ],
            "checks": ("Avisos", [("Agregar al calendario", "Se ve en Calendario del portal.", True, False),
                                  ("Avisar si hay alerta de clima", "", False, False),
                                  ("Enviar al contratista (no disponible)", "", False, True)]),
            "radios": ("Quién la hace", ["Propia", "Contratista"]),
            "switch": ("Estado", "Labor confirmada"),
        },
        "search": ("Buscar lote", "Buscar por lote, labor o cultivo"),
        "filters": {
            "pills": [("Todas", 5, ""), ("Pendientes", 1, "warning"), ("Atrasadas", 1, "critical"), ("Terminadas", 2, "good")],
            "search": "Buscar lote o labor",
            "fields": [("campana", "Campaña", ["2025/26", "2024/25"], "2025/26"),
                       ("cultivo", "Cultivo", ["Todos", "Soja", "Maíz"], "Soja")],
            "add": [("campana", "Campaña"), ("cultivo", "Cultivo"), ("labor", "Labor"), ("fecha", "Fecha de la labor")],
            "defs": [
                {"key": "campana", "label": "Campaña", "type": "select", "options": [{"value": "2526", "label": "2025/26"}, {"value": "2425", "label": "2024/25"}]},
                {"key": "cultivo", "label": "Cultivo", "type": "select", "options": [{"value": "soja", "label": "Soja"}, {"value": "maiz", "label": "Maíz"}]},
                {"key": "labor", "label": "Labor", "type": "select", "options": [{"value": "siembra", "label": "Siembra"}, {"value": "fert", "label": "Fertilización"}, {"value": "pulv", "label": "Pulverización"}]},
                {"key": "fecha", "label": "Fecha de la labor", "type": "daterange", "params": ["fecha_desde", "fecha_hasta"]},
            ],
        },
        "empty": ("No hay labores con estos filtros", "Probá con otra campaña o quitá el filtro de cultivo."),
        "row_action": ("i-calendar", "Ver en el calendario"),
        "attention": [("critical", "i-clock", "Labores atrasadas", "Plan técnico", "2"),
                      ("warning", "i-alert", "Alertas de clima activas", "Alertas y avisos", "1"),
                      ("good", "i-check", "Lotes con siembra terminada", "Mis campos", "8")],
        "bars": ("Avance de la campaña", [("Siembra", 78), ("Fertilización", 52), ("Pulverización", 40), ("Cosecha", 0)]),
        "link_card": ("geagro-cereales:plan-tecnico", "color", "Plan técnico de la campaña", "Labores por lote, insumos y fechas de la campaña 2025/26."),
        "alerts": {
            "good": "La labor se agregó al plan técnico y al calendario.",
            "warning": ("Pronóstico de granizo para mañana", "Revisá los lotes con soja recién emergida."),
            "critical": "No se pudo actualizar el pronóstico del servicio de clima. Volvé a intentarlo en unos minutos.",
            "info": "Estás viendo la campaña 2025/26. Cambiá de campaña desde el encabezado.",
        },
        "toasts": [("good", "Labor registrada", "Siembra del Lote 7 · El Bajo agregada al calendario."),
                   ("warning", "", "Hay 3 lotes sin labor registrada esta semana."),
                   ("critical", "Error de conexión", "No se pudo conectar con el servicio de clima."),
                   ("info", "", "El informe de la campaña va a llegar a tu correo en unos minutos.")],
        "confirm": {"button": "Eliminar labor", "title": "¿Eliminar la fertilización del Lote 12 · Ruta 5?",
                    "text": "Se quita del plan técnico y del calendario. Los insumos asignados vuelven a quedar disponibles.",
                    "action": "Eliminar labor", "toast": "Labor eliminada."},
        "modal_form": {"button": "Registrar avance", "title": "Registrar avance de labor", "submit": "Registrar",
                       "toast": "Avance registrado: 52 de 86 ha sembradas.",
                       "fields": [_f("m-labor", "Labor", value="Siembra · Lote 7 · El Bajo", full=True),
                                  _f("m-fecha", "Fecha", "date", value="2026-10-26"),
                                  _f("m-ha", "Superficie realizada (ha)", value="52")]},
        "tooltips": (("i-calendar", "Ver en el calendario"), "Costo por ha", "Insumos y labores aplicados en la campaña, en dólares."),
        "steps": ["Campaña", "Lote y cultivo", "Labores", "Confirmación"],
        "faq": [("¿De dónde sale el pronóstico?", "Del servicio de clima configurado para el establecimiento. Se actualiza cada 3 horas."),
                ("¿Cómo cambio de campaña?", "Desde el selector de campaña del encabezado. El plan técnico y el calendario se filtran por esa campaña."),
                ("¿Quién ve las alertas?", "El productor y los técnicos asignados al establecimiento.")],
        "compare": {"tabs": ["Lote", "Labores"], "badges": [("Terminada", "good"), ("Soja", "brand")],
                    "primary": "Guardar", "secondary": "Editar", "check": "Agregar al calendario"},
    },

    # ==================================================================== GEAGRO VID
    "geagro-vid": {
        "search_global": "Buscar lote, labor o alerta…",
        "notifications": [
            ("critical", "i-alert", "Riesgo alto de peronospora en Lote 11 · Alto", "Hace 20 minutos · Alertas sanitarias", True),
            ("warning", "i-alert", "Helada prevista para el jueves", "Hace 2 horas · Clima", True),
            ("good", "i-check", "Atadura terminada en Lote 4 · Norte", "Hoy 08:40 · Plan técnico", True),
            ("info", "i-info", "Brotación registrada en Lote 2 · Casa", "Ayer · Fenología", False),
        ],
        "type": {
            "page": "Lotes", "module": "Plan técnico de la campaña", "card": "Alertas sanitarias",
            "body": "El Lote 7 · Río está en hojas extendidas. Riesgo medio de peronospora por las lluvias.",
            "small": "Fecha del último registro fenológico", "eyebrow": "Campaña 2026/27 · Finca Los Álamos",
            "nums": ["86,0 ha", " 8,4 ha"],
        },
        "states": [("Sin riesgo", "good"), ("Riesgo medio", "warning"), ("Riesgo alto", "critical"),
                   ("En monitoreo", "info"), ("Sin registro", "neutral"), ("Malbec", "brand")],
        "breadcrumbs": ["Inicio", "Mis viñedos", "Lote 7 · Río"],
        "tabs": {
            "label": "Ficha del lote",
            "dl": [("Finca", "Los Álamos"), ("Variedad", "Cabernet Sauvignon"), ("Conducción", "Espaldero"), ("Superficie", "8,4 ha")],
            "items": [
                ("Fenología", "3", "Hojas extendidas desde el 20/10/2026."),
                ("Sanidad", "1", "Riesgo medio de peronospora. Última aplicación: 14/10/2026."),
                ("Labores", "", "Desbrote planificado para el 30/10/2026."),
            ],
        },
        "export": "lotes-finca-los-alamos",
        "buttons": {"primary": "Nueva labor", "secondary": "Editar", "ghost": "Configurar",
                    "ok": "Confirmar labor", "warn": "Revisar", "loading": "Exportando campaña…",
                    "icon_tips": ["Editar lote", "Ver lote", "Descargar plan técnico", "Eliminar labor"]},
        "form": {
            "title": "Registrar observación fenológica", "submit": "Guardar observación",
            "errors": [("fecha", "Fecha de observación", "no puede ser posterior a hoy."),
                       ("porcentaje", "Porcentaje del lote", "debe estar entre 0 y 100.")],
            "fields": [
                _f("lote", "Lote", "search", value="Lote 7 · Río", required=True, full=True, help="Buscá por lote, variedad o finca."),
                _f("estado", "Estado fenológico", "select", options=["Hojas extendidas", "Dormancia", "Brotación", "Floración", "Cuaje", "Envero", "Madurez"], required=True),
                _f("fecha", "Fecha de observación", "date", value="2026-11-02", required=True, error="Es posterior a hoy."),
                _f("porcentaje", "Porcentaje del lote (%)", value="120", error="Debe estar entre 0 y 100."),
                _f("observador", "Observador", "select", options=["Lucía Ferrari", "Martín Giménez"]),
                _f("variedad", "Variedad", value="Cabernet Sauvignon", readonly=True, help="Se toma del lote."),
                _f("obs", "Observaciones", "textarea", full=True, placeholder="Hileras observadas, uniformidad, daños…"),
            ],
            "checks": ("Avisos", [("Actualizar alertas sanitarias", "Recalcula el riesgo con el nuevo estado.", True, False),
                                  ("Agregar al calendario", "", False, False),
                                  ("Enviar al técnico externo (no disponible)", "", False, True)]),
            "radios": ("Método", ["Recorrida a campo", "Foto con muestra"]),
            "switch": ("Sanidad", "Requiere tratamiento"),
        },
        "search": ("Buscar lote", "Buscar por lote, variedad o finca"),
        "filters": {
            "pills": [("Todos", 5, ""), ("Riesgo medio", 1, "warning"), ("Riesgo alto", 1, "critical"), ("Sin riesgo", 2, "good")],
            "search": "Buscar lote o variedad",
            "fields": [("finca", "Finca", ["Los Álamos", "El Molle"], "Los Álamos"),
                       ("variedad", "Variedad", ["Todas", "Malbec", "Cabernet Sauvignon", "Torrontés", "Bonarda"], "Malbec")],
            "add": [("finca", "Finca"), ("variedad", "Variedad"), ("conduccion", "Conducción"), ("observacion", "Fecha de observación")],
            "defs": [
                {"key": "finca", "label": "Finca", "type": "select", "options": [{"value": "alamos", "label": "Los Álamos"}, {"value": "molle", "label": "El Molle"}]},
                {"key": "variedad", "label": "Variedad", "type": "select", "options": [{"value": "malbec", "label": "Malbec"}, {"value": "cab", "label": "Cabernet Sauvignon"}, {"value": "torr", "label": "Torrontés"}]},
                {"key": "conduccion", "label": "Conducción", "type": "select", "options": [{"value": "esp", "label": "Espaldero"}, {"value": "par", "label": "Parral"}]},
                {"key": "observacion", "label": "Fecha de observación", "type": "daterange", "params": ["obs_desde", "obs_hasta"]},
            ],
        },
        "empty": ("No hay lotes con estos filtros", "Probá con otra finca o quitá el filtro de variedad."),
        "row_action": ("i-calendar", "Ver en el calendario"),
        "attention": [("critical", "i-alert", "Lotes con riesgo sanitario alto", "Alertas y avisos", "1"),
                      ("warning", "i-clock", "Labores atrasadas", "Plan técnico", "3"),
                      ("good", "i-check", "Registros fenológicos de la semana", "Fenología", "9")],
        "bars": ("Labores de la campaña", [("Poda", 100), ("Atadura", 85), ("Desbrote", 40), ("Tratamientos", 55)]),
        "link_card": ("geagro-vid:vinedos", "color", "Mis viñedos", "Lotes, variedades y estado fenológico de la finca."),
        "alerts": {
            "good": "La observación fenológica se guardó y las alertas se recalcularon.",
            "warning": ("Riesgo medio de peronospora en 2 lotes", "Las lluvias de esta semana favorecen la infección. Revisá el plan de tratamientos."),
            "critical": "No se pudieron calcular los grados día: faltan datos de la estación meteorológica.",
            "info": "Estás viendo la campaña 2026/27. Cambiá de campaña desde el encabezado.",
        },
        "toasts": [("good", "Observación registrada", "Lote 7 · Río: hojas extendidas en el 80 % del lote."),
                   ("warning", "", "Hay 2 lotes sin registro fenológico esta semana."),
                   ("critical", "Error de conexión", "No se pudo conectar con la estación meteorológica."),
                   ("info", "", "El informe de la campaña va a llegar a tu correo en unos minutos.")],
        "confirm": {"button": "Eliminar labor", "title": "¿Eliminar el desbrote del Lote 11 · Alto?",
                    "text": "Se quita del plan técnico y del calendario de la campaña.",
                    "action": "Eliminar labor", "toast": "Labor eliminada."},
        "modal_form": {"button": "Registrar tratamiento", "title": "Registrar tratamiento sanitario", "submit": "Registrar",
                       "toast": "Tratamiento registrado. Lote 11 · Alto pasa a monitoreo.",
                       "fields": [_f("m-lote", "Lote", value="Lote 11 · Alto · Torrontés", full=True),
                                  _f("m-fecha", "Fecha", "date", value="2026-10-26"),
                                  _f("m-prod", "Producto", "select", options=["Oxicloruro de cobre", "Azufre mojable"])]},
        "tooltips": (("i-calendar", "Ver en el calendario"), "Grados día", "Suma de temperaturas medias sobre 10 °C desde el 1 de agosto."),
        "steps": ["Finca", "Lote", "Labores", "Confirmación"],
        "faq": [("¿Cómo se calcula el riesgo de peronospora?", "Con la regla de los tres 10 (10 °C, 10 mm de lluvia y brotes de 10 cm) y el pronóstico de los próximos días."),
                ("¿Qué escala fenológica se usa?", "La de Eichhorn-Lorenz modificada (E-L)."),
                ("¿Quién recibe las alertas sanitarias?", "El productor y los técnicos asignados a la finca.")],
        "compare": {"tabs": ["Lote", "Fenología"], "badges": [("Sin riesgo", "good"), ("Malbec", "brand")],
                    "primary": "Guardar", "secondary": "Editar", "check": "Agregar al calendario"},
    },
}

# ---------------------------------------------------------------- GEAGRO: backoffice
# Referencia del administrador Jazzmin (no se modifica). Apps y enlaces tomados de
# JAZZMIN_SETTINGS en agro_system/settings/base.py de cada rama; íconos de
# static/img/icons/ asignados por app en "icons".
BACKOFFICE = {
    "geagro-cereales": [
        ("Dashboard", "dashboard", []),
        ("Operaciones", "operaciones", ["Calendario de OP", "Insumos por campaña", "Presupuesto vs real", "Listado de órdenes"]),
        ("Acopio", "acopio", []),
        ("Alertas", "alertas", []),
        ("Autenticación y autorización", "autenticacion", []),
        ("Datos del clima", "clima", []),
        ("Insumos", "insumos", ["Gráficos de stock", "Catálogo de insumos"]),
        ("Parámetros", "parametros", []),
        ("Productores", "productores", []),
        ("Usuarios", "usuarios", []),
        ("Ventas", "ventas", []),
    ],
    "geagro-vid": [
        ("Dashboard", "dashboard", []),
        ("Operaciones", "operaciones", ["Calendario de OP"]),
        ("Alertas", "alertas", []),
        ("Autenticación y autorización", "autenticacion", []),
        ("Datos del clima", "clima", []),
        ("Insumos", "insumos", ["Gráficos de stock"]),
        ("Monitoreo de cultivo", "monitoreo", []),
        ("Parámetros", "parametros", []),
        ("Productores", "productores", []),
        ("Usuarios", "usuarios", []),
        ("Ventas", "ventas", []),
    ],
}

# Funcionalidades del portal que existen en el código pero no tienen navegación activa (docs/pendientes.md)
PENDING_FEATURES = {
    "geagro-cereales": [("Historial", "Existe pages/historial.html, pero no tiene URL ni figura en el sidebar. No se agrega hasta que tenga navegación activa.")],
    "geagro-vid": [("Historial", "Existe pages/historial.html, pero no tiene URL ni figura en el sidebar. No se agrega hasta que tenga navegación activa."),
                   ("Íconos de Fenología e Informes", "Necesitan íconos originales definitivos; mientras tanto el sidebar muestra el marcador pendiente.")],
}

# Sprite de interfaz: los 47 de GELECTRIC (core/templates/core/_icon_sprite.html) y
# las acciones genéricas que agregó GENEOS UI.
GELECTRIC_SPRITE = (
    "i-alert-bubble i-arrowleft i-arrowup i-bars i-bell i-bolt i-book i-calc i-calendar i-cart i-cash i-check "
    "i-chevdown i-chevright i-clock i-coins i-edit i-eye i-eye-off i-file i-file-out i-filter i-flag i-gauge i-gear "
    "i-help i-home i-idcard i-lock i-logout i-mail i-map i-menu i-more i-percent i-phone i-piechart i-plug i-plus "
    "i-receipt i-search i-spinner i-user i-user-plus i-users i-wrench i-x"
).split()
# íconos del sprite de GELECTRIC que representan sus módulos o su negocio: solo se usan en GELECTRIC
GELECTRIC_ONLY = "i-bolt i-users i-cart i-calc i-receipt i-piechart i-percent i-cash i-plug i-gauge i-wrench i-coins i-bars i-idcard i-map i-phone".split()
