# Tareas pendientes de los otros dos integrantes

## Compañero 1: validaciones y pruebas
Crear src/validation/validate_dataset.py y tests con casos reproducibles. Validar columnas, tipos, faltantes, duplicados, rangos, consistencia temporal, entre tablas y volumen. Verificar noticias posteriores al cierre, fin de semana, cambio de horario, cierre temprano y ausencia de noticias. Comprobar que target_* nunca entra en features. Completar docs/validation.md con datos reales y revisar diccionario. No basta entregar un archivo vacío o solo revisar un PR.

## Compañero 2: desempeño y decisiones
Implementar operación medible sobre CSV y Parquet del MISMO dataset. Registrar volumen, tiempo, memoria, repeticiones y verificación de igualdad. Considerar que caché y tamaño pequeño sesgan resultados; no presentar replicación artificial como más observaciones independientes. Completar decisions y arquitectura con evidencia, incluyendo limitaciones del acceso externo.

## Participación individual
Primer parcial: por persona dos commits relevantes, un PR propio, revisión de otro PR y participación en issue. Segundo: contribución técnica y contribución de documentación/validación; issue por tarea principal, ramas vinculadas, PR revisados y evidencia de integración. No fabricar conflictos ni atribuir a alguien código que no desarrolló.

## Revisión propuesta
Responsable pipeline revisa compañero 1; compañero 1 revisa compañero 2; compañero 2 revisa responsable pipeline. Los nombres están por completar; no usar nombres asumidos.
