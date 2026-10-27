"""El contenido de ejemplo de cada producto usa sus propios términos e íconos."""
import re

from django.test import Client, override_settings

from geneos_ui.catalog_data import PRODUCTS
from geneos_ui.catalog_examples import BACKOFFICE, EXAMPLES, GELECTRIC_ONLY
from geneos_ui import product_icons

# términos propios de cada negocio que no deben aparecer en los demás productos
TERMS = {
    "gelectric": ["asociad", "suministro", "cuota capital", "medidor", "kWh"],
    "gema": ["matafuego", "recarga", "prueba hidráulica", "oblea"],
    "geagro-cereales": ["soja", "maíz", "siembra"],  # "lote" y "campaña" se usan en los dos
    "geagro-vid": ["viñedo", "fenológ", "peronospora", "variedad"],
}


def _texts(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _texts(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _texts(v)


def test_mismas_claves_en_los_cuatro_productos():
    keys = {k: set(v) for k, v in EXAMPLES.items()}
    assert len({frozenset(k) for k in keys.values()}) == 1


DATA_KEYS = ("eyebrow", "title", "desc", "kpis", "series_title", "donut_title", "donut", "table_title", "cols", "rows", "tagline")


def test_no_se_mezclan_terminos_entre_productos():
    for prod, ex in EXAMPLES.items():
        data = next(p for p in PRODUCTS if p["key"] == prod)
        nav = [e.label for e in data["nav"](None)]
        text = " ".join([*_texts(ex), *_texts([data[k] for k in DATA_KEYS]), *nav]).lower()
        for other, terms in TERMS.items():
            if other == prod:
                continue
            for t in terms:
                assert t.lower() not in text, f"{prod} usa «{t}» de {other}"


def test_iconos_de_ejemplos():
    for prod, ex in EXAMPLES.items():
        for t in _texts(ex):
            if re.fullmatch(r"i-[\w-]+", t) and prod != "gelectric":
                assert t not in GELECTRIC_ONLY, f"{prod} usa {t}, que representa un módulo de GELECTRIC"
            if product_icons.is_product_ref(t):
                assert t.split(":")[0] == prod, f"{prod} usa un ícono de otro producto: {t}"


def test_backoffice_solo_geagro_y_con_iconos_del_backoffice():
    assert set(BACKOFFICE) == {"geagro-cereales", "geagro-vid"}
    for prod, items in BACKOFFICE.items():
        for label, module, _ in items:
            rec = product_icons.resolve(f"{prod}:{module}", set_name="backoffice")
            assert rec, (prod, label)
            assert rec["status"] == "pendiente" or "/img/icons/" in rec["file"], (prod, label)
    assert "Acopio" not in [i[0] for i in BACKOFFICE["geagro-vid"]]


@override_settings(DEBUG=True)
def test_catalogo_renderiza_contenido_de_cada_producto():
    html = Client().get("/?static=1").content.decode()
    for prod, ex in EXAMPLES.items():
        assert f'data-kit-product="{prod}"' in html
        assert ex["form"]["title"] in html
        assert f'id="{prod}-confirm"' in html


def test_vid_usa_lote_como_el_sistema():
    """La rama 2026-vid dice «lote»; «cuartel» no aparece en el sistema."""
    data = next(p for p in PRODUCTS if p["key"] == "geagro-vid")
    text = " ".join([*_texts(EXAMPLES["geagro-vid"]), *_texts([data[k] for k in DATA_KEYS])]).lower()
    assert "cuartel" not in text and "lote" in text
