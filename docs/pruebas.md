# Pruebas

```bash
python tools/build_catalog.py          # dist/ui-kit.html: lo usan las pruebas en el navegador
pytest                                 # todo (las de tests/visual/ se saltean sin Playwright o sin el catálogo)
python tests/visual/capture.py dist/ui-kit.html /tmp/actual
python tests/visual/compare.py /tmp/referencia /tmp/actual --esperados tests/visual/cambios-esperados.txt
```

## Prueba intermitente: `tests/visual/test_datetime.py::test_abajo_si_entra`

**Qué pasó.** Durante el desarrollo de la 0.6.0 una corrida completa falló en una sola prueba que no se repitió (no quedó registrado cuál). Para identificarla se corrió la suite completa varias veces seguidas sobre el mismo commit (`55d509c`): en 2 de 6 corridas falló `test_abajo_si_entra` con `assert ('above' == 'below')` (el panel de fecha y hora se abrió arriba del campo en lugar de abajo) y las otras 4 pasaron.

**Qué no es.**
- No depende de la escala tipográfica: la prueba es de la 0.5.0 y corre sobre el catálogo con la escala compacta, que es idéntica a la 0.5.0 (0 diferencias en las capturas).
- No se reproduce aislada: 32 repeticiones del mismo escenario fuera de la suite, con el procesador del navegador frenado 4, 12 y 20 veces, abrieron siempre abajo; en otras 50 el campo quedó siempre en la posición pedida.
- No es un error de ubicación del panel: con el campo a 120 px del borde superior de una ventana de 960 px, abajo sobran unos 780 px y el panel mide unos 430; el código elige «arriba» solo si abajo no entra.

**Causa probable.** La prueba ubicaba el campo con un solo `window.scrollBy` y hacía clic enseguida. Si algo cambia el alto de la página entre esos dos pasos (en la suite, la hoja de Google Fonts que el entorno de pruebas bloquea y responde con demora variable, o el dibujo diferido de los gráficos del catálogo), el campo queda más abajo de lo previsto y el panel, con razón, se abre arriba. Es un problema de la prueba, no del componente.

**Corrección (0.6.0).** `test_abajo_si_entra` y `test_arriba_si_abajo_no_entra` esperan las fuentes y repiten el desplazamiento hasta que el campo queda quieto dos cuadros seguidos en la posición pedida, y verifican esa posición antes del clic. Si vuelve a fallar, el mensaje incluye la posición del campo, el desplazamiento, el alto del panel y el de la ventana, para distinguir entre la prueba y el componente.

Con la corrección, 6 de 6 corridas completas seguidas pasaron (antes, 4 de 6).
