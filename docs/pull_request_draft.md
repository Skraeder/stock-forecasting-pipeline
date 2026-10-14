# Título
feat: add reproducible NVDA data ingestion and preparation

# Descripción
El proyecto necesita adquirir y alinear precios diarios de NVIDIA y sentimiento de noticias antes de comparar GARCH con GARCH-X. Este cambio agrega scripts de adquisición con snapshots/caché, procesamiento por calendario NASDAQ, capas raw/interim/processed y notebooks de exploración, junto con documentación de alcance y fuentes.

## Verificación
- Comprobación local de rutas de transformación y alineación: ver docs/local_verification.md.
- Descarga externa, muestra real y ejecución en Databricks pendientes hasta contar con acceso a los proveedores.
- Validaciones/tests del compañero 1 y benchmark del compañero 2 permanecen pendientes.

## Limitaciones
NEWS_SENTIMENT requiere permisos/plan e histórico suficientes. Una respuesta incompleta detiene el pipeline. No se incluyen resultados de modelos ni datos inventados.

Relacionar con el issue real: `Refs #NUMERO` (reemplazar antes de publicar).
