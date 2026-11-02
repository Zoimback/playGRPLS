# Feature Specification: Bot autónomo de construcciones y aldeas

**Feature Branch**: `feature/grepolis-desktop.0.1`

**Created**: 2026-11-02

**Status**: Draft

**Input**: User description: "Crear un bot autónomo para Grepolis que gestione construcciones y recoja recursos de aldeas agrícolas según reglas explícitas de prioridad, disponibilidad, planificación, persistencia, aislamiento de errores y ejecución segura en modo DRY_RUN."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gestionar construcciones (Priority: P1)

Como propietario de una ciudad, quiero que el bot consulte la cola y el estado real de los edificios para iniciar como máximo una ampliación válida y programar la siguiente comprobación.

**Why this priority**: La construcción es una función principal del bot y requiere decisiones basadas en recursos, población, requisitos y tiempos reales.

**Independent Test**: Proporcionar una ciudad con cola, edificios y recursos conocidos; ejecutar un ciclo y verificar la decisión, la ausencia de acciones inválidas y la próxima comprobación.

**Acceptance Scenarios**:

1. **Given** una construcción activa, **When** comienza un ciclo, **Then** el bot no inicia otra, conserva la hora de finalización recibida y programa la comprobación después de esa hora más el margen configurado.
2. **Given** una cola vacía y varios edificios ampliables, **When** se ejecuta el ciclo, **Then** descarta los no ampliables, los que tienen dependencias pendientes y los que no cumplen población o capacidad.
3. **Given** varios candidatos válidos, **When** se ordenan, **Then** el bot elige el nivel más bajo y conserva el orden original del servidor cuando los niveles empatan.
4. **Given** que el candidato de menor nivel no puede pagarse, **When** existe otro candidato pagable, **Then** el bot prueba el siguiente candidato según prioridad e inicia solo uno.
5. **Given** que ningún candidato puede pagarse, **When** existe producción positiva y capacidad de almacenamiento suficiente, **Then** calcula la próxima comprobación cuando el candidato pueda pagarse sin acumular por encima del almacén.
6. **Given** que una ampliación se inicia correctamente, **When** el servidor devuelve su finalización, **Then** esa hora gobierna la siguiente comprobación.

### User Story 2 - Recoger recursos de aldeas (Priority: P1)

Como propietario de una ciudad, quiero que el bot revise mis aldeas configuradas y recoja recursos con la opción de cinco minutos cuando cada aldea esté disponible.

**Why this priority**: La recogida frecuente mantiene los recursos y debe funcionar sin depender del ciclo de construcciones.

**Independent Test**: Proporcionar aldeas con estados disponibles, futuras, inactivas y erróneas; ejecutar el ciclo y verificar que procesa cada una de forma independiente.

**Acceptance Scenarios**:

1. **Given** una aldea configurada y disponible, **When** comienza el ciclo agrícola, **Then** solicita la recogida de recursos de cinco minutos y registra el resultado.
2. **Given** una aldea cuyo momento de disponibilidad aún no ha llegado, **When** se ejecuta el ciclo, **Then** no envía una recogida y conserva su próxima oportunidad.
3. **Given** varias aldeas y un error en una de ellas, **When** se procesa el ciclo, **Then** el bot registra el error y continúa con las demás.
4. **Given** un ciclo agrícola completado, **When** se programa el siguiente, **Then** la próxima ejecución queda a 300 segundos salvo que el estado real indique una espera posterior.

### User Story 3 - Mantener ejecución segura y recuperable (Priority: P1)

Como operador, quiero que construcciones y aldeas funcionen de manera independiente, con estado persistente y modo seguro, para recuperar el bot después de fallos o reinicios sin duplicar acciones.

**Why this priority**: La autonomía solo es fiable si una tarea fallida no detiene la otra y el proceso puede continuar después de reiniciar.

