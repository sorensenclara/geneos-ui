"""Chequeos de Django (``manage.py check``) para GENEOS_UI.

E001  PRODUCT con formato inválido
E002  puente desconocido
E003  producto sin preset y sin THEME_CSS (la página quedaría sin colores)
E004  un archivo de THEME_CSS no está en los estáticos
E005  NAV_ICONS inválido
W001  SIDEBAR_DEFAULT inválido (se usa el del preset)
W002  un logo declarado no está en los estáticos
W003  el producto sobrescribe un template de componente de la biblioteca
      (deja de recibir las mejoras de ese componente al actualizar)
"""
from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.checks import Error, Warning, register

from .conf import BRIDGES, NAV_ICON_MODES, PRODUCT_RE, SIDEBAR_STATES, get_config, user_settings

PACKAGE_TEMPLATES = Path(__file__).resolve().parent / "templates"
COMPONENT_TEMPLATES = ("layouts/app.html", "layouts/auth.html", "components/sidebar.html", "components/prefs.html",
                       "components/theme_switch.html", "components/nav_switch.html", "components/pagination.html",
                       "components/breadcrumbs.html", "components/topbar_brand.html", "components/icon_sprite.html")


def _valid_nav_icons(value):
    if value in NAV_ICON_MODES:
        return True
    return isinstance(value, dict) and set(value) <= {"rest", "active"} and bool(value.get("rest"))


@register()
def check_geneos_ui(app_configs, **kwargs):
    cfg = get_config()
    user = user_settings()
    problems = []
    product = cfg["PRODUCT"]
    if not isinstance(product, str) or not PRODUCT_RE.fullmatch(product):
        problems.append(Error(
            f"GENEOS_UI['PRODUCT'] = {product!r} no es un identificador válido.",
            hint="Minúsculas, números y guiones; empieza con una letra (p. ej. 'geflota').",
            id="geneos_ui.E001",
        ))
    for b in cfg["BRIDGES"]:
        if b not in BRIDGES:
            problems.append(Error(f"Puente desconocido: {b!r}.", hint="Valores válidos: " + ", ".join(BRIDGES), id="geneos_ui.E002"))
    if not cfg["HAS_PRESET"] and not cfg["THEME_CSS"]:
        problems.append(Error(
            f"El producto {product!r} no tiene preset ni GENEOS_UI['THEME_CSS'].",
            hint="Declarar THEME_CSS con el CSS de sus colores --gn-c-* (ver docs/nuevo-producto.md).",
            id="geneos_ui.E003",
        ))
    for path in cfg["THEME_CSS"]:
        if not finders.find(path):
            problems.append(Error(f"No se encuentra el CSS del tema {path!r} en los estáticos.", id="geneos_ui.E004"))
    if not _valid_nav_icons(cfg["NAV_ICONS"]):
        problems.append(Error(
            f"GENEOS_UI['NAV_ICONS'] = {cfg['NAV_ICONS']!r} no es válido.",
            hint="'tint', 'as-is' o {'rest': variante, 'active': variante o None}.",
            id="geneos_ui.E005",
        ))
    if user.get("SIDEBAR_DEFAULT") not in (None, *SIDEBAR_STATES):
        problems.append(Warning("GENEOS_UI['SIDEBAR_DEFAULT'] debe ser 'expanded' o 'collapsed'.", id="geneos_ui.W001"))
    for key in ("LOGO_FULL", "LOGO_ICON", "LOGO_TOPBAR"):
        if user.get(key) and not finders.find(user[key]):
            problems.append(Warning(f"GENEOS_UI['{key}'] = {user[key]!r} no está en los estáticos.", id="geneos_ui.W002"))
    problems += _overridden_templates()
    return problems


def _overridden_templates():
    from django.template import TemplateDoesNotExist
    from django.template.loader import get_template

    out = []
    for name in COMPONENT_TEMPLATES:
        try:
            origin = Path(get_template(f"geneos_ui/{name}").origin.name).resolve()
        except (TemplateDoesNotExist, AttributeError, TypeError):
            continue
        if PACKAGE_TEMPLATES not in origin.parents:
            out.append(Warning(
                f"El template geneos_ui/{name} está sobrescrito en {origin}.",
                hint="Ese componente deja de recibir las mejoras de la biblioteca. Usar los bloques del layout "
                     "o silenciar con SILENCED_SYSTEM_CHECKS = ['geneos_ui.W003'] si es intencional.",
                id="geneos_ui.W003",
            ))
    return out
