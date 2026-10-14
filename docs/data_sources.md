# Fuentes de datos

Consultado: 13 de octubre de 2026. El acceso debe comprobarse con la cuenta del equipo.

| Aspecto | Precios | Noticias |
|---|---|---|
| Origen | Yahoo Finance | Alpha Vantage |
| Propietario/servicio | Yahoo Finance; cliente comunitario yfinance | Alpha Vantage; artículos de diversas fuentes |
| Método | yf.download | GET /query, NEWS_SENTIMENT |
| Formato recibido | DataFrame serializado a CSV sin limpieza | Respuesta JSON sin modificar |
| Unidad | ticker/sesión | noticia/ticker/publicación |
| Frecuencia | diaria para este proyecto | timestamps de publicación; extracción histórica mensual subdivisible |
| Volumen estimado | cientos de sesiones del periodo, más warmup; exacto al ejecutar | desconocido hasta descargar; máximo 1000 resultados por consulta |
| Variables | OHLCV, Adj Close, dividendos, splits | time_published, URL, source, ticker_sentiment_score, relevance_score |
| Restricciones | servicio y cliente sin garantía de disponibilidad; verificar licencia/uso | permisos/plan/cuota/histórico; NEWS_SENTIMENT figura como premium |
| Problemas | revisiones, ajustes corporativos, fechas faltantes, fallo/red | truncación, cobertura editorial, duplicados, puntuaciones ausentes |

## Documentación oficial
- yfinance download: https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html
- yfinance, uso e independencia de Yahoo: https://ranaroussi.github.io/yfinance/
- Alpha Vantage, NEWS_SENTIMENT: https://www.alphavantage.co/documentation/#news-sentiment
- Calendarios y cierres especiales: https://pandas-market-calendars.readthedocs.io/en/latest/usage.html
- Volumes en Databricks: https://docs.databricks.com/aws/en/volumes/volume-files

## Adquisición
Los parámetros no secretos y SHA-256 quedan en metadatos/manifiestos. La API key únicamente vive en la variable de entorno y no se agrega a logs. Una respuesta sin feed es error, no un mes con cero noticias. Cada respuesta que alcanza el límite se divide en ventanas más pequeñas; solo hojas no saturadas entran al manifiesto final. El filtro posterior utiliza [inicio,fin), aunque la API repita un artículo de frontera.

## Muestras y redistribución
El repositorio no trae datos inventados. La ejecución genera muestras pequeñas; noticias sin URL ni texto. Antes de hacerlas públicas el equipo debe verificar condiciones de uso: quitar textos no otorga automáticamente licencia de redistribución. Si la redistribución no está permitida, proporcionar el script al profesor y acceso autorizado local.
