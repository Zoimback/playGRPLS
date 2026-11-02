# Feature Specification: Poblacion, cola y batallas contra bandidos

**Feature Branch**: `feature/grepolis-desktop.0.1`

**Created**: 2026-11-02

**Status**: Draft

**Input**: User description: "Ampliar el bot para reaccionar a poblacion cero, llenar una cola de hasta dos construcciones cuando existan demasiados recursos, investigar tropas y simulador de batallas, elegir una estrategia contra bandidos, enviar tropas, esperar su llegada y recoger la recompensa."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evitar poblacion bloqueada (Priority: P1)

Como propietario de una ciudad, quiero que el bot priorice la ampliacion de la granja cuando la poblacion disponible sea cero, para que la ciudad pueda seguir creciendo.

**Why this priority**: Poblacion cero bloquea construcciones y unidades. Resolverlo evita que el bot quede detenido.

**Independent Test**: Proporcionar una ciudad con poblacion disponible cero, granja ampliable y recursos suficientes; verificar que la granja se convierte en el siguiente objetivo valido.

**Acceptance Scenarios**:

1. **Given** poblacion disponible igual a cero y granja ampliable, **When** comienza la decision de construccion, **Then** la granja se prioriza antes que otros edificios del mismo nivel.
2. **Given** poblacion cero pero granja no ampliable o bloqueada, **When** se evalua la ciudad, **Then** el bot conserva una razon explicita y no inicia una ampliacion invalida.
3. **Given** poblacion suficiente, **When** se evalua la ciudad, **Then** la regla especial de granja no desplaza la prioridad normal por nivel.

### User Story 2 - Llenar cola de construccion (Priority: P1)

Como propietario de una ciudad, quiero que el bot use los dos espacios permitidos de la cola cuando existan recursos sobrantes, sin superar el limite ni comprometer recursos necesarios.

**Why this priority**: Mantener la cola llena reduce tiempos muertos y usa recursos acumulados.

**Independent Test**: Proporcionar cola vacia, cola con una orden y cola llena, junto con recursos y edificios validos; verificar que solo se añaden las ordenes permitidas.

**Acceptance Scenarios**:

1. **Given** cola vacia y suficientes recursos para dos edificios, **When** se ejecuta la planificacion, **Then** programa hasta dos ampliaciones respetando prioridad y costes acumulados.
2. **Given** una orden activa y recursos suficientes para otra, **When** se ejecuta la planificacion, **Then** añade como maximo una orden adicional.
3. **Given** dos ordenes activas, **When** se ejecuta la planificacion, **Then** no envia otra construccion.
4. **Given** recursos sobrantes pero ninguna ampliacion valida, **When** se ejecuta la planificacion, **Then** conserva los recursos y registra la razon.

### User Story 3 - Evaluar y librar batalla contra bandidos (Priority: P1)

Como propietario de una ciudad, quiero conocer mis tropas, comparar una fuerza bandida y elegir una estrategia con resultado seguro antes de enviar tropas.

**Why this priority**: Las batallas pueden perder tropas y recursos. El bot debe evitar acciones sin una prediccion suficiente.

**Independent Test**: Proporcionar tropas propias, fuerza bandida, simulaciones posibles, distancia y recompensa; verificar que el bot elige solo una estrategia con resultado aceptable o decide esperar.

**Acceptance Scenarios**:

1. **Given** tropas propias y una fuerza bandida observable, **When** se abre el simulador, **Then** el bot obtiene resultados para las composiciones permitidas sin iniciar la batalla.
2. **Given** una estrategia con resultado seguro y tropas disponibles, **When** la llegada y el coste son validos, **Then** el bot selecciona esa estrategia y programa la llegada.
3. **Given** ninguna estrategia con resultado seguro, **When** se evalua la batalla, **Then** no envia tropas y registra la causa.
4. **Given** tropas en camino, **When** la batalla aun no llega, **Then** el bot no duplica el envio.
5. **Given** una batalla resuelta y recompensa disponible, **When** comienza el ciclo de recompensas, **Then** recoge la recompensa una sola vez y registra el resultado.

### User Story 4 - Recuperar batalla y recompensas (Priority: P2)

Como operador, quiero que el bot persista viajes, resultados pendientes y recompensas para continuar después de reiniciar.

**Why this priority**: El viaje puede durar más que una ejecución y perder la recompensa desperdicia el resultado.

**Independent Test**: Persistir un viaje y una recompensa pendiente, reiniciar el proceso y verificar que se restaura la siguiente consulta sin repetir el ataque.

**Acceptance Scenarios**:

1. **Given** un viaje guardado con hora de llegada futura, **When** el bot reinicia, **Then** programa la comprobación en esa hora.
2. **Given** una recompensa disponible ya registrada, **When** el ciclo se ejecuta, **Then** recoge una vez y marca la recompensa como confirmada.
3. **Given** una respuesta ambigua después de enviar tropas, **When** se recupera el estado, **Then** consulta movimientos antes de reintentar.

### Edge Cases

