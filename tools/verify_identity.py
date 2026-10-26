"""Verifica que la identidad de cada tema coincida con los repositorios de los productos.

Compara, contra las ramas de trabajo publicadas (origin/2026, origin/2026-cereales,
origin/2026-vid), sin modificar nada en esos repositorios:

1. Colores: cada valor hex de themes/*.css se busca en el CSS/HTML propio del
   producto (sin librerías de terceros) y se informa archivo y línea.
2. Logotipos: hash SHA-256 de las copias del catálogo contra los originales.
3. Tipografía: familias y pesos que carga cada producto.
4. Contraste WCAG de las combinaciones que usa la librería.

Uso:
    python tools/verify_identity.py --gelectric ../geletric-django --gema ../GEMA --geagro ../geneos-geagro
    → imprime el resumen y escribe docs/verificacion-identidad.md
"""
import argparse
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = ROOT / "geneos_ui" / "static" / "geneos_ui" / "css" / "themes"
TOKENS = ROOT / "geneos_ui" / "static" / "geneos_ui" / "css" / "tokens.css"
LOGOS = ROOT / "sandbox" / "static" / "demo" / "logos"

PRODUCTS = {
    "gelectric": {"repo": "gelectric", "branch": "2026", "name": "GELECTRIC",
                  "logos": {"full": "core/static/core/images/SVG/Isologotipo GELETRIC white.svg", "icon": "core/static/core/images/SVG/Iso GELETRIC.svg"}},
    "gema": {"repo": "gema", "branch": "2026", "name": "GEMA",
             "logos": {"full": "core/static/core/images/gema-logo-white.svg", "icon": "core/static/core/images/gema-logo-favicon.svg"}},
    "geagro-cereales": {"repo": "geagro", "branch": "2026-cereales", "name": "GEAGRO Cereales",
                        "logos": {"full": "agro_system/static/images/logo-geagro-cereal.svg", "icon": "agro_system/static/img/logo-sm-GEAGRO-cereal.svg"}},
    "geagro-vid": {"repo": "geagro", "branch": "2026-vid", "name": "GEAGRO Vid",
                   "logos": {"full": "agro_system/static/images/logo-geagro-light.svg", "icon": "agro_system/static/img/logo-sm-GEAGRO-vid.svg"}},
}
# Archivos de terceros que no cuentan como identidad del producto
VENDOR = re.compile(r"(/lexa/|/libs/|bootstrap|app(-rtl)?\.min\.css|app\.css|icons(\.min)?\.css|typicons|/vendor/|templates/(components|extras)/)", re.I)
SOURCE_GLOBS = ["*.css", "*.html"]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout


def ref(repo, branch):
    for candidate in (f"origin/{branch}", branch):
        if git(repo, "rev-parse", "--verify", "-q", candidate).strip():
            return candidate
    raise SystemExit(f"No encuentro la rama {branch} en {repo}")


def find_hex(repo, rev, hexval):
    h = hexval.lower()
    variants = [h]
    if h[1] == h[2] and h[3] == h[4] and h[5] == h[6]:
        variants.append("#" + h[1] + h[3] + h[5])  # forma corta: #ffffff → #fff
    args = []
    for v in variants:
        args += ["-e", v + "\\b" if len(v) == 4 else v]
    out = git(repo, "grep", "-n", "-i", "-E", *args, rev, "--", *SOURCE_GLOBS)
    hits = []
    for line in out.splitlines():
        _, path, lineno, *_ = line.split(":", 3)
        if VENDOR.search("/" + path):
            continue
        hits.append(f"{path}:{lineno}")
    return hits


def theme_values(product):
    text = (THEMES / f"{product}.css").read_text()
    block = text.split("[data-gn-variant", 1)[0]
    return re.findall(r"(--gn-(?:c|chart)-[\w-]+):\s*(#[0-9a-fA-F]{6})", block)


