from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import include, path


def demo(request):
    rows = [{"n": i, "nombre": f"Registro {i:03d}", "estado": ("Al día", "good") if i % 3 else ("Vencido", "critical")} for i in range(1, 248)]
    order = request.GET.get("o", "")
    if order.lstrip("-") == "nombre":
        rows.sort(key=lambda r: r["nombre"], reverse=order.startswith("-"))
    size = int(request.GET.get("page_size", 25) or 25)
    page = Paginator(rows, size).get_page(request.GET.get("page"))
    return render(request, "demo.html", {"page_obj": page, "crumbs": [("Inicio", "/"), ("Demo", None)]})


urlpatterns = [
    path("", include("geneos_ui.urls")),
    path("demo/", demo, name="demo"),
]
