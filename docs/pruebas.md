# Pruebas

```bash
python tools/build_catalog.py          # dist/ui-kit.html: lo usan las pruebas en el navegador
pytest                                 # todo (las de tests/visual/ se saltean sin Playwright o sin el catálogo)
python tests/visual/capture.py dist/ui-kit.html /tmp/actual
python tests/visual/compare.py /tmp/referencia /tmp/actual --esperados tests/visual/cambios-esperados.txt
```

## Pruebas intermitentes: `test_abajo_si_entra` y `test_arriba_si_abajo_no_entra`

Las dos están en `tests/visual/test_datetime.py` y comprueban hacia dónde se abre el panel de fecha y hora. `test_abajo_si_entra` deja el campo a 120 px del borde superior de una ventana de 960 px y espera que el panel se abra abajo. `test_arriba_si_abajo_no_entra` lo deja a 120 px del borde inferior, espera que se abra arriba y que la página no se mueva.

**Qué pasó.** Durante la 0.6.0 fallaron de forma intermitente en la suite completa: el panel se abrió arriba en la primera, y la página se movió en la segunda. Las dos son pruebas de la 0.5.0 y fallan igual con la escala compacta, así que no dependen de la escala.

**Primera corrección (276de43), insuficiente.** Se supuso que un cambio de alto de la página entre el desplazamiento y el clic movía el campo. Las pruebas pasaron a esperar a que el campo quedara quieto dos cuadros seguidos antes del clic. Pasaron 6 corridas completas seguidas, pero después volvieron a fallar: 1 de 3 corridas. La suposición era equivocada. El campo sí quedaba quieto; lo que se movía era la página, después de esa espera y durante el clic.

**Causa.** Se instrumentó la página para registrar cada desplazamiento, cada llamada de JavaScript que desplaza o enfoca, y la posición del campo en el documento. En las corridas que fallaron:

- El campo no se movió en el documento: su posición absoluta y el alto de la página fueron los mismos antes y después.
- Ningún script de la página desplazó ni enfocó nada antes del salto. La primera llamada registrada es el foco que el propio clic le da al botón.
- La página saltó 807 px hacia arriba entre el inicio del clic de Playwright y el momento en que el botón recibió el foco. El campo quedó contra el borde inferior (927 px) y el panel, como corresponde, se abrió arriba.

El salto viene de `page.click()`: antes de hacer clic, Playwright comprueba que el elemento esté quieto y lo desplaza a la vista si lo considera necesario, y en algunas corridas reubicó la página. Es un efecto de la herramienta de pruebas, no del componente.

**Por qué no es un problema del componente.** Con el campo a 927 px, abajo quedan 33 px y arriba más de 800, así que abrir arriba es lo correcto. La ubicación se decide con la posición real del campo al abrir, y con la página quieta el panel se abre abajo siempre. Un usuario que hace clic con el mouse o abre el panel con el teclado no provoca ese desplazamiento.

**Corrección (0.6.0).** Solo en esas dos pruebas, el clic se hace con el mouse en el centro del botón (`page.mouse.click`), sin el desplazamiento automático de Playwright. Siguen siendo eventos reales de puntero (presionar, foco, soltar, clic). Las demás pruebas siguen abriendo el panel con `page.click()`, y `test_teclado_completo_y_escape_devuelve_el_foco` lo abre con Alt+↓.

**Verificación.** Con la página instrumentada, las dos pruebas solas fallaron en 13 de 40 corridas con `page.click()` y en 0 de 40 con el clic del mouse. La suite completa, con la corrección, pasó en 6 de 6 corridas seguidas, y esas dos pruebas junto con las de clic y teclado, en 40 de 40 corridas aisladas.


## Filtros progresivos y padding

Después de generar el catálogo, ejecutá `python -m pytest tests/visual/test_progressive_filters.py`.
Las pruebas cubren 1440, 992, 991, 390 y 320 px, padding de las tres variantes,
columnas y fechas, foco y teclado, estado anunciado por el botón, funcionamiento
sin JavaScript, recuperación del estado de sesión y envío de los filtros ocultos
tanto en búsquedas como en exportaciones.
