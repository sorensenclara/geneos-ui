"""Navegación declarativa del sidebar.

Cada producto describe su menú con NavItem y GENEOS UI se encarga de:

- filtrar lo que el usuario no puede ver (permisos de Django o una función
  propia del producto, por ejemplo ``lambda r: r.user.is_company_admin``);
- resolver las URLs (nombre de URL o ruta directa);
- marcar el ítem activo y abrir el grupo que lo contiene;
- dejar los datos listos para el buscador del sidebar.

El paquete no conoce roles ni modelos: las reglas siguen siendo del producto.

Ejemplo::

    from geneos_ui.navigation import NavItem, NavSection

    def get_nav(request):
        return [
            NavItem("Inicio", url="core:home", icon="gema:inicio"),
            NavSection("Gestión"),
            NavItem("Clientes", url="cliente:list", icon="gema:clientes",
                    visible=lambda r: r.user.is_company_admin or r.user.is_operador),
            NavItem("Matafuegos", icon="gema:matafuegos", children=[
                NavItem("Listado", url="matafuegos:list"),
                NavItem("Vencimientos", url="matafuegos:panel-vencimientos",
                        keywords="vencidos por vencer avisos whatsapp"),
            ]),
        ]
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from django.urls import NoReverseMatch, reverse
from django.utils.text import slugify

from . import product_icons


@dataclass
class NavItem:
    label: str
    url: Optional[str] = None            # nombre de URL ("app:vista") o ruta ("/x/")
    url_args: tuple = ()
    url_kwargs: dict = field(default_factory=dict)
    icon: Optional[str] = None           # "i-users" (sprite, acciones) o "gema:clientes" (ícono original del producto)
    icon_static: Optional[str] = None    # ruta de static de un ícono propio que no está en el manifiesto
    children: list = field(default_factory=list)
    perms: tuple = ()                    # permisos de Django requeridos (todos)
    visible: Optional[Callable[[Any], bool]] = None
    keywords: str = ""                   # palabras extra para el buscador
    badge: Optional[str] = None          # texto corto ("Nuevo", "3")
    match: tuple = ()                    # prefijos de ruta extra para marcar activo
    id: Optional[str] = None


@dataclass
class NavSection:
    """Título de sección dentro del menú (p. ej. "Campo actual")."""
    label: str
    perms: tuple = ()
    visible: Optional[Callable[[Any], bool]] = None


def _icon_fields(entry) -> dict:
    """Resuelve "producto:módulo" contra el manifiesto de íconos originales.

    Si el producto no tiene ícono propio para ese módulo (estado "pendiente")
    se marca como pendiente: el sidebar muestra un marcador neutro, no un
    ícono genérico.
    """
    if product_icons.is_product_ref(entry.icon):
        rec = product_icons.resolve(entry.icon)
        if rec and rec["file"]:
            return {"icon": None, "icon_static": rec["file"], "icon_pending": False, "icon_ref": entry.icon}
        return {"icon": None, "icon_static": None, "icon_pending": True, "icon_ref": entry.icon}
    return {"icon": entry.icon, "icon_static": entry.icon_static, "icon_pending": False, "icon_ref": None}


def _allowed(entry, request) -> bool:
    user = getattr(request, "user", None)
    if entry.perms and not (user and user.has_perms(entry.perms)):
        return False
    if entry.visible is not None:
        try:
            return bool(entry.visible(request))
        except Exception:  # una regla rota no debe tirar abajo todo el menú
            return False
    return True


def _resolve(item: NavItem) -> Optional[str]:
    if not item.url:
        return None
    if item.url.startswith(("/", "http://", "https://", "#", "?")):
        return item.url
    try:
        return reverse(item.url, args=item.url_args, kwargs=item.url_kwargs)
    except NoReverseMatch:
        return None


def _is_active(href: Optional[str], item: NavItem, path: str) -> bool:
    prefixes = [p for p in ([href] if href else []) + list(item.match) if p and p.startswith("/")]
    for p in prefixes:
        if p == "/":
            if path == "/":
                return True
        elif path == p or path.startswith(p.rstrip("/") + "/"):
            return True
    return False


def build_nav(entries, request) -> list[dict]:
    """Convierte NavItem/NavSection en dicts listos para el template."""
    path = getattr(request, "path", "") or ""
    out: list[dict] = []
    used_ids: set[str] = set()

    def uid(base):
        base = slugify(base) or "item"
        candidate, n = base, 2
        while candidate in used_ids:
            candidate, n = f"{base}-{n}", n + 1
        used_ids.add(candidate)
        return candidate

    for entry in entries or []:
        if not _allowed(entry, request):
            continue
        if isinstance(entry, NavSection):
            out.append({"type": "section", "label": entry.label})
            continue
        href = _resolve(entry)
        children = []
        for child in entry.children:
            if isinstance(child, NavItem) and _allowed(child, request):
                c_href = _resolve(child)
                if c_href is None:
                    continue
                children.append({
                    "label": child.label,
                    "href": c_href,
                    "keywords": child.keywords,
                    "badge": child.badge,
                    "active": _is_active(c_href, child, path),
                })
        # un grupo sin opciones visibles y sin URL propia no se muestra
        if entry.children and not children and href is None:
            continue
        if not entry.children and href is None:
            continue
        # el activo más específico gana: si un hijo coincide, el padre no se marca
        child_active = any(c["active"] for c in children)
        out.append({
            "type": "group" if children else "item",
            "id": entry.id or uid(entry.label),
            "label": entry.label,
            "href": href,
            **_icon_fields(entry),
            "keywords": entry.keywords,
            "badge": entry.badge,
            "children": children,
            "active": (not children) and _is_active(href, entry, path),
            "has_active": child_active,
        })

    # títulos de sección que quedaron sin contenido debajo
    cleaned = []
    for i, e in enumerate(out):
        if e["type"] == "section":
            nxt = out[i + 1] if i + 1 < len(out) else None
            if nxt is None or nxt["type"] == "section":
                continue
        cleaned.append(e)
    return cleaned


def search_index(nav: list[dict]) -> list[dict]:
    """Índice plano (módulo + opción) para buscadores externos al sidebar."""
    rows = []
    for e in nav:
        if e["type"] == "section":
            continue
        if e["href"]:
            rows.append({"label": e["label"], "parent": "", "href": e["href"], "keywords": e["keywords"]})
        for c in e["children"]:
            rows.append({"label": c["label"], "parent": e["label"], "href": c["href"], "keywords": c["keywords"]})
    return rows
