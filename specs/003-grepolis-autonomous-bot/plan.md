# Implementation Plan: Bot autonomo de construcciones y aldeas

**Branch**: `feature/grepolis-desktop.0.1` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

## Summary

Implementar el bot en `src/` con una sesion HTTP reutilizable, lectura de Backbone, acciones explicitas de construccion y recogida, dos ciclos independientes y estado JSON recuperable. Windows y Linux usaran los mismos modulos Python; solo cambiaran comandos de activacion y rutas configurables.

## Technical Context

**Language/Version**: Python 3.11+.

**Primary Dependencies**: Dependencias HTTP ya adoptadas por el proyecto; biblioteca estandar para CLI, JSON, logging, reloj y persistencia.

**Storage**: Archivos JSON locales con escritura temporal y reemplazo atomico.

**Testing**: pytest; pruebas unitarias deterministas y contratos HTTP con respuestas simuladas.

**Target Platform**: Windows y Linux, incluida Raspberry Pi Zero 2 W.

**Project Type**: Servicio/CLI Python sin interfaz grafica.

**Performance Goals**: Un proceso continuo con bajo consumo; una consulta por ciclo y peticiones de accion solo cuando la decision sea valida.

**Constraints**: `DRY_RUN=true` por defecto; no guardar secretos; respetar CSRF y contratos observados; aislar ciclos; no usar Selenium; no gastar oro.

**Scale/Scope**: Una cuenta, un mundo, varias ciudades configurables y aldeas configuradas; una ampliacion por ciudad y ciclo.

## Constitution Check

La constitucion del repositorio contiene placeholders y no define gates ejecutables. Se aplican las restricciones del proyecto: Python, responsabilidades separadas, pytest, cobertura minima 0.80, `DRY_RUN` y pruebas desde `venv`.

**Gate result**: PASS with repository guidance applied.

## Research Summary

- Construccion observada: `POST /game/town_overviews?action=build_building` con payload JSON de edificio, ciudad, `tear_down`, `no_bar`, `build_for_gold` y `nl_init`.
- Recogida observada: `POST /game/frontend_bridge?action=execute` con `FarmTownPlayerRelation/<id>`, `action_name=claim`, `type=resources` y `option=1`.
- La cola, recursos, produccion, almacen, edificios y relaciones proceden del servidor y se consultan antes de decidir.
- CSRF se obtiene de la pagina actual y nunca se persiste.
- No se implementan saqueo, comercio, oro ni Selenium.

## Project Structure

```text
src/
├── config.py              # Variables de entorno y rutas portables
├── session.py             # Login, cookies, CSRF y reautenticacion
├── game_api.py            # Consultas y acciones HTTP
├── game_data.py           # Normalizacion de Backbone y entidades
├── buildings.py           # Candidatos y datos de edificios
├── construction.py        # Decision y planificacion de construccion
├── farm_towns.py          # Elegibilidad y recogida de aldeas
├── scheduler.py           # Tareas independientes y reintentos
├── state_store.py         # Persistencia JSON atomica
├── logging_config.py      # Logging sin secretos
└── main.py                # Orquestacion CLI

tests/
├── unit/
├── contract/
└── integration/
```

**Structure Decision**: `src/` sera la aplicacion solicitada. `tests/` separara logica pura, contratos HTTP y pruebas de integracion opcionales. Los modulos conservaran responsabilidades estrechas y no dependeran del sistema operativo.

## Phase 0: Research

1. Consolidar contratos observados en `contracts/observed-http.md`.
2. Confirmar reglas de prioridad, tiempos de servidor, `DRY_RUN` y aislamiento en `research.md`.
3. Resolver persistencia atomica, reloj inyectable y reintentos portables.

## Phase 1: Design

1. Definir entidades y transiciones en `data-model.md`.
2. Definir entradas/salidas HTTP y reglas de no repeticion en `contracts/observed-http.md`.
3. Definir comandos Windows/Linux y escenarios de validacion en `quickstart.md`.

## Implementation Order

1. Modelos, parsers y store JSON.
2. Cliente de sesion y consultas de solo lectura.
3. Motor de construccion y calculo de espera con capacidad de almacen.
4. Recogida de aldeas con `option=1`.
5. Acciones protegidas por `DRY_RUN`.
6. Scheduler independiente, reintentos y recuperacion.
7. CLI, logs, pruebas y validacion multiplataforma.

## Complexity Tracking

No hay violaciones constitucionales conocidas ni alternativas complejas justificadas.