def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def blend_white(hexval, alpha):
    """Color blanco con opacidad sobre un fondo (para el texto del sidebar)."""
    h = hexval.lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(c + (255 - c) * alpha):02x}" for c in rgb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gelectric", required=True)
    ap.add_argument("--gema", required=True)
    ap.add_argument("--geagro", required=True)
    args = ap.parse_args()
    repos = {"gelectric": Path(args.gelectric), "gema": Path(args.gema), "geagro": Path(args.geagro)}
    md = ["# Verificación de identidad", "",
          "Generado por `tools/verify_identity.py` contra las ramas de trabajo publicadas. "
          "Los productos no se modificaron.", ""]
    summary = []

    for key, p in PRODUCTS.items():
        repo = repos[p["repo"]]
        rev = ref(repo, p["branch"])
        commit = git(repo, "rev-parse", "--short", rev).strip()
        md += [f"## {p['name']} · `{rev}` ({commit})", "", "### Colores", "",
               "| Token | Valor | Dónde está en el producto |", "| --- | --- | --- |"]
        found = missing = 0
        for token, val in theme_values(key):
            hits = find_hex(repo, rev, val)
            if hits:
                found += 1
                where = ", ".join(f"`{h}`" for h in hits[:2]) + (f" y {len(hits) - 2} más" if len(hits) > 2 else "")
            else:
                missing += 1
                others = [o for o, r in repos.items() if r != repo and find_hex(r, ref(r, PRODUCTS[[k for k, v in PRODUCTS.items() if v["repo"] == o][0]]["branch"]), val)]
                where = "**No está en el producto.** " + (f"Se toma de {', '.join(others)} (valor compartido)." if others else "Valor de GENEOS UI.")
            md.append(f"| `{token}` | `{val}` | {where} |")
        md.append("")

        md += ["### Logotipos", "", "| Logo | Archivo original | Coincide |", "| --- | --- | --- |"]
        logos_ok = True
        for kind, path in p["logos"].items():
            original = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True).stdout
            copy = (LOGOS / f"{key}-{kind}.svg").read_bytes()
            same = bool(original) and hashlib.sha256(original).hexdigest() == hashlib.sha256(copy).hexdigest()
            logos_ok &= same
            md.append(f"| {kind} | `{path}` | {'Sí, idéntico (SHA-256)' if same else '**No**'} |")
        md.append("")

        fonts = set()
        for line in git(repo, "grep", "-i", "-E", "Titillium|font-family|fonts.googleapis", rev, "--", *SOURCE_GLOBS).splitlines():
            if VENDOR.search("/" + line.split(":", 2)[1]):
                continue
            for fam in re.findall(r"family=([A-Za-z+]+)(?::([^&\"')]+))?", line):
                fonts.add(fam[0].replace("+", " ") + (f" ({fam[1]})" if fam[1] else ""))
        md += ["### Tipografía", "", "Fuentes que carga el producto: " + (", ".join(sorted(fonts)) or "ninguna explícita") + ".",
               "Las fuentes de las librerías de terceros (Poppins en el CSS base de Lexa) no se cuentan: el CSS propio del producto las reemplaza por Titillium Web.",
               "GENEOS UI carga Titillium Web 400, 600 y 700 (los pesos que usan los componentes).", ""]
        summary.append((p["name"], found, missing, logos_ok, sorted(fonts)))

    # contraste
    tokens = TOKENS.read_text()
    neutral = dict(re.findall(r"(--gn-(?:surface|surface-2|bg|text|text-2|text-muted|border-control)):\s*(#[0-9a-fA-F]{6})", tokens.split("[data-gn-theme")[0]))
    md += ["## Contraste (WCAG 2.1)", "", "Mínimos: 4,5:1 texto normal, 3:1 texto grande y bordes de controles.", "",
           "| Producto | Combinación | Contraste |", "| --- | --- | --- |"]
    for key, p in PRODUCTS.items():
        v = dict(theme_values(key))
        rows = [
            ("Texto del botón primario sobre la marca", v["--gn-c-on-brand"], v["--gn-c-brand"]),
            ("Texto de marca sobre blanco", v["--gn-c-ink"], "#ffffff"),
            ("Texto del sidebar sobre el fondo", blend_white(v["--gn-c-sidebar"], .85), v["--gn-c-sidebar"]),
            ("Indicador activo sobre el ítem activo", v["--gn-c-accent"], v["--gn-c-sidebar-deep"]),
        ]
        for label, a, b in rows:
            c = contrast(a, b)
            ok = c >= 4.5 or ("Indicador" in label and c >= 3)
            mark = "✓" if ok else ("✗ aceptado: el naranja se mantiene por identidad (decisión del 26/10/2026)" if key == "gema" and "primario" in label else "✗")
            md.append(f"| {p['name']} | {label} (`{a}` / `{b}`) | {c:.2f}:1 {mark} |")
    for label, a, b in [("Texto tenue sobre superficie", neutral["--gn-text-muted"], neutral["--gn-surface"]),
                        ("Texto tenue sobre superficie 2", neutral["--gn-text-muted"], neutral["--gn-surface-2"]),
                        ("Texto secundario sobre fondo", neutral["--gn-text-2"], neutral["--gn-bg"]),
                        ("Borde de campo sobre superficie", neutral["--gn-border-control"], neutral["--gn-surface"])]:
        c = contrast(a, b)
        ok = c >= (3 if "Borde" in label else 4.5)
        md.append(f"| Compartido | {label} (`{a}` / `{b}`) | {c:.2f}:1 {'✓' if ok else '✗'} |")
    md.append("")

    out = ROOT / "docs" / "verificacion-identidad.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    for name, found, missing, logos_ok, fonts in summary:
        print(f"{name}: {found} colores encontrados en el repo, {missing} compartidos; logos {'OK' if logos_ok else 'DISTINTOS'}; fuentes {fonts}")
    print("→", out)


if __name__ == "__main__":
    main()
