# Implementation Plan: Poblacion, cola y batallas contra bandidos

**Branch**: `feature/grepolis-desktop.0.1` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

## Summary

Extender el bot actual para priorizar granja con poblacion cero, planificar hasta dos construcciones con costes acumulados y añadir una capa de investigacion/decision para bandidos. La batalla permanecera bloqueada hasta confirmar simulador, tropas enemigas, envio, llegada, resultado y recompensa.

## Technical Context

**Language/Version**: Python 3.11+.

**Primary Dependencies**: Dependencias existentes del bot; biblioteca estandar para modelos, persistencia, logging y reloj.

**Storage**: Estado JSON atomico existente, ampliado con cola planificada, movimientos y recompensas.

**Testing**: pytest y pytest-cov; contratos HTTP simulados, decisiones puras e integracion sin red.

**Target Platform**: Windows y Linux, incluida Raspberry Pi Zero 2 W.

**Project Type**: Servicio/CLI one-shot ejecutado por Task Scheduler, `at` o invocacion manual.

**Performance Goals**: Una lectura de estado por decision; no repetir peticiones ni acciones ambiguas.

**Constraints**: `DRY_RUN=true` por defecto; no gastar oro; no enviar tropas sin simulacion segura; usar `cooldown_at` y `cooldown_duration` del servidor, nunca constantes.

**Scale/Scope**: Una cuenta, un mundo, varias ciudades y objetivos de bandidos configurados.

## Constitution Check

La constitucion contiene placeholders y no define gates ejecutables. Se aplican las reglas del repositorio: Python, responsabilidades separadas, pytest, cobertura minima 0.80, estado seguro y sin secretos.

**Gate result**: PASS with repository guidance applied.

## Research Summary

- `Units` observo 62 espadas y cero en otras unidades de combate de la captura.
- `PlayerAttackSpot` observo nivel 19, `town_id=3856`, recompensa de 5 jinetes, recompensa disponible y `units=[]`.
- `cooldown_duration=300` fue solo una observacion; el servidor manda cada valor.
- No se confirmaron payloads de simulador, envio de tropas, resultado ni recompensa. La implementacion debe mantener esas acciones bloqueadas hasta disponer de contratos.

## Project Structure

```text
src/
├── game_data.py          # Poblacion, cola, unidades, objetivos y movimientos
├── construction.py       # Prioridad de granja y planificacion de dos espacios
├── battle_data.py        # Normalizacion de objetivos, tropas y recompensas
├── battle_engine.py      # Estrategias, umbral de seguridad y no-envio
├── game_api.py           # Lecturas y contratos de acciones confirmados
├── scheduler.py          # Proximas ejecuciones por timestamps del servidor
├── state_store.py        # Persistencia de cola y batalla
└── main.py               # Ciclos independientes one-shot

tests/
├── unit/
├── contract/
└── integration/
```

**Structure Decision**: Extender `src` sin duplicar la sesion HTTP ni el scheduler. Separar batalla de construccion para impedir que una decision militar modifique la cola o viceversa.

## Phase 0: Research

1. Capturar con DevTools los contratos pendientes cuando MCP y sesion autenticada esten disponibles.
2. Confirmar que `cooldown_at` y `cooldown_duration` se leen por objetivo.
3. Documentar simulador, fuerza enemiga, envio, llegada, resultado y recompensa.
4. No activar mutaciones militares hasta cerrar todos los contratos.

## Phase 1: Design

1. Ampliar entidades de poblacion, cola y tropas en `data-model.md`.
2. Definir estrategia segura y estados de batalla en `contracts/observed-http.md`.
3. Diseñar tareas de cola, movimiento y recompensa con deduplicacion.

## Implementation Order

1. Añadir poblacion cero y capacidad de cola dos a decisiones de construccion.
2. Añadir tests de costes acumulados y no sobrepasar cola.
3. Añadir lectura de unidades y objetivos sin acciones.
4. Implementar simulacion pura con resultado seguro/insuficiente.
5. Añadir contratos de envio solo tras captura real.
6. Añadir seguimiento de llegada, resultado y recompensa.
7. Integrar persistencia one-shot y validacion Windows/Linux.

## Safety Gates

- No enviar tropas si no existe fuerza enemiga verificable.
- No enviar tropas si simulador falla, empata o devuelve datos incompletos.
- No recoger recompensa sin estado confirmado.
- No repetir una accion ambigua sin reconciliar movimientos o recompensas.
- No fijar cooldowns: usar valores server-side.

## Complexity Tracking

No se introduce complejidad militar activa hasta disponer de contratos observados. La simulacion se mantendra como funcion pura y testeable.