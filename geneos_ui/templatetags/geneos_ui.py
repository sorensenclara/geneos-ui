"""Template tags de GENEOS UI.

    {% load geneos_ui %}
    {% gn_css %} {% gn_js %}                      recursos de la librería
    {% gn_theme_boot %} {% gn_theme_switch %}     modo claro/oscuro (claro por defecto)
    {% gn_prefs %}                                solapa flotante de preferencias (tema y menú)
    {% gn_icon "i-users" %}                       ícono del sprite
    {% gn_badge "Vencido" "critical" %}           badge de estado
    {% gn_sidebar %}                              sidebar con el menú del producto
    {% gn_breadcrumbs crumbs %}                   [("Inicio", "/"), ("Clientes", None)]
    {% gn_pagination page_obj %}                  paginación que conserva los filtros
    {% gn_sort_th "Nombre" "nombre" %}            encabezado ordenable (?o=nombre / -nombre)
    {% gn_cell "Etiqueta" %}…{% endgn_cell %}     <td data-th> para tablas responsive
    {% gn_query page=2 %}                         querystring actual con cambios
    {% gn_messages_json %}                        mensajes de Django como notificaciones
"""
from django import template
from django.contrib.messages import get_messages
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .. import product_icons
from ..conf import get_config

register = template.Library()

BADGE_KINDS = {"good", "warning", "critical", "info", "neutral", "brand", "solid"}
MESSAGE_KINDS = {"debug": "info", "info": "info", "success": "good", "warning": "warning", "error": "critical"}


@register.simple_tag
def gn_css(product=None, bridges=None):
    cfg = get_config()
    product = product or cfg["PRODUCT"]
    bridges = cfg["BRIDGES"] if bridges is None else [b for b in bridges.split(",") if b]
    files = ["geneos_ui/css/tokens.css", f"geneos_ui/css/themes/{product}.css", "geneos_ui/css/geneos-ui.css"]
    files += [f"geneos_ui/css/bridges/{b}.css" for b in bridges]
    links = []
    if cfg["LOAD_FONTS"]:
        links.append(('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700&display=swap',))
    links += [(static(f),) for f in files]
    return format_html_join("\n", '<link rel="stylesheet" href="{}">', links)


THEME_BOOT = (
    "<script>(function(){var t='light';try{if(localStorage.getItem('gn-theme')==='dark')t='dark';}catch(e){}"
    "document.documentElement.setAttribute('data-gn-theme',t);})();</script>"
)


@register.simple_tag
def gn_theme_boot():
    """Aplica el modo guardado antes de pintar (va en el <head>). Sin preferencia: claro."""
    return mark_safe(THEME_BOOT)


NAV_BOOT = (
    "<script>(function(){var d=document.documentElement,n=d.getAttribute('data-gn-nav-default')||'vertical';"
    "try{var s=localStorage.getItem('gn-nav');if(s==='vertical'||s==='horizontal')n=s;}catch(e){}"
    "d.setAttribute('data-gn-nav',n);})();</script>"
)


@register.simple_tag
def gn_nav_boot():
    """Aplica la disposición de navegación guardada antes de pintar (va en el <head>).

    Sin preferencia guardada usa data-gn-nav-default del <html> (valor del producto).
    """
    return mark_safe(NAV_BOOT)


@register.inclusion_tag("geneos_ui/components/nav_switch.html")
def gn_nav_switch():
    return {}


@register.inclusion_tag("geneos_ui/components/prefs.html")
def gn_prefs():
    """Solapa flotante con las preferencias de interfaz (modo de color y disposición del menú).

    Reúne {% gn_theme_switch %} y {% gn_nav_switch %}, que siguen funcionando igual
    (mismo JS, mismo localStorage). El layout base la incluye en {% block prefs %}.
    """
    return {}


@register.inclusion_tag("geneos_ui/components/theme_switch.html")
def gn_theme_switch():
    return {}


@register.simple_tag
def gn_js():
    return format_html('<script src="{}" defer></script>', static("geneos_ui/js/geneos-ui.js"))


@register.simple_tag
def gn_icon(name, css_class="", label=""):
    if label:
        return format_html('<svg class="gn-icon {}" role="img" aria-label="{}"><use href="#{}"/></svg>', css_class, label, name)
    return format_html('<svg class="gn-icon {}" aria-hidden="true"><use href="#{}"/></svg>', css_class, name)


@register.simple_tag
def gn_nav_icon(entry):
    """Ícono de un ítem del sidebar: original del producto, pendiente o del sprite."""
    if entry.get("icon_static"):
        html = format_html('<img class="gn-nav__icon-img" src="{}" alt="">', static(entry["icon_static"]))
        # navegación horizontal (barra clara): variantes originales normal y activa (GEMA, GELECTRIC)
        # o, si el producto solo tiene el SVG blanco (GEAGRO), ese mismo archivo como máscara
        if entry.get("icon_h_tint"):
            html += format_html('<span class="gn-nav__icon-tint" style="--gn-icon-src: url(&quot;{}&quot;)" aria-hidden="true"></span>',
                                static(entry["icon_static"]))
        if entry.get("icon_h"):
            html += format_html('<img class="gn-nav__icon-h" src="{}" alt="">', static(entry["icon_h"]))
        if entry.get("icon_h_active"):
            html += format_html('<img class="gn-nav__icon-h-active" src="{}" alt="">', static(entry["icon_h_active"]))
        return html
    if entry.get("icon_pending"):
        return mark_safe('<span class="gn-nav__icon-pending" title="Ícono pendiente de diseño" aria-hidden="true"></span>')
    return gn_icon(entry.get("icon") or "i-file")


