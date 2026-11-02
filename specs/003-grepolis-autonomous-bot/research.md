# Research

## Decision: Reutilizar contratos HTTP observados

**Rationale**: Login, CSRF, Backbone, construccion y recogida ya fueron ejecutados y validados con respuestas reales. Evita inventar endpoints.

**Alternatives considered**: Selenium o navegador automatizado; descartado por requisito de ejecucion sin interfaz grafica.

## Decision: Dos ciclos independientes

**Rationale**: Construccion y aldeas tienen frecuencias, errores y proximas ejecuciones distintas. Una excepcion no debe cancelar el otro ciclo.

**Alternatives considered**: Un unico bucle secuencial; descartado porque un fallo o espera de construccion bloquearia aldeas.

## Decision: Persistencia JSON atomica

**Rationale**: Compatible con Windows, Linux y Raspberry Pi sin servicio adicional. Escribir a temporal y reemplazar evita dejar un estado parcialmente escrito.

**Alternatives considered**: Base de datos local; descartada para el MVP por complejidad y alcance.

## Decision: Reloj inyectable y tiempos del servidor

**Rationale**: Permite probar planificacion y reinicios deterministamente. `to_be_completed_at` y `lootable_at` mandan cuando existen.

**Alternatives considered**: Duraciones calculadas localmente; descartadas porque pueden divergir del servidor.

## Decision: DRY_RUN por defecto

**Rationale**: Evita mutaciones durante desarrollo y permite validar decisiones con datos reales.

**Alternatives considered**: Activar escritura por defecto; descartado por riesgo operativo.

## Unknowns resolved

- Construccion: `town_overviews`, accion `build_building`, JSON con `building_id`, `town_id`, `tear_down`, `no_bar`, `build_for_gold`, `nl_init`.
- Recogida: `frontend_bridge`, accion `execute`, `FarmTownPlayerRelation/<id>`, `claim`, `resources`, `option=1`.
- Cola: `BuildingOrders`; disponibilidad de aldea: `lootable_at` y `relation_status`.
- Plataforma: Python y biblioteca estandar permiten mismo codigo en Windows/Linux; rutas se generan con `pathlib`.

## Remaining risk

Los contratos de Grepolis pueden cambiar. El cliente debe validar claves y respuestas, registrar diagnostico seguro y fallar sin repetir acciones ambiguas.