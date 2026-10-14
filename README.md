# Stock Forecasting Pipeline: volatilidad de NVIDIA y noticias financieras

Proyecto de Datos Masivos, equipo de tres integrantes. Construimos un pipeline reproducible que adquiere precios diarios y noticias de NVDA, conserva snapshots, alinea ambas fuentes en el tiempo y prepara un dataset para comparar GARCH con GARCH-X.

## Integrantes
- Responsable de adquisición y procesamiento: **completar nombre**.
- Responsable de validación y pruebas: **completar nombre**.
- Responsable de benchmark y documentación técnica: **completar nombre**.

## Problema y pregunta principal
Las noticias podrían aportar información sobre la variabilidad de los rendimientos. Una unión incorrecta por fecha puede introducir información futura en un pronóstico.

**¿Agregar la intensidad de sentimiento negativo de noticias de NVDA mejora el pronóstico de varianza diaria del día bursátil siguiente frente a GARCH(1,1), al evaluar fechas posteriores al entrenamiento?**

## Objetivo
Construir y documentar el sistema de adquisición, almacenamiento, procesamiento y exploración que permita investigar esa pregunta. La superioridad predictiva es una hipótesis; este paquete no contiene resultados de modelos.

## Fuentes y alcance
- Yahoo Finance mediante yfinance: OHLCV, cierre ajustado y acciones corporativas.
- Alpha Vantage NEWS_SENTIMENT: publicación UTC, fuente, sentimiento y relevancia **específicos de NVDA**.
- Periodo de estudio: 2025-01-01 <= fecha < 2026-10-01. Precios: 90 días adicionales de contexto previo.
- Calendario NASDAQ, incluidos festivos, horario de verano y cierres tempranos.
- GDELT no se utiliza en este piloto; no se borran ni se alteran los datos que existan en Databricks.

## Estado actual
Código de adquisición/procesamiento y documentación preparados. Descarga con la cuenta del equipo, muestra real, exploración observada, validación independiente, pruebas del equipo y benchmark **pendientes** hasta ejecutarlos. Ningún archivo de ejemplo se presenta como dato real.

## Requisitos e instalación
Python 3.10 o posterior. Ejecuta desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
```

Para noticias necesitas una API key con permisos, cuota y acceso histórico suficientes. La documentación consultada el 13-oct-2026 clasifica NEWS_SENTIMENT como premium: una clave gratuita no garantiza acceso. Primero comprueba el acceso; no compres un plan por ejecutar este paquete.

## Obtención de datos
Primero prueba solo precios:

```bash
python -m src.ingestion.download_data --source prices
```

Para introducir la clave sin guardarla en un archivo o comando visible:

```bash
python -c "import os,runpy; from getpass import getpass; os.environ['ALPHAVANTAGE_API_KEY']=getpass('Alpha Vantage API key: '); runpy.run_module('src.ingestion.download_data',run_name='__main__')" --source news
```

Si tu entorno ya tiene ALPHAVANTAGE_API_KEY configurada, usa:

```bash
python -m src.ingestion.download_data --source news
```

El presupuesto max_news_requests limita cada ejecución. Las ventanas saturadas se dividen; pueden requerir más de 22 solicitudes. Una reejecución reutiliza respuestas válidas y no gasta solicitudes en ellas. Reanudar solo cuando la cuota del proveedor lo permita.

## Procesamiento y exploración
```bash
python -m src.processing.build_dataset
python -m src.processing.explore_data --reports-root reports
```

Los archivos grandes permanecen fuera de GitHub. `data/sample/` se llena con muestras reales después de procesar, no antes. Revisa derechos de uso antes de publicarlas; las muestras de noticias omiten URLs y textos.

## Databricks
Clona el repositorio como Git folder y abre `notebooks/00_databricks_setup.ipynb`. Sigue sus celdas en orden. Configura un Volume existente en el widget `data_root`; cada proyecto debe tener su propia subcarpeta. Los scripts mantienen compatibilidad con terminal aunque se lancen desde un notebook.

## Estructura
| Ruta | Contenido |
|---|---|
| data/raw | Snapshots y manifiestos de adquisición; no versionados |
| data/interim | Tablas limpiadas de precios y noticias |
| data/processed | Dataset diario CSV/Parquet y particiones ticker/año |
| data/sample | Muestras pequeñas reales que se generan al ejecutar |
| src/ingestion | Descargas y reanudación |
| src/processing | Limpieza, alineación y exploración |
| src/validation, tests | Tareas pendientes del compañero 1 |
| reports | Figuras y tablas observadas; se generan al ejecutar |
| docs | Alcance, fuentes, diccionario, arquitectura y colaboración |
| config | Configuración sin secretos |

## Limitaciones
Una acción diaria genera pocos miles de registros como máximo, no un volumen masivo. La complejidad se concentra en fuentes heterogéneas, trazabilidad y alineación temporal. Para justificar escalabilidad se medirán formatos y volúmenes sin afirmar que Spark acelera un dataset pequeño. Las fechas, scores y precios son snapshots actuales de los proveedores: no acreditan disponibilidad histórica point-in-time de sus revisiones.

## Trabajo pendiente
Consulta `docs/team_pending.md` y `docs/delivery_checklist.md`. GARCH-X, pronósticos, métricas y conclusiones financieras pertenecen a la fase de análisis final.
