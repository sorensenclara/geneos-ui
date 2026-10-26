"""Chequeos sobre los archivos estáticos: reglas de la librería."""
import re
from pathlib import Path

CSS = Path(__file__).resolve().parent.parent / "geneos_ui" / "static" / "geneos_ui" / "css"
REQUIRED = ["--gn-c-sidebar", "--gn-c-sidebar-deep", "--gn-c-brand", "--gn-c-brand-hover", "--gn-c-on-brand",
            "--gn-c-ink", "--gn-c-accent", "--gn-c-good", "--gn-c-warning", "--gn-c-critical", "--gn-c-info"]


def test_cada_tema_declara_su_identidad_completa():
    for theme in ["gelectric", "gema", "geagro-cereales", "geagro-vid"]:
        text = (CSS / "themes" / f"{theme}.css").read_text()
        assert f'[data-gn-product="{theme}"]' in text
        missing = [t for t in REQUIRED if t + ":" not in text]
        assert not missing, (theme, missing)


def test_libreria_vive_en_una_capa():
    for f in [CSS / "tokens.css", CSS / "geneos-ui.css", *(CSS / "themes").glob("*.css")]:
        assert "@layer geneos-ui" in f.read_text(), f.name


def test_todas_las_clases_tienen_prefijo_gn():
    text = re.sub(r"/\*.*?\*/", "", (CSS / "geneos-ui.css").read_text(), flags=re.S)
    classes = set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"[\d.]+(px|em|rem|s|%)", "", text)))
    bad = sorted(c for c in classes if not c.startswith(("gn-", "is-", "has-", "icon-fill")))
    assert not bad, bad


def test_sin_colores_sueltos_en_componentes():
    """Los componentes usan tokens; solo se permiten blanco/negro para texto sobre color sólido y sombras."""
    text = re.sub(r"/\*.*?\*/", "", (CSS / "geneos-ui.css").read_text(), flags=re.S)
    hexes = set(re.findall(r"#[0-9a-fA-F]{3,6}\b", text))
    assert hexes <= {"#fff"}, hexes