**Independent Test**: Persistir tareas, simular reinicio, errores de red y fallo de un ciclo; verificar restauración, reintentos limitados, aislamiento y ausencia de duplicados.

**Acceptance Scenarios**:

1. **Given** tareas pendientes guardadas, **When** el bot reinicia, **Then** restaura sus objetivos y próximas ejecuciones desde el estado persistido.
2. **Given** un fallo de construcción, **When** llega una ejecución agrícola, **Then** el ciclo agrícola continúa sin quedar bloqueado por la construcción.
3. **Given** un fallo agrícola, **When** llega una ejecución de construcción, **Then** el ciclo de construcción continúa sin quedar bloqueado por las aldeas.
4. **Given** una respuesta temporalmente fallida, **When** reintentar sea seguro, **Then** el bot aplica espera progresiva y un límite de intentos sin generar peticiones innecesarias.
5. **Given** `DRY_RUN=true`, **When** el bot decide una construcción o recogida, **Then** registra la acción prevista sin modificar el juego.
6. **Given** `DRY_RUN=false` y autorización explícita, **When** una acción es válida, **Then** ejecuta solo la acción decidida y registra la respuesta del servidor.

### Edge Cases

- La cola contiene datos incompletos o una finalización ausente.
- Dos edificios tienen el mismo nivel y el servidor devuelve un orden estable.
- El candidato de menor nivel carece de un recurso, pero otro candidato sí puede pagarse.
- La producción de un recurso es cero o negativa.
- El almacén no puede contener el déficit calculado antes de la próxima producción.
- La población disponible cambia entre la consulta y la decisión.
- Una aldea no tiene relación activa, no tiene `lootable_at` o devuelve una respuesta inválida.
- La opción de cinco minutos no está disponible para una aldea concreta.
- El reloj local difiere del tiempo devuelto por el servidor.
- La sesión caduca durante una petición y la reautenticación falla.
- El estado JSON está corrupto, bloqueado o no puede guardarse de forma segura.
- El proceso se reinicia después de enviar una acción, pero antes de confirmar su respuesta.
- Una tarea atrasada no debe ejecutarse repetidamente para compensar cada intervalo perdido.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El bot MUST consultar la cola de construcción antes de cada decisión de construcción.
- **FR-002**: El bot MUST abstenerse de iniciar una ampliación mientras exista una construcción activa.
- **FR-003**: El bot MUST programar la comprobación posterior usando la finalización recibida del servidor y un margen configurable.
- **FR-004**: El bot MUST descartar edificios con `can_upgrade = false`, dependencias pendientes, población insuficiente o capacidad de almacenamiento insuficiente.
- **FR-005**: El bot MUST priorizar el edificio con menor nivel y conservar el orden original del servidor en empates.
- **FR-006**: El bot MUST probar candidatos posteriores cuando el candidato prioritario no pueda pagarse.
- **FR-007**: El bot MUST calcular la espera de recursos usando recursos actuales, costes, producción por hora y capacidad máxima del almacén.
- **FR-008**: El bot MUST usar la hora de finalización devuelta por el servidor después de iniciar una ampliación.
- **FR-009**: El bot MUST consultar todas las aldeas agrícolas configuradas en cada ciclo agrícola.
- **FR-010**: El bot MUST evaluar individualmente disponibilidad y estado de cada aldea.
- **FR-011**: El bot MUST usar siempre la opción de recogida de cinco minutos para recoger recursos.
- **FR-012**: El bot MUST repetir el ciclo agrícola cada 300 segundos, salvo una espera posterior indicada por el estado real.
- **FR-013**: El bot MUST mantener ciclos de construcciones y aldeas independientes, aunque compartan la sesión autenticada.
- **FR-014**: El fallo de una aldea MUST NOT impedir el procesamiento de las demás aldeas.
- **FR-015**: El fallo de un ciclo MUST NOT detener el otro ciclo.
- **FR-016**: El bot MUST guardar tareas, próximas ejecuciones, objetivos y resultados en estado persistente recuperable.
- **FR-017**: El bot MUST restaurar el estado después de reiniciar sin repetir una acción ya confirmada.
- **FR-018**: El bot MUST tratar errores de red, sesión y respuestas inválidas con reintentos limitados cuando reintentar sea seguro.
- **FR-019**: El bot MUST registrar decisiones, acciones previstas o ejecutadas, respuestas, errores y próximas ejecuciones sin registrar credenciales, cookies ni tokens.
- **FR-020**: El bot MUST mantener `DRY_RUN=true` por defecto y no modificar el juego sin autorización explícita para desactivarlo.
- **FR-021**: El bot MUST usar datos y tiempos recibidos del servidor cuando estén disponibles, sin sustituirlos por estimaciones locales.
- **FR-022**: El bot MUST funcionar continuamente sin navegador gráfico y con consumo compatible con una Raspberry Pi Zero 2 W.

