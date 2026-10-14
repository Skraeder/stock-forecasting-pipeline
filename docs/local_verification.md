# Verificación local del código

Fecha: 13 de octubre de 2026.

- Los cinco notebooks pasan validación de formato nbformat.
- Los módulos pasan compilación de Python.
- Se ejecutaron 18 comprobaciones internas sobre un fixture sintético identificado, ubicado fuera del paquete y eliminado al terminar. Ningún dato de ese fixture se incluye en data/sample ni se presenta como resultado financiero.
- Se comprobó el flujo completo raw/interim/processed y la generación de cuatro figuras exploratorias; cálculo de rendimientos; tratamiento de un festivo y cierre temprano; noticia posterior al cierre; fin de semana; rezago; etiqueta final faltante; conteo agregado; detección de huecos y checksum alterado.
- Con respuestas HTTP simuladas se comprobó división de ventana saturada, reutilización de caché y rechazo de respuesta API sin feed. No prueba acceso real a Alpha Vantage.

## Intento externo
La descarga real de NVDA desde este entorno devolvió HTTP 429 / YFRateLimitError. No se recibieron precios ni se generó una muestra real. No se repitieron descargas para insistir contra el límite. La extracción debe probarse desde el entorno autorizado del equipo cuando el servicio permita acceso.

No se consultó Alpha Vantage con una clave personal: aún falta comprobar permisos NEWS_SENTIMENT, histórico y cuota. No se ejecutó el pipeline en el workspace Databricks del usuario. No se ajustaron modelos.

## Distinción respecto a tareas del equipo
Esta comprobación de implementación no reemplaza los módulos de validación, las pruebas mantenidas en tests/ ni el benchmark del equipo. Esas tareas están marcadas como pendientes, al igual que las métricas obtenidas de datos reales.
