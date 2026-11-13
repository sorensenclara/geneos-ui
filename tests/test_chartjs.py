"""Contrato del adaptador opcional Chart.js y compatibilidad SVG."""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "geneos_ui"
JS = (BASE / "static/geneos_ui/js/geneos-ui.js").read_text(encoding="utf-8")
ADAPTER = (BASE / "static/geneos_ui/js/chartjs-adapter.js").read_text(encoding="utf-8")
TAGS = (BASE / "templatetags/geneos_ui.py").read_text(encoding="utf-8")
CSS = (BASE / "static/geneos_ui/css/geneos-ui.css").read_text(encoding="utf-8")


def test_svg_clasico_permanece():
    assert 'if (t === "line") lineChart(el)' in JS
    assert 'if (t === "donut") donutChart(el)' in JS
    assert 'data-gn-engine") === "chartjs"' in JS


def test_chartjs_opcional_y_accesible():
    assert "window.Chart" in ADAPTER
    assert "data-gn-source" in ADAPTER
    assert "application/json" in ADAPTER
    assert "gn-visually-hidden" in ADAPTER
    assert "textContent" in ADAPTER
    assert "GN.renderChartJS" in ADAPTER
    assert "GN.destroyChartJS" in ADAPTER


def test_assets_chartjs_separados():
    assert "def gn_chartjs_js()" in TAGS
    assert "js/chartjs-adapter.js" in TAGS
    assert 'data-gn-engine="chartjs"' in CSS


def test_chartjs_incluido_automaticamente():
    assert 'js/chartjs-adapter.js' in TAGS
    assert 'vendor/chartjs/chart.umd.min.js' in TAGS
    assert 'data-gn-chartjs-src' in TAGS
    assert 'vendorUrl' in ADAPTER
    assert 'document.head.appendChild(script)' in ADAPTER


def test_chartjs_vendor_fijado_y_con_licencia():
    vendor = BASE / "static/geneos_ui/vendor/chartjs"
    script = vendor / "chart.umd.min.js"
    assert script.exists(), "Falta ejecutar el workflow vendor-chartjs.yml"
    assert script.stat().st_size > 100_000
    assert (vendor / "LICENSE.md").exists()
    assert (vendor / "SHA256SUMS").exists()
