# Cally 0.9.2 (copia sin modificar)

Componentes web de calendario que usa `gn-calendar` (selectores de fecha y de fecha y hora de GENEOS UI).

- Proyecto: https://github.com/WickyNilliams/cally
- Licencia: MIT (ver `LICENSE`).
- Origen: paquete npm `cally@0.9.2`, archivo `dist/cally.js`. El tarball se verificó contra el
  registro de npm con el `shasum` `41e725570ebc1d5eadeefa6a81e29563c4f0a182`.
- SHA-256 de `cally.js`: `4dcba6a3b8ec63b66ff2fbfc6cf47b7dee1eb4896eac89fe7487d82e28e15870`.
  `tests/test_datetime.py` comprueba este valor para detectar cambios accidentales.
- Es un módulo ES sin dependencias externas (incluye Atomico). Se carga con
  `<script type="module">`; GENEOS UI no lo modifica, solo lo estiliza con `::part()`.

Para actualizarlo: reemplazar `cally.js` y `LICENSE` por los del nuevo paquete, actualizar la
versión y el hash en este archivo y en el test, y repetir las pruebas de teclado y lector de
pantalla de `tests/visual/test_datetime.py`.
