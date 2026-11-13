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

from .. import __version__, presets, product_icons
from ..conf import get_config

register = template.Library()

BADGE_KINDS = {"good", "warning", "critical", "info", "neutral", "brand", "solid"}
MESSAGE_KINDS = {"debug": "info", "info": "info", "success": "good", "warning": "warning", "error": "critical"}


def _asset(path, cfg):
    url = static(path)
    if cfg["STATIC_VERSION_QUERY"]:
        url += ("&" if "?" in url else "?") + "v=" + __version__
    return url


def _nonce(context):
    """Nonce de CSP del request (django-csp o el CSP de Django 6), si lo hay."""
    if not context:
        return ""
    nonce = context.get("csp_nonce")
    request = context.get("request")
    if not nonce and request is not None:
        nonce = getattr(request, "csp_nonce", None)
    return str(nonce) if nonce else ""


def _with_nonce(script, context):
    nonce = _nonce(context)
    if nonce:
        script = script.replace("<script>", format_html('<script nonce="{}">', nonce), 1)
    return mark_safe(script)


def _nonce_attr(context):
    nonce = _nonce(context)
    return format_html(' nonce="{}"', nonce) if nonce else ""


@register.simple_tag(takes_context=True)
def gn_css(context, product=None, bridges=None):
    """Fuente, tokens, tema del producto, componentes y puentes, en ese orden."""
    cfg = get_config()
    if product and product != cfg["PRODUCT"]:
        themes = presets.preset(product).get("THEME_CSS") or [f"geneos_ui/css/themes/{product}.css"]
    else:
        product = cfg["PRODUCT"]
        themes = cfg["THEME_CSS"]
    bridges = cfg["BRIDGES"] if bridges is None else [b for b in bridges.split(",") if b]
    links = []
    font = cfg["FONT_CSS"]
    if font:
        links.append((font if font.startswith(("http://", "https://", "//")) else static(font),))
    links.append((_asset("geneos_ui/css/tokens.css", cfg),))
    links += [(static(t),) for t in themes]
    links.append((_asset("geneos_ui/css/geneos-ui.css", cfg),))
    links += [(_asset(f"geneos_ui/css/bridges/{b}.css", cfg),) for b in bridges]
    html = format_html_join("\n", '<link rel="stylesheet" href="{}">', links)
    rgb = cfg["BOOTSTRAP_RGB"] if product == cfg["PRODUCT"] else {}
    if rgb and "bootstrap5" in bridges:
        # fuera de la @layer y con :root[…] para ganarle a Bootstrap en cualquier orden
        decls = format_html_join(" ", "--bs-{}-rgb: {};", sorted(rgb.items()))
        html += format_html('\n<style{}>:root[data-gn-product="{}"] {{ {} }}</style>', _nonce_attr(context), product, decls)
    legacy = cfg["LEGACY_CSS"] if product == cfg["PRODUCT"] else []
    if legacy:
        # CSS existente del producto en la capa "legacy", después de la biblioteca: sus clases se ven
        # como siempre, pero sus reglas de <body> no pisan el layout ni el modo oscuro de GENEOS UI
        imports = format_html_join("\n", '@import url("{}") layer(legacy);', [(static(p),) for p in legacy])
        html += format_html('\n<style{}>@layer geneos-ui, legacy;\n{}\n'
                            'body.gn-root {{ background: var(--gn-bg); color: var(--gn-text); font-family: var(--gn-font); }}</style>',
                            _nonce_attr(context), imports)
    return html


THEME_BOOT = (
    "<script>(function(){var t='light';try{if(localStorage.getItem('gn-theme')==='dark')t='dark';}catch(e){}"
    "document.documentElement.setAttribute('data-gn-theme',t);})();</script>"
)


@register.simple_tag(takes_context=True)
def gn_theme_boot(context=None):
    """Aplica el modo guardado antes de pintar (va en el <head>). Sin preferencia: claro.

    Si el producto declara VARIANTS, aplica también la variante de color que eligió el
    usuario (``localStorage["gn-variant:<producto>"]``), migrando una vez la clave vieja.
    """
    html = _with_nonce(THEME_BOOT, context)
    cfg = get_config()
    if cfg["VARIANTS"]:
        html += _with_nonce(variant_boot(cfg), context)
    return html


NAV_BOOT = (
    "<script>(function(){var d=document.documentElement,n=d.getAttribute('data-gn-nav-default')||'vertical';"
    "try{var s=localStorage.getItem('gn-nav');if(s==='vertical'||s==='horizontal')n=s;}catch(e){}"
    "d.setAttribute('data-gn-nav',n);})();</script>"
)


