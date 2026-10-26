from django.core.checks import Error, Warning, register

from .conf import BRIDGES, PRODUCTS, get_config


@register()
def check_geneos_ui(app_configs, **kwargs):
    cfg = get_config()
    problems = []
    if cfg["PRODUCT"] not in PRODUCTS:
        problems.append(Error(
            f"GENEOS_UI['PRODUCT'] = {cfg['PRODUCT']!r} no es un producto conocido.",
            hint="Valores válidos: " + ", ".join(PRODUCTS),
            id="geneos_ui.E001",
        ))
    for b in cfg["BRIDGES"]:
        if b not in BRIDGES:
            problems.append(Error(f"Puente desconocido: {b!r}.", hint="Valores válidos: " + ", ".join(BRIDGES), id="geneos_ui.E002"))
    if cfg["SIDEBAR_DEFAULT"] not in ("expanded", "collapsed"):
        problems.append(Warning("GENEOS_UI['SIDEBAR_DEFAULT'] debe ser 'expanded' o 'collapsed'.", id="geneos_ui.W001"))
    return problems
