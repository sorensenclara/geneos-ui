import json
import re
from pathlib import Path

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from . import __version__
from .catalog_data import PRODUCTS
from .catalog_examples import BACKOFFICE, EXAMPLES, GELECTRIC_ONLY, GELECTRIC_SPRITE, PENDING_FEATURES
from .conf import get_config
from .presets import PRESETS
from .navigation import build_nav
from . import product_icons


def _catalog_allowed(request):
    flag = get_config()["CATALOG"]
    if flag is not None:
        return bool(flag)
    user = getattr(request, "user", None)
    return settings.DEBUG or bool(user and user.is_staff)


def _kpi(k):
    label, value, unit, icon, trend, direction = k
    arrow, _, tone = direction.partition(":")
    ref, _, variant = icon.partition("@")
    return {"label": label, "value": value, "unit": unit, "icon": ref, "icon_variant": variant or "white", "trend": trend,
            "arrow": arrow if arrow in ("up", "down") else "", "tone": tone or "neutral"}


VARIANT_LABELS = {
    "tile": "Tile con fondo", "white": "Blanco", "active": "Activo", "base": "Base", "color": "Color",
    "simple": "Simple", "simple-alt": "Simple (alternativa)", "tile-vid": "Tile VID", "tile-png": "Tile PNG",
    "simple-png": "Simple PNG", "white-png": "Blanco PNG", "isologo": "Isologo",
}
PRODUCT_LABELS = {"gelectric": "GELECTRIC", "gema": "GEMA", "geagro": "GEAGRO (Cereales y Vid)",
                  "geagro-cereales": "GEAGRO Cereales", "geagro-vid": "GEAGRO Vid"}
STATUS_ORDER = {"activo": 0, "pendiente": 1, "disponible": 2}
SET_LABELS = {"modulos": "Módulos", "menu": "Menú", "marca": "Marca", "portal": "Portal del productor",
              "backoffice": "Backoffice (Jazzmin)", "vid": "Línea VID", "png": "Set PNG"}


def icon_inventory():
    """Registros del manifiesto preparados para la sección Iconografía del catálogo."""
    rows = []
    for i in product_icons.icons():
        prod = i["product"]
        rows.append({
            **i,
            "product_label": PRODUCT_LABELS[prod],
            # GEAGRO compartido aparece al filtrar por Cereales o por Vid
            "filter_products": "geagro-cereales geagro-vid" if prod == "geagro" else prod,
            "theme": "geagro-cereales" if prod == "geagro" else prod,
            "variant_label": VARIANT_LABELS.get(i["variant"], i["variant"]),
            "set_label": SET_LABELS.get(i["set"], i["set"]),
            "dark_thumb": i["variant"] in ("white", "white-png"),
            "origin": i["source"][0] if i["source"] else None,
            "origin_branches": " · ".join(s["branch"] for s in i["source"]),
        })
    rows.sort(key=lambda r: (list(PRODUCT_LABELS).index(r["product"]), STATUS_ORDER[r["status"]], r["module"], r["variant"]))
    modules = sorted({(r["module"], r["module_label"]) for r in rows}, key=lambda m: m[1])
    counts = {k: sum(1 for r in rows if r["status"] == k) for k in ("activo", "disponible", "pendiente")}
    sets = [(k, v) for k, v in SET_LABELS.items() if any(r["set"] == k for r in rows)]
    return {"rows": rows, "modules": modules, "sets": sets, "counts": counts, "total": len(rows),
            "files": sum(1 for r in rows if r["file"])}


SPRITE_FILE = Path(__file__).parent / "templates" / "geneos_ui" / "components" / "icon_sprite.html"


def sprite_groups():
    """Sprite de interfaz: el set original de GELECTRIC y las acciones agregadas por GENEOS UI."""
    ids = re.findall(r'<symbol id="(i-[\w-]+)"', SPRITE_FILE.read_text(encoding="utf-8"))
    gel = [{"id": i, "only": i in GELECTRIC_ONLY} for i in ids if i in GELECTRIC_SPRITE]
    kit = [{"id": i, "only": False} for i in ids if i not in GELECTRIC_SPRITE]
    return {"gelectric": gel, "kit": kit}


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
            "tagline": p["tagline"], "version_label": p["version_label"], "home_url": "#inicio", "sidebar_default": PRESETS[p["key"]]["SIDEBAR_DEFAULT"],
            "sidebar_legacy_key": PRESETS[p["key"]].get("SIDEBAR_LEGACY_KEY"),
            "logo_topbar": p["logo_topbar"], "nav_layout": PRESETS[p["key"]]["NAV_LAYOUT"],
        }
        products.append({
            **p,
            "gn": gn,
            "nav_built": build_nav(p["nav"](request), request),
            "series_json": json.dumps([{"label": a, "value": b} for a, b in p["series"]]),
            "donut_json": json.dumps([{"label": d[0], "value": d[1], **({"color": d[2]} if len(d) > 2 else {})} for d in p["donut"]]),
            "kpis_view": [_kpi(k) for k in p["kpis"]],
            "ex": EXAMPLES[p["key"]],
            "filter_defs_json": json.dumps(EXAMPLES[p["key"]]["filters"]["defs"], ensure_ascii=False),
            "pending_features": PENDING_FEATURES.get(p["key"], []),
            "backoffice": [{"label": label, "ref": f"{p['key']}:{module}", "children": children,
                            "pending": (product_icons.resolve(f"{p['key']}:{module}", set_name="backoffice") or {}).get("status") == "pendiente"}
                           for label, module, children in BACKOFFICE.get(p["key"], [])],
        })
    active = next(p for p in products if p["key"] == current)
    return render(request, "geneos_ui/catalog/index.html", {
        "products": products,
        "active": active,
        "gn": {**active["gn"], "load_fonts": True, "bridges": []},
        "version": __version__,
        "static_build": request.GET.get("static") == "1",
        "icon_inventory": icon_inventory(),
        "sprite_groups": sprite_groups(),
        "search_placeholders": json.dumps({p["key"]: EXAMPLES[p["key"]]["search_global"] for p in PRODUCTS}, ensure_ascii=False),
    })
