# Diccionario de datos

Definición preparada; porcentajes de faltantes **pendientes de medición**, disponibles luego en exploration_summary.json.

## Precios interim
| Variable | Tipo | Descripción/unidad | Faltantes esperados |
|---|---|---|---|
| date | datetime sin zona | Fecha de sesión NASDAQ | No |
| ticker | string | NVDA | No |
| open, high, low, close | float | OHLC reportado por proveedor, USD | No; se detiene si existen |
| adjusted_close | float | Cierre ajustado por proveedor, USD ajustados | No |
| volume | numérico | Acciones negociadas | No |
| dividends | float, si fuente entrega | Dividendo por acción reportado | Según fuente |
| stock_splits | float, si fuente entrega | Factor de split reportado | Según fuente |
| return_pct | float | 100 ln(AdjClose_t / AdjClose_t-1), % | Primera fila del warmup |

## Noticias interim
| Variable | Tipo | Descripción/unidad |
|---|---|---|
| article_id | string | SHA-256 de ticker, URL y timestamp |
| published_utc | datetime UTC | Fecha y hora publicada por proveedor |
| url | string | Identificador/enlace de fuente; no en muestra pública |
| source | string | Medio publicado, puede estar vacío |
| sentiment | float | Score específico del ticker entre -1 y 1 |
| relevance | float | Relevancia del ticker entre 0 y 1 |
| source_file | string | Snapshot de procedencia |
| asof_date | datetime | Primera sesión cuyo cierre es >= publicación |
| available_at_close_utc | datetime UTC | Cierre utilizado para alinear; no prueba latencia del proveedor |
| neg_intensity | float | max(0,-sentiment), entre 0 y 1 |

## Dataset processed
Incluye precios y estas variables:

| Variable | Tipo | Descripción | Faltantes esperados |
|---|---|---|---|
| news_count | int | Noticias válidas asignadas a ese cierre | No, cero sin noticias |
| has_news | bool | Existe al menos una noticia válida recuperada | No |
| sentiment_mean | float | Promedio ponderado por max(relevance,0.01) | Cero sin noticias, con has_news=false |
| neg_intensity | float | Promedio ponderado de intensidad negativa | Cero sin noticias |
| negative_share | float | Proporción de artículos con score negativo | Cero sin noticias |
| news_neg_lag1 | float | Intensidad de la sesión anterior | Primera sesión |
| target_date | datetime | Fecha de la siguiente sesión del dataset | Última sesión |
| target_return_next_pct | float | Rendimiento de la siguiente sesión, etiqueta | Última sesión |
| target_variance_proxy_next | float | Cuadrado del rendimiento siguiente (%²), etiqueta | Última sesión |
| year | int | Año de date, clave de partición | No |

En el pronóstico hecho al cierre de t para t+1 se usa neg_intensity_t. news_neg_lag1_t se usaría para pronosticar la varianza de t desde t-1. No desplazar ambas veces ni usar columnas target como variables predictoras. El retorno al cuadrado es un proxy ruidoso, no la varianza observada verdadera.
