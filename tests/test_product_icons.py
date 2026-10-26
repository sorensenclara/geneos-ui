"""La iconografía original se copia sin modificaciones y la navegación la usa."""
import hashlib
import json
import re
from pathlib import Path

import pytest
from django.template import Context, Template

from geneos_ui import product_icons
from geneos_ui.catalog_data import PRODUCTS
from geneos_ui.navigation import build_nav

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "geneos_ui" / "static"
ICONS_DIR = STATIC / "geneos_ui" / "icons"
REQUIRED = ("id", "product", "module", "module_label", "variant", "format", "file", "status", "usage", "source", "sha256")
ICONS = product_icons.manifest()["icons"]
WITH_FILE = [i for i in ICONS if i["file"]]


@pytest.mark.parametrize("rec", WITH_FILE, ids=[i["id"] for i in WITH_FILE])
def test_copia_identica_al_original(rec):
    """El SHA-256 registrado es el del archivo en la rama del producto; la copia debe coincidir byte a byte."""
    data = (STATIC / rec["file"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == rec["sha256"]
    assert len(data) == rec["bytes"]


def test_manifiesto_completo():
    for rec in ICONS:
        for key in REQUIRED:
            assert key in rec, (rec["id"], key)
        assert rec["status"] in ("activo", "disponible", "pendiente")
        if rec["status"] == "pendiente":
            assert rec["file"] is None and rec["note"]
        else:
            assert rec["source"] and rec["source"][0]["path"].endswith(rec["name"])
            # nombre original conservado y carpeta según el estado
            assert rec["file"].endswith("/" + rec["name"])
            assert ("/activos/" if rec["status"] == "activo" else "/disponibles/") in rec["file"]


def test_no_hay_archivos_fuera_del_manifiesto():
    listed = {rec["file"] for rec in WITH_FILE}
    for prod in ("gelectric", "gema", "geagro", "geagro-cereales", "geagro-vid"):
        for f in (ICONS_DIR / prod).rglob("*"):
            if f.is_file():
                assert str(f.relative_to(STATIC)) in listed, f


def test_navegacion_del_catalogo_usa_originales():
    """Ningún módulo del sidebar usa el sprite genérico, salvo el Inicio de GELECTRIC (que es de su propio sprite)."""
    for p in PRODUCTS:
        for e in build_nav(p["nav"](None), None):
            if e["type"] == "section":
                continue
            if p["key"] == "gelectric" and e["label"] == "Inicio":
                assert e["icon"] == "i-home"
                continue
            assert e["icon_static"] or e["icon_pending"], (p["key"], e["label"])
            if e["icon_static"]:
                rec = next(r for r in ICONS if r["file"] == e["icon_static"])
                assert rec["status"] == "activo" and rec["variant"] == "white"


def test_pendientes_de_vid_no_usan_iconos_genericos():
    nav = {e["label"]: e for e in build_nav(next(p for p in PRODUCTS if p["key"] == "geagro-vid")["nav"](None), None)}
    for label in ("Fenología", "Informes", "Monitoreo de cultivo"):
        assert nav[label]["icon_pending"] and not nav[label]["icon"]
    html = Template("{% load geneos_ui %}{% gn_nav_icon e %}").render(Context({"e": nav["Fenología"]}))
    assert "gn-nav__icon-pending" in html and "<use" not in html


def test_insumos_cereales_usa_el_svg_del_backoffice():
    rec = product_icons.resolve("geagro-cereales:insumos")
    assert rec["file"].endswith("img/icons/insumos.svg") and rec["set"] == "backoffice"


def test_png_de_graficos_disponible_pero_fuera_del_sidebar():
    pngs = [r for r in ICONS if r["module"] == "informes" and r["format"] == "png"]
    assert pngs and all(r["status"] == "disponible" for r in pngs)


def test_sprite_sin_iconos_de_modulo_inventados():
    retired = "building chart clipboard cloud dollar extinguisher flame grape layers leaf silo sprout tasks truck".split()
    for f in ("geneos_ui/templates/geneos_ui/components/icon_sprite.html", "geneos_ui/static/geneos_ui/icons/sprite.svg"):
        ids = set(re.findall(r'<symbol id="i-([\w-]+)"', (ROOT / f).read_text()))
        assert not ids & set(retired), f
