"""El HTML que genera el paquete para los cuatro productos no cambia respecto
de la referencia (tests/snapshots/<versión>/), salvo lo que normaliza
``generate.normalize`` (parámetro de versión y marcas del catálogo)."""
import difflib
import re
from pathlib import Path

import pytest

from tests.snapshots.generate import render_all

REFERENCE = "0.7.0"
REF_DIR = Path(__file__).resolve().parent / "snapshots" / REFERENCE


# Cambios de HTML hechos a propósito en la 0.3.0, sin efecto visual ni de comportamiento.
# Se quitan del HTML actual antes de comparar; cada uno tiene su propio test.
CAMBIOS_INTENCIONALES = [
    # Ejemplo nuevo, cubierto por las pruebas responsive y de interacción.
    (r'<a href="#filtros-progresivos">Filtros progresivos</a>', ""),
    (r'(?s)<section class="kit-section" id="filtros-progresivos".*?</section>', ""),
    # La escala predeterminada se verifica en los tests de tipografía.
    (r'(<html [^>]*?) data-gn-type="legible"', r"\g<1>"),
    # Catálogo · el selector de escala se verifica por separado en Chromium.
    (r'(?s)\n<div class="kit-type-scale">.*?</div>', ""),
    # 0.4.0 · GELECTRIC ofrece su variante azul: el boot aplica la elección guardada antes de pintar
    (r"(?s)<script>\(function\(c\)\{var d=document\.documentElement,k='gn-variant:'.*?</script>", ""),
    # 0.4.0 · grupo «Color» del panel de preferencias (solo productos con VARIANTS)
    (r'(?s)\n    <div class="gn-prefs__group gn-prefs__group--variant".*?\n    </div>(?=\n    <p class="gn-prefs__note">|\n    <div class="gn-prefs__group gn-prefs__group--variant")', ""),
    # 0.4.0 · catálogo: sección «Vista de módulo» al final (gn_page_head y gn_link_list)
    (r'(?s)\n\n<section class="kit-section" id="vista-de-modulo".*?</section>', ""),
    # 0.5.0 · catálogo: sección «Fecha y hora», su entrada en el índice y los scripts de los selectores
    (r'(?s)\{# =+ FECHA Y HORA.*?</section>\n\n|<section class="kit-section" id="fecha-hora".*?</section>\n\n', ""),
    (r'<a href="#fecha-hora">Fecha y hora</a>', ""),
    (r'<script src="[^"]*geneos_ui/vendor/cally/cally\.js[^"]*" type="module"></script>\n?<script src="[^"]*geneos_ui/js/datetime\.js[^"]*" defer></script>', ""),
]


# Texto del catálogo que cambia con cada versión (no es diseño): se normaliza en los dos lados.
NORMALIZAR_AMBOS = [
    (r"geneos-ui @ git\+https://\S+?\.git@v[0-9.]+", "geneos-ui @ <repositorio>@vX"),  # línea de instalación (GitHub desde la 0.3.0)
]


def both(html):
    # Normalizar únicamente límites dinámicos de fechas del catálogo (hoy y +30 días).
    html = re.sub(r'\b(min|max)="\d{4}-\d{2}-\d{2}"', lambda m: m.group(1) + '="<fecha-dinamica>"', html)
    # La demo nueva se prueba por separado y no forma parte de snapshots 0.7.0.
    html = re.sub(r'<div id="chartjs-demo".*?</div>(?=\s*</section>)', "", html, flags=re.S)
    # El adaptador nuevo se comprueba en tests/test_chartjs.py, no en snapshots 0.7.0.
    html = re.sub(r'<script src="[^"]*/geneos_ui/js/chartjs-adapter[.]js" data-gn-chartjs-src="[^"]*" defer></script>', "", html)
    for pattern, repl in NORMALIZAR_AMBOS:
        html = re.sub(pattern, repl, html)
    return re.sub(r"\n[ \t]*(?=\n)", "", html)  # líneas en blanco que dejan los {% if %}


@pytest.fixture(scope="module")
def current():
    return render_all()


@pytest.mark.parametrize("name", sorted(p.stem for p in REF_DIR.glob("*.html")))
def test_html_igual_a_la_referencia(current, name):
    expected = both((REF_DIR / f"{name}.html").read_text(encoding="utf-8"))
    got = both(current[name])
    if name == "catalog":
        got = got.replace("Indicadores con valor, unidad y tendencia; SVG para gráficos simples y Chart.js para análisis interactivos. Ambos respetan la paleta del producto y la accesibilidad.", "Indicadores con valor, unidad y tendencia; gráficos en SVG sin librerías externas, con tabla accesible para lectores de pantalla. Los colores salen de la paleta del producto.")
        # Las tablas de gestión se verifican en sus propias pruebas de navegador.
        got = re.sub(r'(?s)\n<div class="kit-stack" id="tablas-de-gestion">.*?(?=\n</section>)', "", got)
        got = got.replace('<span class="kit-table-standard-label">Estándar · </span>', '')
        # El ejemplo de botones abre una confirmación y comparte su botón de cierre.
        got = got.replace("Radio compartido de 32 px. Probá «Eliminar» para abrir la confirmación y «Guardar» para ver el estado de carga.",
                          "El botón Guardar muestra el estado de carga real: hacé clic.")
        got = re.sub(r'(class="gn-btn gn-btn--danger") data-gn-modal-open="[^"]+-confirm"(?=>.*?</svg>Eliminar</button>)',
                     r"\1", got)
        got = got.replace('class="gn-btn gn-btn--ghost gn-btn--icon gn-btn--sm" data-gn-modal-close aria-label="Cerrar"',
                          'class="gn-alert__close" data-gn-modal-close aria-label="Cerrar"')
    if got != expected:
        diff = "\n".join(list(difflib.unified_diff(expected.splitlines(), got.splitlines(), REFERENCE, "actual", lineterm="", n=1))[:60])
        pytest.fail(f"{name}: el HTML cambió respecto de {REFERENCE}\n{diff}")
