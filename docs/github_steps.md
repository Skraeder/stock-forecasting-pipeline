# Cómo subir tu parte, paso a paso

1. Conserva tu repositorio actual stock-forecasting-pipeline. Este ZIP no cambia GitHub automáticamente.
2. Invita a ambos compañeros en Settings > Collaborators.
3. En Issues > New issue, crea `Definir alcance y construir pipeline de NVDA` y asígnatelo. Copia como checklist: alcance, fuentes, adquisición, procesamiento, exploración, muestra y arquitectura.
4. Crea otros dos issues: `Implementar validaciones y pruebas` y `Comparar formatos y documentar desempeño`. Los compañeros completarán contenido y asignación.
5. Desde el selector main crea `feature/project-setup`. Para más adelante, usa ramas separadas por tarea.
6. Descomprime el paquete en tu computadora. Para conservar subcarpetas en Add file > Upload files, arrastra el CONTENIDO de stock-forecasting-pipeline, no el ZIP ni su carpeta exterior. Verifica que no quede stock-forecasting-pipeline/stock-forecasting-pipeline. No subas data/raw, interim, processed ni una clave. La interfaz puede omitir archivos ocultos: revisa .gitignore por separado.
7. Antes del commit completa los tres nombres en README. Primer commit sugerido: `docs: define NVDA project scope and architecture`. Una segunda contribución puede ser `feat: add ingestion and processing pipeline`; realiza los commits sobre cambios reales, no solo para aumentar cantidad.
8. Abre Pull requests > New pull request; base main, compare feature/project-setup. Usa docs/pull_request_draft.md para descripción y menciona el número real de tu issue; no cierres el issue hasta completar su evidencia de ejecución.
9. Tu compañero revisa el PR desde su cuenta. Después integra a main. Guarda enlaces para evaluación. Para el segundo parcial deben conservarse revisiones, issues e integración, no únicamente la carpeta final.
10. En tu Git folder de Databricks, haz Pull de main. Abre notebooks/00_databricks_setup.ipynb y corre las celdas en orden. Usa un Volume propio para datos.
11. Cuando se generen muestras reales, figuras y observaciones, súbelas en otra rama/PR tras revisar permisos y salidas. No publiques claves, JSON completos ni salida autenticada.

Alternativa con Git local (después de clonar el repositorio real): copia los archivos del paquete, crea la rama, git add de rutas específicas, commit y push. No ejecutar git init dentro del ZIP como sustituto del repositorio compartido.
