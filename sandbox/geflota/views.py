from django.core.paginator import Paginator
from django.shortcuts import render

MODELOS = ["Mercedes-Benz Sprinter", "Iveco Daily", "Ford Ranger", "Toyota Hilux", "Volkswagen Amarok", "Renault Kangoo"]
ESTADOS = [("En servicio", "good"), ("En taller", "warning"), ("Fuera de servicio", "critical")]


def vehiculos_data():
    rows = []
    for i in range(1, 58):
        estado = ESTADOS[0] if i % 5 else ESTADOS[1] if i % 2 else ESTADOS[2]
        rows.append({"patente": f"AF {100 + i * 7:03d} {chr(65 + i % 26)}{chr(66 + i % 24)}", "modelo": MODELOS[i % len(MODELOS)],
                     "km": f"{(i * 13711) % 240000:,}".replace(",", "."), "estado": estado})
    return rows


def inicio(request):
    kpis = [("Vehículos activos", "48", "de 57"), ("En taller", "6", "3 vencen esta semana"), ("Km del mes", "182.400", "+4 % vs. sept.")]
    return render(request, "geflota/inicio.html", {"kpis": kpis, "crumbs": [("Inicio", None)]})


def vehiculos(request):
    rows = vehiculos_data()
    order = request.GET.get("o", "")
    if order.lstrip("-") in ("patente", "modelo"):
        rows.sort(key=lambda r: r[order.lstrip("-")], reverse=order.startswith("-"))
    page = Paginator(rows, int(request.GET.get("page_size", 10) or 10)).get_page(request.GET.get("page"))
    return render(request, "geflota/vehiculos.html", {"page_obj": page, "crumbs": [("Inicio", "/geflota/"), ("Vehículos", None)]})


def pendiente(request, seccion):
    return render(request, "geflota/inicio.html", {"kpis": [], "crumbs": [("Inicio", "/geflota/"), (seccion.capitalize(), None)]})


MANTENIMIENTO = [
    {"label": "Órdenes de servicio", "href": "/geflota/s/ordenes/", "icon": "i-wrench", "description": "Pedidos al taller y su estado"},
    {"label": "Vencimientos de VTV, seguro y patente", "href": "/geflota/s/vencimientos/", "icon": "i-calendar",
     "description": "Lo que vence en los próximos 30 días"},
    {"label": "Plan de mantenimiento preventivo por kilometraje", "icon": "i-gauge", "status": "En definición"},
    {"label": "Historial de reparaciones", "status": "En definición"},
]


def mantenimiento(request):
    return render(request, "geflota/mantenimiento.html", {"items": MANTENIMIENTO, "crumbs": [("Inicio", "/geflota/"), ("Mantenimiento", None)]})


def ayuda(request):
    return render(request, "geflota/inicio.html", {"kpis": [], "crumbs": [("Inicio", "/geflota/"), ("Ayuda y soporte", None)]})
