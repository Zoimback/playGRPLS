# Research

## Observacion real

La consulta autenticada devolvio:

- Modelo `Units`: 62 `sword`; el resto de unidades de combate observadas estaban en 0.
- Modelo `PlayerAttackSpot`: nivel 19, `town_id` 3856, `reward_available=true`, recompensa de 5 `rider`, `cooldown_duration=300` en esa captura y `units=[]`.
- Coleccion `Attacks`: vacia en la captura.
- Colecciones de movimientos: sin ataque activo observable.
- Colecciones `CampaignDroppedUnits`: vacia en la captura.

## Decision: Priorizar granja con poblacion cero

Si poblacion libre es cero, la granja debe ganar prioridad solo cuando el servidor permita ampliar, se cumplan dependencias y existan recursos.

## Decision: Planificar hasta dos construcciones

El bot debe consultar la capacidad real de cola antes de llenar el segundo espacio. Debe descontar recursos y poblacion de ordenes ya planificadas.

## Decision: Batalla segura antes que batalla rapida

No se debe enviar tropas con solo datos del objetivo. Hace falta fuerza enemiga y resultado del simulador. Si falta uno, decision es esperar.

`cooldown_duration` y `cooldown_at` son dinamicos. El valor observado `300` no es una constante.

## Riesgo de investigacion

La sesion DevTools no mantuvo el mundo abierto durante toda la investigacion. La consulta HTTP confirmo metadatos de tropas y objetivo, pero no confirmo payload de simulador, envio de tropas ni recogida de recompensa. Esos contratos deben capturarse en una sesion autenticada antes de activar mutaciones.