def variant_boot(cfg):
    import json
    allowed = [k for k, _ in cfg["VARIANTS"]]
    legacy = cfg.get("VARIANT_LEGACY") or {}
    data = json.dumps({"p": cfg["PRODUCT"], "a": allowed, "lk": legacy.get("key"), "lv": legacy.get("values") or {}},
                      ensure_ascii=True).replace("<", "\\u003c")
    return ("<script>(function(c){var d=document.documentElement,k='gn-variant:'+c.p,v=null;"
            "try{v=localStorage.getItem(k);if(v===null&&c.lk){var o=localStorage.getItem(c.lk);"
            "if(o!==null&&o in c.lv){v=c.lv[o];localStorage.setItem(k,v);}}}catch(e){}"
            "if(v!==null&&c.a.indexOf(v)!==-1){if(v)d.setAttribute('data-gn-variant',v);else d.removeAttribute('data-gn-variant');}"
            "})(" + data + ");</script>")


@register.simple_tag(takes_context=True)
def gn_nav_boot(context=None):
    """Aplica la disposición de navegación guardada antes de pintar (va en el <head>).

    Sin preferencia guardada usa data-gn-nav-default del <html> (valor del producto).
    """
    return _with_nonce(NAV_BOOT, context)


@register.inclusion_tag("geneos_ui/components/nav_switch.html")
def gn_nav_switch():
    return {}


@register.inclusion_tag("geneos_ui/components/prefs.html")
def gn_prefs(products=None):
    """Solapa flotante con las preferencias de interfaz (modo de color y disposición del menú).

    Reúne {% gn_theme_switch %} y {% gn_nav_switch %}, que siguen funcionando igual
    (mismo JS, mismo localStorage). El layout base la incluye en {% block prefs %}.
    Si el producto declara VARIANTS, agrega el grupo «Color». ``products`` (catálogo):
    lista de identificadores para los que se dibuja un grupo cada uno; se ve el del
    producto activo.
    """
    from ..conf import variants_for
    cfg = get_config()
    keys = products if products is not None else [cfg["PRODUCT"]]
    groups = [{"product": p, "variants": variants_for(p, cfg)} for p in keys]
    return {"variant_groups": [g for g in groups if g["variants"]]}


@register.inclusion_tag("geneos_ui/components/theme_switch.html")
def gn_theme_switch():
    return {}


@register.simple_tag
def gn_js():
    return format_html('<script src="{}" defer></script>', _asset("geneos_ui/js/geneos-ui.js", get_config()))


@register.simple_tag
def gn_chartjs_js():
    """Adaptador opcional de Chart.js; cargar Chart.js 4 antes de este script."""
    return format_html('<script src="{}" defer></script>', _asset("geneos_ui/js/chartjs-adapter.js", get_config()))


@register.simple_tag
def gn_datetime_js():
    """Scripts de los selectores de fecha y hora (Cally + datetime.js) para páginas sin {{ form.media }}."""
    from ..widgets import datetime_media

    return mark_safe(str(datetime_media()))


@register.simple_tag
def gn_icon(name, css_class="", label=""):
    if label:
        return format_html('<svg class="gn-icon {}" role="img" aria-label="{}"><use href="#{}"/></svg>', css_class, label, name)
    return format_html('<svg class="gn-icon {}" aria-hidden="true"><use href="#{}"/></svg>', css_class, name)


@register.simple_tag(takes_context=True)
def gn_nav_icon(context, entry):
    """Ícono de un ítem del sidebar: original del producto, pendiente o del sprite."""
    if entry.get("icon_static"):
        html = format_html('<img class="gn-nav__icon-img" src="{}" alt="">', static(entry["icon_static"]))
        gn = context.get("gn") or {}
        if gn.get("sidebar_icons") == "tint":
            # SIDEBAR_ICONS = "tint": el mismo SVG como máscara, con los colores del sidebar (reposo y activo)
            html += format_html('<span class="gn-nav__icon-stint" style="--gn-icon-src: url(&quot;{}&quot;)" aria-hidden="true"></span>',
                                static(entry["icon_static"]))
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


# --------------------------------------------------------------- 0.4.0
@register.simple_tag
def gn_any_icon(ref, css_class="", label=""):
    """Un ícono a partir de una referencia: "i-nombre" (sprite), "producto:módulo"
    (manifiesto de íconos originales) o una ruta de estáticos (``icon - Módulo.svg``)."""
    if not ref:
        return ""
    if ref.startswith("i-"):
        return gn_icon(ref, css_class, label)
    if product_icons.is_product_ref(ref):
        # sobre fondo claro: la variante de color original del producto, si existe; si no, nada
        for variant in ("tile", "base", "color"):  # "simple" es del backoffice de GEAGRO: no se mezcla
            rec = product_icons.resolve(ref, variant)
            if rec and rec.get("file") and rec.get("status") != "pendiente":
                return format_html('<img class="gn-any-icon {}" src="{}" alt="{}">', css_class, static(rec["file"]), label)
        return ""
    return format_html('<img class="gn-any-icon {}" src="{}" alt="{}">', css_class, static(ref), label)


