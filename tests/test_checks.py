"""Chequeos de GENEOS_UI: errores y avisos nuevos de la 0.3.0."""
import pytest

from geneos_ui.checks import check_geneos_ui


def ids(settings, **cfg):
    settings.GENEOS_UI = cfg
    return [e.id for e in check_geneos_ui(None)]


@pytest.mark.parametrize("product", ["gelectric", "gema", "geagro-cereales", "geagro-vid"])
def test_los_cuatro_productos_sin_problemas(settings, product):
    assert ids(settings, PRODUCT=product, LOGO_FULL=f"demo/logos/{product}-full.svg") == []


def test_errores(settings):
    assert "geneos_ui.E001" in ids(settings, PRODUCT="GE FLOTA", THEME_CSS=["geneos_ui/css/tokens.css"])
    assert ids(settings, PRODUCT="geflota") == ["geneos_ui.E003"]
    assert ids(settings, PRODUCT="geflota", THEME_CSS=["no/existe.css"]) == ["geneos_ui.E004"]
    assert ids(settings, PRODUCT="gema", NAV_ICONS="verde") == ["geneos_ui.E005"]
    assert ids(settings, PRODUCT="gema", NAV_ICONS={"active": "active"}) == ["geneos_ui.E005"]
    assert ids(settings, PRODUCT="gema", BRIDGES=["tailwind"]) == ["geneos_ui.E002"]


def test_avisos(settings):
    assert ids(settings, PRODUCT="gema", SIDEBAR_DEFAULT="abierto") == ["geneos_ui.W001"]
    assert ids(settings, PRODUCT="gema", LOGO_TOPBAR="no/existe.svg") == ["geneos_ui.W002"]


def test_template_sobrescrito(settings, tmp_path):
    (tmp_path / "geneos_ui" / "components").mkdir(parents=True)
    (tmp_path / "geneos_ui" / "components" / "sidebar.html").write_text("<aside></aside>")
    settings.TEMPLATES = [{**settings.TEMPLATES[0], "DIRS": [tmp_path]}]
    assert ids(settings, PRODUCT="gema") == ["geneos_ui.W003"]