- Poblacion cero y granja sin recursos o dependencias.
- Cola con uno o dos espacios ocupados.
- Dos edificios requieren los mismos recursos y el primero consume el saldo necesario para el segundo.
- Capacidad de almacenamiento insuficiente para seguir acumulando.
- El servidor cambia la cola entre consulta y envio.
- No hay tropas de combate, hay tropas insuficientes o solo hay unidades defensivas.
- La fuerza bandida no se puede observar o el simulador no devuelve resultado.
- El simulador devuelve derrota, empate o resultado incompleto.
- El tiempo de llegada cruza el reinicio o el reloj local difiere del servidor.
- La recompensa deja de estar disponible o ya fue recogida.
- Una accion de batalla expira por CSRF, timeout o sesion caducada.
- El bot no debe gastar oro ni enviar tropas sin una estrategia validada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El bot MUST detectar poblacion disponible igual a cero antes de elegir una ampliacion.
- **FR-002**: El bot MUST priorizar la granja cuando poblacion cero, la granja sea ampliable, cumpla dependencias y pueda pagarse.
- **FR-003**: El bot MUST tratar la cola como capacidad maxima de dos ordenes.
- **FR-004**: El bot MUST considerar recursos y poblacion consumidos por orden previa al planificar la siguiente orden.
- **FR-005**: El bot MUST detener la planificacion cuando la cola tenga dos ordenes activas.
- **FR-006**: El bot MUST usar edificios adicionales cuando existan recursos sobrantes y candidatos validos, sin construir por encima de la capacidad de cola.
- **FR-007**: El bot MUST consultar tropas disponibles por ciudad antes de evaluar una batalla.
- **FR-008**: El bot MUST identificar objetivos de bandidos, fuerza observable, tiempo de llegada, cooldown devuelto por el servidor y recompensa disponible.
- **FR-009**: El bot MUST consultar el simulador antes de seleccionar una composicion de ataque.
- **FR-010**: El bot MUST seleccionar solo estrategias cuyo resultado cumpla el umbral de seguridad configurado.
- **FR-011**: El bot MUST abstenerse de enviar tropas si faltan datos, el simulador falla o ninguna estrategia es segura.
- **FR-012**: El bot MUST evitar enviar tropas duplicadas al mismo objetivo mientras exista un movimiento pendiente.
- **FR-013**: El bot MUST programar la siguiente comprobacion con la hora de llegada devuelta por el servidor.
- **FR-014**: El bot MUST recoger una recompensa disponible una sola vez después de una batalla confirmada.
- **FR-015**: El bot MUST persistir cola, tropas en movimiento, estrategia seleccionada, llegada, estado de batalla y recompensa.
- **FR-016**: El bot MUST mantener `DRY_RUN=true` por defecto para construcciones adicionales, envios y recompensas.
- **FR-017**: El bot MUST registrar decisiones y razones sin credenciales, cookies, CSRF ni payloads sensibles.

### Key Entities

- **Estado de población**: Poblacion libre, maxima, consumo previsto y regla de granja.
- **Plan de cola**: Ordenes activas, espacios libres, costes acumulados y edificios candidatos.
- **Fuerza propia**: Unidades disponibles por ciudad y unidades comprometidas en movimientos.
- **Objetivo bandido**: Nivel, ubicacion, fuerza observable, cooldown y recompensa.
- **Simulación**: Composición, resultado, pérdidas previstas y nivel de seguridad.
- **Movimiento de tropas**: Origen, objetivo, unidades, hora de llegada y estado.
- **Recompensa**: Resultado disponible, tipo, cantidad y estado de recogida.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el 100% de los ciclos con poblacion cero y granja valida, la granja aparece antes que cualquier candidato normal.
- **SC-002**: En el 100% de los ciclos, la cola nunca supera dos construcciones activas.
- **SC-003**: En al menos el 95% de los ciclos con recursos sobrantes y candidatos validos, la cola queda llena sin incumplir costes ni dependencias.
- **SC-004**: El bot no envia ninguna batalla cuando falta resultado de simulador o la estrategia no cumple el umbral de seguridad.
- **SC-005**: El bot no duplica movimientos ni recoge una recompensa confirmada más de una vez durante una prueba de reinicio.
- **SC-006**: Durante una prueba de 24 horas, las decisiones de cola, batalla y recompensa quedan persistidas y recuperables.
- **SC-007**: El 100% de los logs de batalla contiene objetivo, estrategia, resultado, llegada y siguiente acción sin secretos.

## Assumptions

- La cola máxima observada para la primera versión es de dos construcciones.
- La granja es la solución prioritaria cuando poblacion libre es cero.
- El bot usa solo tropas disponibles y no gasta oro en la primera versión.
- Una batalla solo se autoriza tras una simulación con resultado seguro configurable.
- El simulador, fuerza bandida y endpoint de recompensa deben confirmarse antes de activar escritura.
- El servidor proporciona horas de llegada, cooldowns y estados de recompensa más fiables que el reloj local.

## Out of Scope

- Ataques contra jugadores, conquistas, transporte y comercio.
- Estrategias premium o gasto de oro.
- Batallas sin simulador verificable.
- Automatizar una batalla real durante la investigación.
