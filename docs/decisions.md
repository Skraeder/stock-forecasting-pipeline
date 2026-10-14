# Decisiones de adquisición y procesamiento

## Pronosticar volatilidad
Razón: el piloto más reciente compara GARCH y GARCH-X, que modelan varianza condicional. Alternativa: precio puntual con browniano/ARIMA. Consecuencia: etiquetas y evaluación final se centrarán en varianza; no prometer dirección o precio exacto.

## Sentimiento específico de NVDA
Razón: una noticia puede tener tono general distinto al relativo a la empresa. Alternativa: tono general o GDELT Events. Consecuencia: necesitamos ticker_sentiment y un acceso de Alpha Vantage compatible; GDELT no se sustituye silenciosamente.

## Calendario NASDAQ en vez de las 16:00 fijas
Razón: hay festivos, horario de verano y cierres tempranos. Consecuencia: nueva dependencia; asignación de noticias posterior al cierre al siguiente cierre real. Supuesto: publicación UTC como disponibilidad; latencia real desconocida.

## CSV/JSON raw y Parquet preparado
Razón: conservar snapshots y producir tablas tipadas. Alternativa: solo CSV o Delta. Consecuencia: PyArrow y manifiestos; benchmark independiente pendiente. Raw Yahoo es salida del cliente, no copia HTTP original.

## Detenerse ante cobertura incompleta
Razón: no confundir error de API con ausencia de artículos ni entrenar sobre ventanas saturadas. Alternativa: continuar con ceros. Consecuencia: se reanuda por caché y se debe comprobar permiso/histórico.

## Pandas para el piloto
Razón: frecuencia diaria y una acción. Alternativa: PySpark desde el inicio. Consecuencia: sistema no distribuido, modular y migrable; no afirmar rendimiento distribuido sin evidencia.

## Snapshot reproducible
Razón: los proveedores revisan históricos. Se registra extracción/checksum y se reutiliza la copia. Consecuencia: reproducible con snapshot, pero no prueba del dato que un operador conocía en cada fecha histórica.

## Piso de relevancia 0.01
Razón: conservar convención del piloto y evitar peso total cero. Alternativa: omitir relevancia cero o media simple. Consecuencia: artículos de relevancia cero reciben peso pequeño; revisar sensibilidad en el análisis final.

## Pendiente del compañero 2
Añadir mediciones CSV/Parquet y justificar decisiones con tiempos, memoria, volumen e igualdad del resultado.
