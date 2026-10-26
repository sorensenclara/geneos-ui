# Publicación desde Mac

1. Descomprimir este ZIP en Descargas.
2. Abrir Terminal y ejecutar:

```bash
cd ~/Downloads/geneos-ui-github
git init
git branch -M main
git add .
git commit -m "GENEOS UI Kit 0.1.0 - catalogo y pruebas"
git remote add origin https://github.com/sorensenclara/geneos-ui.git
git push -u origin main
```

Si GitHub creó el repositorio con README o un commit inicial, detenerse si `git push` es rechazado: no forzar.

3. En GitHub: Settings > Pages > Build and deployment > Source: GitHub Actions.
4. Revisar Actions: Tests y Publicar UI Kit.
5. URL esperada cuando el despliegue termine: https://sorensenclara.github.io/geneos-ui/

No se crea tag ni se instala en los productos antes de la aprobación visual.