@register.simple_tag
def gn_product_icon(ref, variant="white", css_class="", label="", set_name=None):
    """{% gn_product_icon "gema:clientes" "base" %} → <img> con el archivo original.

    set_name="backoffice" elige el ícono del backoffice de GEAGRO en lugar del portal.
    """
    if not product_icons.is_product_ref(ref):
        return gn_icon(ref, css_class, label)
    rec = product_icons.resolve(ref, variant, set_name or None)
    if not rec or not rec["file"]:
        return format_html('<span class="gn-product-icon gn-product-icon--pending {}" title="Ícono pendiente de diseño"></span>', css_class)
    return format_html('<img class="gn-product-icon {}" src="{}" alt="{}">', css_class, static(rec["file"]), label)


@register.simple_tag
def gn_badge(label, kind="neutral", dot=False):
    kind = kind if kind in BADGE_KINDS else "neutral"
    return format_html('<span class="gn-badge gn-badge--{}{}">{}</span>', kind, " gn-badge--dot" if dot else "", label)


@register.inclusion_tag("geneos_ui/components/sidebar.html", takes_context=True)
def gn_sidebar(context, nav=None, sidebar_id="gn-sidebar", gn=None, hidden=False):
    gn = gn or context.get("gn", {})
    return {"gn": gn, "nav": nav if nav is not None else gn.get("nav", []), "sidebar_id": sidebar_id, "hidden": hidden, "request": context.get("request")}


@register.inclusion_tag("geneos_ui/components/breadcrumbs.html")
def gn_breadcrumbs(crumbs):
    return {"crumbs": crumbs or []}


@register.simple_tag(takes_context=True)
def gn_query(context, **changes):
    request = context.get("request")
    params = request.GET.copy() if request else None
    if params is None:
        from django.http import QueryDict
        params = QueryDict(mutable=True)
    for k, v in changes.items():
        if v is None:
            params.pop(k, None)
        else:
            params[k] = v
    qs = params.urlencode()
    return "?" + qs if qs else "?"


def _page_window(page, around=1):
    total, current = page.paginator.num_pages, page.number
    pages = sorted({1, total, *range(max(1, current - around), min(total, current + around) + 1)})
    out, prev = [], 0
    for p in pages:
        if p - prev > 1:
            out.append(None)
        out.append(p)
        prev = p
    return out


@register.inclusion_tag("geneos_ui/components/pagination.html", takes_context=True)
def gn_pagination(context, page_obj, sizes="10,25,50,100", param="page", size_param="page_size"):
    return {
        "request": context.get("request"),
        "page": page_obj,
        "window": _page_window(page_obj) if page_obj else [],
        "sizes": [int(s) for s in str(sizes).split(",") if s.strip().isdigit()],
        "param": param,
        "size_param": size_param,
    }


@register.simple_tag(takes_context=True)
def gn_sort_th(context, label, field, param="o", css_class=""):
    request = context.get("request")
    current = request.GET.get(param, "") if request else ""
    if current == field:
        aria, nxt = "ascending", "-" + field
    elif current == "-" + field:
        aria, nxt = "descending", field
    else:
        aria, nxt = None, field
    href = gn_query(context, **{param: nxt, "page": None})
    sort_attr = format_html(' aria-sort="{}"', aria) if aria else ""
    return format_html(
        '<th scope="col" class="{}"{}><a class="gn-table__sort" href="{}">{}<span class="gn-table__sort-icon" aria-hidden="true"></span></a></th>',
        css_class, sort_attr, href, label,
    )


class CellNode(template.Node):
    def __init__(self, label, css, nodelist):
        self.label, self.css, self.nodelist = label, css, nodelist

    def render(self, context):
        label = self.label.resolve(context)
        css = self.css.resolve(context) if self.css else ""
        return format_html('<td data-th="{}"{}>{}</td>', label, format_html(' class="{}"', css) if css else "", mark_safe(self.nodelist.render(context)))


@register.tag(name="gn_cell")
def do_cell(parser, token):
    """{% gn_cell "Estado" %}…{% endgn_cell %} o {% gn_cell "Monto" "is-num" %}…"""
    bits = token.split_contents()
    if len(bits) not in (2, 3):
        raise template.TemplateSyntaxError("gn_cell espera una etiqueta y, opcionalmente, clases CSS.")
    nodelist = parser.parse(("endgn_cell",))
    parser.delete_first_token()
    return CellNode(parser.compile_filter(bits[1]), parser.compile_filter(bits[2]) if len(bits) == 3 else None, nodelist)


@register.simple_tag(takes_context=True)
def gn_messages_json(context):
    request = context.get("request")
    if not request:
        return ""
    data = [{"message": str(m), "kind": MESSAGE_KINDS.get(m.level_tag, "info")} for m in get_messages(request)]
    if not data:
        return ""
    from django.utils.html import json_script
    return json_script(data, "gn-messages")
