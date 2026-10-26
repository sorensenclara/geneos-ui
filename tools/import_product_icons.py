"""Copia la iconografía original de cada producto a GENEOS UI y genera el manifiesto.

Lee los archivos de las ramas de trabajo con ``git show`` (no modifica los
repositorios de los productos), los copia byte a byte con su nombre original y
escribe ``geneos_ui/product_icons.json`` con producto, módulo, variante,
formato, ruta de origen, commit, SHA-256 y estado de uso.

    python tools/import_product_icons.py --gelectric ../geletric-django --gema ../GEMA --geagro ../geneos-geagro
    python tools/import_product_icons.py --check --gelectric … --gema … --geagro …   → solo verifica

Estados:
- activo: lo usa hoy la interfaz del producto o la navegación de GENEOS UI.
- disponible: archivo original sin uso actual (se guarda para futuras pantallas).
- pendiente: el producto no tiene ícono propio; no hay archivo y no se inventa uno.

Carpetas: icons/<producto>/activos/… e icons/<producto>/disponibles/…, conservando
debajo la ruta original relativa a static/ (evita choques: GEAGRO tiene alert.svg
en images/icon/ y otro distinto en img/icons/).
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "geneos_ui" / "static"
ICONS = STATIC / "geneos_ui" / "icons"
MANIFEST = ROOT / "geneos_ui" / "product_icons.json"
PRODUCT_DIRS = ("gelectric", "gema", "geagro", "geagro-cereales", "geagro-vid")

SOURCES = {
    "gelectric": {"repo": "gelectric", "branch": "2026", "dirs": ["core/static/core/images/SVG"]},
    "gema": {"repo": "gema", "branch": "2026", "dirs": ["core/static/core/images/iconos"]},
    "geagro-cereales": {"repo": "geagro", "branch": "2026-cereales", "dirs": ["agro_system/static/images/icon", "agro_system/static/img/icons"]},
    "geagro-vid": {"repo": "geagro", "branch": "2026-vid", "dirs": ["agro_system/static/images/icon", "agro_system/static/img/icons"]},
}
REPO_NAMES = {"gelectric": "sorensenclara/geletric-django", "gema": "sorensenclara/GEMA", "geagro": "sorensenclara/geneos-geagro"}

# módulo (slug, etiqueta) a partir de una palabra clave del nombre de archivo
MODULES = [
    # GELECTRIC
    ("asociados", "Asociados y servicios", r"Asociados"), ("abastecimiento", "Abastecimiento", r"Abastecimiento"),
    ("contabilidad", "Contabilidad y Finanzas", r"Contabilidad"), ("comercial", "Comercial", r"Comercial"),
    ("reportes", "Reportes", r"Reportes"), ("impuestos", "Impuestos", r"Impuestos"), ("sueldos", "Sueldos", r"Sueldos"),
    ("integraciones", "Integraciones", r"Integraciones"), ("consumo", "Consumo", r"Consumo"), ("tecnico", "Técnico", r"Tecnico"),
    # GEMA
    ("inicio", "Inicio", r"^inicio"), ("clientes", "Clientes", r"^clientes"), ("matafuegos", "Matafuegos", r"^matafuego"),
    ("ordenes", "Órdenes de trabajo", r"^ordenes de trabajo"), ("tareas", "Tareas", r"^tarea"), ("usuarios", "Usuarios", r"^usuarios|^user\b|^user "),
    ("compania", "Mi compañía", r"^compa"), ("vencimientos", "Vencimientos", r"^vencimientos"),
    # GEAGRO
    ("dashboard", "Dashboard", r"dashboard"), ("plan-tecnico", "Plan técnico", r"technical.plan|Technical Plan"),
    ("calendario", "Calendario", r"calendar"), ("alertas", "Alertas y avisos", r"alert"), ("clima", "Clima", r"weather"),
    ("campos", "Mis campos", r"campo"), ("vinedos", "Mis viñedos", r"vi(n|ñ)edos"), ("insumos", "Insumos", r"insumos"),
    ("operaciones", "Operaciones", r"operaciones"), ("parametros", "Parámetros", r"par(a|á)metros"), ("ventas", "Ventas", r"ventas"),
    ("acopio", "Acopio", r"acopio"), ("productores", "Productores", r"producer|productores"),
    ("autenticacion", "Autenticación", r"authentication|autentificacion"), ("configuracion", "Configuración", r"configuracion"),
    ("informes", "Informes (gráficos)", r"gr(a|á)ficos"), ("compras", "Compras", r"compras"), ("control", "Control", r"control"),
    ("transporte", "Transporte", r"transporte"),
]

# ítems de la navegación de GENEOS UI que usan cada archivo (convierte el archivo en "activo")
KIT_NAV = {
    ("gelectric", "SVG/icon white -Asociados y Servicio.svg"), ("gelectric", "SVG/icon white -Abastecimiento.svg"),
    ("gelectric", "SVG/icon white - Contabilidad.svg"), ("gelectric", "SVG/icon white -Comercial.svg"),
    ("gelectric", "SVG/icon white -Reportes.svg"), ("gelectric", "SVG/icon white -Impuestos.svg"),
    ("gelectric", "SVG/icon white -Sueldos.svg"), ("gelectric", "SVG/icon white -Integraciones.svg"),
    ("gelectric", "SVG/icon white -Consumo.svg"), ("gelectric", "SVG/icon white -Tecnico.svg"),
    ("gema", "iconos/inicio-white.svg"), ("gema", "iconos/clientes-white.svg"), ("gema", "iconos/matafuego-white.svg"),
    ("gema", "iconos/ordenes de trabajo-white.svg"), ("gema", "iconos/tarea-white.svg"), ("gema", "iconos/usuarios-white.svg"),
    ("gema", "iconos/compañia-white.svg"), ("gema", "iconos/vencimientos-white.svg"),
    ("geagro", "images/icon/dashboard.svg"), ("geagro", "images/icon/technical_plan.svg"), ("geagro", "images/icon/calendar.svg"),
    ("geagro", "images/icon/alert.svg"), ("geagro", "images/icon/weather.svg"), ("geagro-cereales", "images/icon/campo.svg"),
    ("geagro", "images/icon/vinedos.svg"), ("geagro", "img/icons/operaciones.svg"), ("geagro", "img/icons/insumos.svg"),
    ("geagro-cereales", "img/icons/Acopio-white.svg"), ("geagro", "img/icons/ventas.svg"), ("geagro", "img/icons/parametros.svg"),
}

# íconos que el producto necesita y no existen: se registran sin archivo
PENDING = [
    {"product": "geagro-vid", "module": "fenologia", "module_label": "Fenología", "variant": "white",
     "note": "El portal usa mdi mdi-sprout-outline. Pendiente de diseño (decisión del 26/10/2026)."},
    {"product": "geagro-vid", "module": "monitoreo", "module_label": "Monitoreo de cultivo", "variant": "white",
     "note": "Sin ícono propio. Pendiente de diseño (decisión del 26/10/2026)."},
    {"product": "geagro-vid", "module": "informes", "module_label": "Informes (gráficos)", "variant": "white",
     "note": "Falta la versión SVG blanca o monocromática. Existe el PNG a color «GEAGRO - Icon Gráficos» como recurso disponible; "
             "no se usa en el sidebar (decisión del 26/10/2026). El portal usa mdi mdi-chart-bar."},
]


def nfc(s):
    return unicodedata.normalize("NFC", s)


def git(repo, *args, binary=False):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout
    return out if binary else out.decode()


def ref_for(repo, branch):
    for cand in (f"origin/{branch}", branch):
        if subprocess.run(["git", "-C", str(repo), "rev-parse", "-q", "--verify", cand], capture_output=True).returncode == 0:
            return cand
    raise SystemExit(f"No encuentro la rama {branch} en {repo}")


def list_files(repo, ref, dirs):
    out = git(repo, "ls-tree", "-r", "-z", "--name-only", ref, "--", *dirs)
    return [p for p in out.split("\0") if p and p.lower().endswith((".svg", ".png"))]


def classify(product, rel):
    """Devuelve (set, variante) según la carpeta y el nombre original."""
    name = rel.rsplit("/", 1)[-1]
    low = nfc(name).lower()
    if product == "gelectric":
        if low.startswith("iso"):
            return "marca", "isologo"
        return "modulos", "white" if low.startswith("icon white") else "tile"
    if product == "gema":
        if low.endswith("-active.svg"):
            return "menu", "active"
        if low.endswith("-white.svg"):
            return "menu", "white"
        return "menu", "base"
    # GEAGRO
    if "isologo" in low or low.startswith("mesa de trabajo"):
        return "marca", "isologo"
    if rel.startswith("images/icon/"):
        return "portal", "color" if ("color" in low) else "white"
    if "Iconos PNG/" in rel:
        if " white" in low:
            return "png", "white-png"
        return "png", "simple-png" if "simple" in low else "tile-png"
    if low.endswith(" vid.svg"):
        return "vid", "tile-vid"
    if "simple" in low:
        return "backoffice", "simple"
    if low == "operaciones icon.svg":
        return "backoffice", "simple-alt"
    if low == "acopio.svg":
        return "backoffice", "color"
    return "backoffice", "white"


def module_for(name):
    n = nfc(name)
    base = re.sub(r"^(icon( white)? ?- ?|GEAGRO - (Icon )?)", "", n, flags=re.I)
    for slug, label, pat in MODULES:
        if re.search(pat, base, re.I):
            return slug, label
    return "marca", "Marca"


def product_refs(repo, ref, rel_static, name):
    """Archivo:línea del producto que referencia el archivo (templates, CSS, Python, JS)."""
    out = subprocess.run(["git", "-C", str(repo), "grep", "-n", "-F", nfc(name), ref, "--", "*.html", "*.css", "*.py", "*.js"],
                         capture_output=True).stdout.decode()
    refs = []
    folder = rel_static.rsplit("/", 1)[0] + "/"
    for line in out.splitlines():
        _, path, num, text = line.split(":", 3)
        # nombres genéricos (alert.svg, calendar.svg…) existen en dos carpetas: exigir la carpeta
        if folder.split("/")[-2] not in ("SVG", "iconos") and folder not in nfc(text):
            if not (folder.endswith("icon/") and "images/icon/" in text) and not (folder.endswith("icons/") and "img/icons/" in text):
                continue
        refs.append(f"{path}:{num}")
    return refs


def collect(repos):
    """Recorre las ramas y arma la lista de archivos con su contenido."""
    found = {}
    for prod, src in SOURCES.items():
        repo = repos[src["repo"]]
        ref = ref_for(repo, src["branch"])
        commit = git(repo, "rev-parse", "--short", ref).strip()
        for path in list_files(repo, ref, src["dirs"]):
            if path != nfc(path):
                # duplicado con nombre en NFD (mismo archivo guardado dos veces por macOS)
                twin = nfc(path)
                if twin in list_files(repo, ref, [path.rsplit("/", 1)[0]]):
                    continue
            data = git(repo, "show", f"{ref}:{path}", binary=True)
            rel = nfc(path.split("/static/", 1)[1] if "/static/" in path else path)
            if prod == "gelectric":
                rel = rel.replace("core/images/", "", 1)
            elif prod == "gema":
                rel = rel.replace("core/images/", "", 1)
            found.setdefault((prod, rel), []).append({
                "repo": src["repo"], "branch": src["branch"], "ref": ref, "commit": commit, "path": nfc(path),
                "data": data, "sha256": hashlib.sha256(data).hexdigest(),
                "refs": product_refs(repo, ref, path.split("/static/", 1)[-1], path.rsplit("/", 1)[-1]),
            })
    return found


def build_records(found):
    # GEAGRO: si Cereales y Vid tienen el mismo archivo idéntico, va a "geagro" (compartido)
    merged = {}
    for (prod, rel), sources in found.items():
        merged[(prod, rel)] = sources
    records = []
    seen = set()
    for (prod, rel), sources in sorted(merged.items()):
        if (prod, rel) in seen:
            continue
        product = prod
        all_sources = list(sources)
        if prod.startswith("geagro"):
            other = "geagro-vid" if prod == "geagro-cereales" else "geagro-cereales"
            twin = merged.get((other, rel))
            if twin and twin[0]["sha256"] == sources[0]["sha256"]:
                product = "geagro"
                all_sources += twin
                seen.add((other, rel))
        seen.add((prod, rel))
        src = all_sources[0]
        name = rel.rsplit("/", 1)[-1]
        set_, variant = classify(prod, rel)
        module, label = ("marca", "Marca") if variant == "isologo" else module_for(name)
        used_in = []
        for s in all_sources:
            tag = {"2026-cereales": "Cereales", "2026-vid": "Vid"}.get(s["branch"], "")
            used_in += [(f"{tag}: " if tag and product == "geagro" else "") + r for r in s["refs"]]
        kit_use = ["sidebar"] if (product, rel) in KIT_NAV else []
        status = "activo" if (used_in or kit_use) else "disponible"
        usage = ("producto y GENEOS UI" if used_in and kit_use else "producto" if used_in
                 else "GENEOS UI" if kit_use else "sin uso")
        folder = "activos" if status == "activo" else "disponibles"
        records.append({
            "id": f"{product}/{rel}",
            "product": product,
            "set": set_,
            "module": module,
            "module_label": label,
            "variant": variant,
            "format": name.rsplit(".", 1)[-1].lower(),
            "name": name,
            "file": f"geneos_ui/icons/{product}/{folder}/{rel}",
            "status": status,
            "usage": usage,
            "used_in": sorted(set(used_in)),
            "kit_use": kit_use,
            "bytes": len(src["data"]),
            "sha256": src["sha256"],
            "source": [{"repo": REPO_NAMES[s["repo"]], "branch": s["branch"], "commit": s["commit"], "path": s["path"]} for s in all_sources],
            "_data": src["data"],
        })
    for p in PENDING:
        records.append({"id": f"{p['product']}/pendiente/{p['module']}", "product": p["product"], "set": "portal",
                        "module": p["module"], "module_label": p["module_label"], "variant": p["variant"], "format": "svg",
                        "name": None, "file": None, "status": "pendiente", "usage": "pendiente de diseño", "used_in": [], "kit_use": ["sidebar"],
                        "bytes": 0, "sha256": None, "source": [], "note": p["note"]})
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gelectric", required=True)
    ap.add_argument("--gema", required=True)
    ap.add_argument("--geagro", required=True)
    ap.add_argument("--check", action="store_true", help="solo comparar la copia con los originales")
    a = ap.parse_args()
    repos = {"gelectric": Path(a.gelectric), "gema": Path(a.gema), "geagro": Path(a.geagro)}
    records = build_records(collect(repos))

    if a.check:
        bad = 0
        for r in records:
            if r["file"] is None:
                continue
            copy = STATIC / r["file"]
            if not copy.exists() or copy.read_bytes() != r["_data"]:
                bad += 1
                print("DISTINTO o FALTA:", r["file"])
        n = sum(1 for r in records if r["file"])
        print(f"{n - bad}/{n} archivos idénticos a los originales")
        sys.exit(1 if bad else 0)

    for d in PRODUCT_DIRS:
        shutil.rmtree(ICONS / d, ignore_errors=True)
    for r in records:
        if r["file"]:
            dest = STATIC / r["file"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.pop("_data"))
        else:
            r.pop("_data", None)
    MANIFEST.write_text(json.dumps({
        "generated_by": "tools/import_product_icons.py",
        "sources": {k: {"repo": REPO_NAMES[v["repo"]], "branch": v["branch"]} for k, v in SOURCES.items()},
        "icons": records,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    from collections import Counter
    print(Counter((r["product"], r["status"]) for r in records))
    print(len([r for r in records if r["file"]]), "archivos →", ICONS)


if __name__ == "__main__":
    main()
