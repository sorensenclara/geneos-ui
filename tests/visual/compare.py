"""Compara dos carpetas de capturas.

    python tests/visual/compare.py <referencia> <actual> [--max 0.001] [--diffs <carpeta>]

Falla (código 1) si alguna captura difiere en más de --max (fracción de píxeles)
o si falta. Guarda una imagen de diferencias por captura que no coincide.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops


def ratio(a, b):
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        return 1.0, None
    diff = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v > 24 else 0)
    changed = diff.histogram()[255]
    return changed / (ia.width * ia.height), diff


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("ref")
    ap.add_argument("cur")
    ap.add_argument("--max", type=float, default=0.001)
    ap.add_argument("--diffs")
    args = ap.parse_args(argv)
    bad = []
    for ref in sorted(Path(args.ref).glob("*.png")):
        cur = Path(args.cur) / ref.name
        if not cur.exists():
            bad.append((ref.name, "falta"))
            continue
        r, diff = ratio(ref, cur)
        status = "ok" if r <= args.max else "DIFIERE"
        print(f"{status:8} {r * 100:7.3f} %  {ref.name}")
        if r > args.max:
            bad.append((ref.name, f"{r * 100:.3f} %"))
            if args.diffs and diff:
                Path(args.diffs).mkdir(parents=True, exist_ok=True)
                diff.save(Path(args.diffs) / ref.name)
    print("resultado:", "sin diferencias" if not bad else bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
