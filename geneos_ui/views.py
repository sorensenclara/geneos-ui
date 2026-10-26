import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from . import __version__
from .catalog_data import PRODUCTS
from .conf import SIDEBAR_DEFAULTS, get_config
from .navigation import build_nav


def _catalog_allowed(request):
    flag = get_config()["CATALOG"]
    if flag is not None:
        return bool(flag)
    user = getattr(request, "user", None)
    return settings.DEBUG or bool(user and user.is_staff)


def _kpi(k):
    label, value, unit, icon, trend, direction = k
    arrow, _, tone = direction.partition(":")
    return {"label": label, "value": value, "unit": unit, "icon": icon, "trend": trend,
            "arrow": arrow if arrow in ("up", "down") else "", "tone": tone or "neutral"}


def catalog(request):
    """UI Kit: todos los componentes, variantes y estados, con los cuatro temas.

    ?product=gema elige el producto inicial; el selector de la página cambia
    de tema sin recargar.
    """
    if not _catalog_allowed(request):
        raise PermissionDenied
    keys = [p["key"] for p in PRODUCTS]
    current = request.GET.get("product") or get_config()["PRODUCT"]
    if current not in keys:
        current = keys[0]
    products = []
    for p in PRODUCTS:
        gn = {
            "product": p["key"], "product_name": p["name"], "logo_full": p["logo_full"], "logo_icon": p["logo_icon"],
            "tagline": p["tagline"], "version_label": p["version_label"], "home_url": "#inicio", "sidebar_default": SIDEBAR_DEFAULTS[p["key"]],
        }
        products.append({
            **p,
            "gn": gn,
            "nav_built": build_nav(p["nav"](request), request),
            "series_json": json.dumps([{"label": a, "value": b} for a, b in p["series"]]),
            "donut_json": json.dumps([{"label": d[0], "value": d[1], **({"color": d[2]} if len(d) > 2 else {})} for d in p["donut"]]),
            "kpis_view": [_kpi(k) for k in p["kpis"]],
        })
    active = next(p for p in products if p["key"] == current)
    return render(request, "geneos_ui/catalog/index.html", {
        "products": products,
        "active": active,
        "gn": {**active["gn"], "load_fonts": True, "bridges": []},
        "version": __version__,
        "static_build": request.GET.get("static") == "1",
    })
