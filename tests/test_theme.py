import re
from pathlib import Path

from django.template import Context, Template

CSS = Path(__file__).resolve().parent.parent / "geneos_ui" / "static" / "geneos_ui" / "css"


def test_light_is_default_and_dark_is_black():
    tokens = (CSS / "tokens.css").read_text()
    base = tokens.split('[data-gn-theme="dark"]')[0]
    assert "--gn-bg: #ffffff" in base
    dark = tokens.split(':root[data-gn-theme="dark"]', 1)[1]
    for value in ("#090909", "#171717", "#242424"):
        assert value in dark
    # el modo no depende del sistema operativo
    assert "prefers-color-scheme" not in tokens


def test_boot_script_defaults_to_light():
    out = Template("{% load geneos_ui %}{% gn_theme_boot %}").render(Context())
    assert "localStorage.getItem('gn-theme')" in out
    assert "var t='light'" in out


def test_theme_switch_markup():
    out = Template("{% load geneos_ui %}{% gn_theme_switch %}").render(Context())
    assert 'data-gn-theme-switch' in out
    assert re.search(r'data-gn-theme-value="light"', out) and 'data-gn-theme-value="dark"' in out
    assert 'role="radiogroup"' in out