LINK_KEYS = ("label", "href", "description", "icon", "status", "status_kind")


def _link(item):
    return {k: (item.get(k) if isinstance(item, dict) else getattr(item, k, None)) for k in LINK_KEYS}


class LinkListNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist, self.kwargs = nodelist, kwargs

    def render(self, context):
        kw = {k: v.resolve(context) for k, v in self.kwargs.items()}
        items = [_link(i) for i in (kw.get("items") or [])]
        if self.nodelist is not None:
            with context.push(_gn_link_items=items):
                self.nodelist.render(context)
        status = kw.get("empty_status")
        if status:
            items = [{**i, "status": i["status"] or (None if i["href"] else status)} for i in items]
        columns = kw.get("columns") or 2
        return template.loader.render_to_string("geneos_ui/components/link_list.html", {
            "items": items, "columns": columns if columns in (1, 2, 3) else 2,
            "label": kw.get("label"), "css_class": kw.get("css_class"),
        })


def _kwargs(parser, bits):
    out = {}
    for bit in bits:
        key, _, value = bit.partition("=")
        if not value:
            raise template.TemplateSyntaxError(f"Argumento sin nombre: {bit!r} (se usa clave=valor)")
        out[key] = parser.compile_filter(value)
    return out


@register.tag(name="gn_link_list")
def do_link_list(parser, token):
    """Lista de funcionalidades: dos columnas en escritorio, una en el celular.

        {% gn_link_list items=funcionalidades columns=2 empty_status="En definición" %}

        {% gn_link_list columns=2 %}
          {% url "core:asociados_list" as u %}{% gn_link_item label="Ficha del asociado" href=u icon="i-idcard" description="…" %}
        {% endgn_link_list %}

    Cada ítem: label (completo, hasta dos líneas en el celular), href (sin href no es un
    enlace), description, icon ("i-…", "producto:módulo" o ruta de estáticos; si no hay,
    no se dibuja ninguno), status y status_kind (un badge, p. ej. "En definición").
    ``empty_status`` marca los ítems sin enlace.
    """
    bits = token.split_contents()
    kwargs = _kwargs(parser, bits[1:])
    nodelist = None
    if "items" not in kwargs:
        nodelist = parser.parse(("endgn_link_list",))
        parser.delete_first_token()
    return LinkListNode(nodelist, kwargs)


class LinkItemNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        bucket = context.get("_gn_link_items")
        if bucket is None:
            raise template.TemplateSyntaxError("{% gn_link_item %} va dentro de {% gn_link_list %}…{% endgn_link_list %}")
        bucket.append(_link({k: v.resolve(context) for k, v in self.kwargs.items()}))
        return ""


@register.tag(name="gn_link_item")
def do_link_item(parser, token):
    return LinkItemNode(_kwargs(parser, token.split_contents()[1:]))


class PageHeadNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist, self.kwargs = nodelist, kwargs

    def render(self, context):
        kw = {k: v.resolve(context) for k, v in self.kwargs.items()}
        actions = mark_safe(self.nodelist.render(context).strip()) if self.nodelist is not None else ""
        return template.loader.render_to_string("geneos_ui/components/page_head.html", {
            "title": kw.get("title"), "subtitle": kw.get("subtitle"), "eyebrow": kw.get("eyebrow"),
            "icon": kw.get("icon"), "actions": actions,
        })


@register.tag(name="gn_page_head")
def do_page_head(parser, token):
    """Encabezado de página con ícono opcional (el original del módulo) y acciones.

        {% gn_page_head title=module.name subtitle="10 funcionalidades" icon=module.icon_tile %}
          <a class="gn-btn gn-btn--secondary" href="/">Volver a Inicio</a>
        {% endgn_page_head %}

    Sin acciones: ``{% gn_page_head title="…" only %}`` (sin bloque de cierre).
    """
    bits = token.split_contents()[1:]
    only = "only" in bits
    kwargs = _kwargs(parser, [b for b in bits if b != "only"])
    nodelist = None
    if not only:
        nodelist = parser.parse(("endgn_page_head",))
        parser.delete_first_token()
    return PageHeadNode(nodelist, kwargs)
