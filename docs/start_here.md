# Empieza aquí

## 1. Subir código
Completa los tres nombres en README. Crea el issue de tu tarea y la rama feature/project-setup en GitHub. Sube los archivos en esa rama siguiendo docs/github_steps.md. Este paquete no publicó cambios en GitHub ni creó issues/PR.

## 2. Probar precios
Desde terminal en la raíz, instala requirements.txt y ejecuta:

```bash
python -m src.ingestion.download_data --source prices
```

Si aparece HTTP 429, conserva la carpeta y vuelve a probar cuando el proveedor permita acceso. No ejecutes Run all repetidamente. En Databricks sigue 00_databricks_setup.ipynb y configura un Volume para evitar depender de almacenamiento temporal.

## 3. Comprobar noticias
NEWS_SENTIMENT está documentado como premium. Si ya tienes una API key con acceso, introdúcela con getpass; nunca pegues la clave en el chat o en GitHub. Una clave gratuita no garantiza el histórico necesario. Si no tienes acceso, los entregables de datos y exploración quedan pendientes: decide con el profesor una fuente permitida antes de cambiar el diseño. No hay que comprar un plan para probar el código.

Para una primera prueba de una ventana corta, crea un config JSON propio con fechas reducidas y usa una data-root diferente. El processing admite un periodo corto para explorar aunque no sea suficiente para ajustar GARCH. Para el proyecto final conserva 2025-01-01 a 2026-10-01 (fin exclusivo).

## 4. Generar tus evidencias
Cuando ambas adquisiciones terminen:

```bash
python -m src.processing.build_dataset
python -m src.processing.explore_data --reports-root reports
```

Ejecuta 01_exploration.ipynb y completa sus observaciones con lo que realmente obtuviste. Actualiza checklist, diccionario y arquitectura con volumen, cobertura y ubicación real. Comparte con tu equipo las tablas, no credenciales.

## 5. Abrir tu pull request
Usa docs/pull_request_draft.md y solicita revisión de un compañero. No marcar como completadas descarga, muestra, exploración observada ni colaboración hasta contar con evidencia real.