### Key Entities

- **Ciudad**: Ciudad administrada, con recursos, producción, población, almacén y edificios.
- **Edificio**: Edificio ampliable con nivel, coste, dependencias, población y duración.
- **Orden de construcción**: Ampliación activa con hora de finalización y estado de cola.
- **Aldea agrícola**: Aldea configurada con tipo de recurso, relación y disponibilidad de recogida.
- **Tarea programada**: Próxima acción de construcción o agricultura con objetivo, hora, estado y reintentos.
- **Estado persistente**: Registro recuperable de tareas, resultados y última observación segura.
- **Ejecución**: Resultado de una consulta o acción, con éxito, error, motivo y próxima ejecución.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En ejecución estable, al menos el 95% de las aldeas elegibles se procesa dentro de los 30 segundos posteriores a cada ciclo de 300 segundos.
- **SC-002**: En una ciudad con candidatos válidos, el bot inicia como máximo una ampliación por ciclo y nunca inicia una que incumpla requisitos, recursos o población.
- **SC-003**: Cuando existe una construcción activa, el 100% de los ciclos de decisión evita iniciar otra construcción.
- **SC-004**: Después de un reinicio, al menos el 99% de las tareas pendientes se restaura en menos de 60 segundos.
- **SC-005**: Durante una prueba de 24 horas, un fallo aislado de construcción no impide las ejecuciones agrícolas válidas, y viceversa.
- **SC-006**: En modo `DRY_RUN`, el 100% de las decisiones se registra sin enviar acciones modificadoras al juego.
- **SC-007**: Durante una prueba continua de 24 horas en Raspberry Pi Zero 2 W, el proceso no requiere navegador gráfico ni reinicio manual por consumo de recursos.
- **SC-008**: El 100% de los registros de tarea contiene objetivo, decisión, resultado, error si existe y próxima ejecución, sin secretos.

## Assumptions

- La primera versión administra una cuenta y un mundo configurados por ejecución.
- Las credenciales y parámetros del mundo existen fuera del código y nunca aparecen en registros.
- La opción `option: 1` representa la recogida de recursos de cinco minutos para la acción agrícola observada.
- El servidor sigue devolviendo datos reales de cola, edificios, recursos, producción, almacén y aldeas.
- El margen de construcción, el intervalo agrícola y el límite de reintentos son configurables.
- Una tarea atrasada se ejecuta una vez y vuelve a planificarse según el estado recibido.
- La persistencia local es suficiente; no se requiere sincronización entre dispositivos.
- El bot no gasta oro ni usa opciones premium en la primera versión.

## Out of Scope

- Saqueo, comercio o mejora de relación con aldeas.
- Tropas, ataques, investigación, cultura, héroes y múltiples cuentas.
- Panel web, aplicación móvil o control remoto.
- Automatización mediante Selenium, navegador o control visual durante la ejecución normal.
- Gasto de oro, reducción premium o acciones que no sean construcción y recogida de recursos de cinco minutos.
