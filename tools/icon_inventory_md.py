"""Escribe docs/iconografia.md a partir de geneos_ui/product_icons.json."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
icons = json.loads((ROOT / "geneos_ui" / "product_icons.json").read_text(encoding="utf-8"))["icons"]
NAMES = {"gelectric": "GELECTRIC", "gema": "GEMA", "geagro": "GEAGRO (compartidos Cereales y Vid)",
         "geagro-cereales": "GEAGRO Cereales", "geagro-vid": "GEAGRO Vid"}
md = ["# Iconografía por producto", "",
      "Generado por `tools/icon_inventory_md.py` desde `geneos_ui/product_icons.json`. "
      "Los archivos son copias idénticas de los originales (SHA-256 verificado en `tests/test_product_icons.py` y con "
      "`tools/import_product_icons.py --check`). Los repositorios de los productos no se modificaron.", "",
      "- **activo**: lo usa hoy el producto o la navegación de GENEOS UI.",
      "- **disponible**: original sin uso actual.",
      "- **pendiente**: el producto no tiene ícono propio; no hay archivo.", "",
      "| Producto | Activos | Disponibles | Pendientes | Archivos |", "| --- | ---: | ---: | ---: | ---: |"]
c = Counter((i["product"], i["status"]) for i in icons)
for p, n in NAMES.items():
    files = sum(1 for i in icons if i["product"] == p and i["file"])
    md.append(f"| {n} | {c[(p, 'activo')]} | {c[(p, 'disponible')]} | {c[(p, 'pendiente')]} | {files} |")
md.append(f"| **Total** | {sum(v for (_, s), v in c.items() if s == 'activo')} | {sum(v for (_, s), v in c.items() if s == 'disponible')} | "
          f"{sum(v for (_, s), v in c.items() if s == 'pendiente')} | {sum(1 for i in icons if i['file'])} |")
for p, n in NAMES.items():
    rows = [i for i in icons if i["product"] == p]
    if not rows:
        continue
    md += ["", f"## {n}", "", "| Estado | Módulo | Variante | Formato | Archivo en GENEOS UI | Origen | Uso |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for i in sorted(rows, key=lambda r: (r["status"], r["module"], r["variant"])):
        src = i["source"][0] if i["source"] else None
        origin = f"`{src['path']}` ({', '.join(s['branch'] for s in i['source'])} · {src['commit']})" if src else "—"
        use = "; ".join(f"`{u}`" for u in i["used_in"][:2]) + (f" y {len(i['used_in']) - 2} más" if len(i["used_in"]) > 2 else "")
        if i["kit_use"] and i["status"] != "pendiente":
            use = (use + "; " if use else "") + "sidebar de GENEOS UI"
        if i["status"] == "pendiente":
            use = i["note"]
        f = f"`{i['file'].split('/icons/', 1)[1]}`" if i["file"] else "—"
        md.append(f"| {i['status']} | {i['module_label']} | {i['variant']} | {i['format'].upper()} | {f} | {origin} | {use or 'sin uso'} |")
md += ["", "## No incorporados", "",
       "- Duplicados por normalización Unicode (mismo contenido, nombre en NFD): `compañia.svg` de GEMA y los PNG «Gráficos» y «Parámetros» de GEAGRO. Se copió la versión NFC.",
       "- Ilustraciones de reportes de GEAGRO en `templates/operations/img/` (educación, familiares, género, persona, salud, el logo de Granero de Sueños y una foto): no son íconos de módulo y ningún template las usa.",
       "- Favicons y logotipos fuera de las carpetas de íconos: siguen en `sandbox/static/demo/logos/` (ver `docs/verificacion-identidad.md`)."]
(ROOT / "docs" / "iconografia.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print("docs/iconografia.md", len(md), "líneas")
