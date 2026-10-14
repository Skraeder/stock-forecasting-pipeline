# Alcance del proyecto

## Contexto
La volatilidad cambia a través del tiempo. Queremos estudiar si una señal de noticias específica de una empresa aporta información incremental para pronosticarla. El primer reto consiste en unir datos con distintas unidades de análisis sin usar publicaciones futuras.

## Pregunta principal
¿Agregar intensidad negativa de noticias de NVDA mejora el pronóstico de varianza diaria del siguiente día bursátil frente a GARCH(1,1), evaluando fechas posteriores al entrenamiento?

## Preguntas secundarias
1. ¿Qué proporción de sesiones tiene noticias válidas recuperadas?
2. ¿Existen duplicados, huecos bursátiles o ventanas saturadas del proveedor?
3. ¿Cómo cambia la distribución de rendimientos y sentimiento en el periodo?
4. ¿En qué fechas la alineación por cierre difiere de una unión por fecha calendario?
5. ¿Qué formato permite leer el mismo dataset con menor tiempo y memoria?

## ¿Qué representa una fila?
- Precios: una sesión bursátil de NVDA.
- Noticias: una combinación ticker + URL + publicación UTC; no equivale necesariamente a un hecho económico único.
- Dataset procesado: una sesión de NVDA con precio, rendimiento y noticias disponibles al cierre. Su etiqueta es el rendimiento/retorno al cuadrado de la siguiente sesión observada.

## Alcance
NVDA, frecuencia diaria, 2025-01-01 a 2026-09-30. Adquisición, capas raw/interim/processed, exploración, validación y evidencia de colaboración. Para contexto se descargan 90 días anteriores de precios. No noticias GDELT ni trading automático.

## Limitaciones
NEWS_SENTIMENT requiere acceso compatible y puede restringir histórico/cuota. La respuesta sin saturación no garantiza exhaustividad ni ausencia de sesgos editoriales. Precio ajustado y sentimiento obtenidos hoy pueden contener revisiones históricas. El calendario de publicación no prueba el instante en que el proveedor hizo accesible cada score. Cero artículos recuperados no prueba ausencia de noticias reales. Una sola acción limita volumen, generalización y capacidad de demostrar procesamiento distribuido.

## Posibles usuarios y valor esperado
Equipo académico y profesor: un sistema reproducible y auditable para estudiar la contribución de noticias a un modelo de volatilidad. No se ofrece una recomendación de inversión.

## Criterios de finalización de tu parte
Código ejecutable por módulos; snapshots y logs sin claves; manifiestos completos; transformaciones descritas; notebook exploratorio listo; muestras y figuras generadas con fuentes reales; PR revisado. La ejecución externa y revisión se registran como pendientes mientras no existan.
