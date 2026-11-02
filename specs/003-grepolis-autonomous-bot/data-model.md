# Data Model

## Configuracion

- `world`: mundo objetivo.
- `town_ids`: ciudades administradas.
- `farm_town_ids`: aldeas configuradas.
- `farm_interval_seconds`: 300 por defecto.
- `construction_margin_seconds`: margen despues de finalizacion.
- `retry_limit`: limite de reintentos.
- `dry_run`: `true` por defecto.
- `state_path`: ruta JSON configurable.

## Ciudad

- `town_id`: identificador positivo.
- `resources`: madera, piedra y hierro disponibles.
- `production_per_hour`: produccion por recurso.
- `storage_capacity`: capacidad maxima.
- `population_free`: poblacion libre.
- `buildings`: edificios en orden recibido.
- `building_orders`: cola activa.

## Edificio

- `building_id`: identificador del edificio.
- `level`: nivel actual.
- `next_level`: siguiente nivel.
- `can_upgrade`: permiso del servidor.
- `missing_dependencies`: dependencias pendientes.
- `enough_resources`: disponibilidad indicada por servidor.
- `enough_storage`: capacidad suficiente.
- `resources_for`: coste por recurso.
- `population_for`: poblacion requerida.
- `population_free`: poblacion libre para ese edificio.
- `building_time`: duracion informativa.

## Orden de construccion

- `order_id`.
- `town_id`.
- `building_type`.
- `created_at`.
- `to_be_completed_at`.
- `building_time_seconds`.
- `status`: `active`, `confirmed`, `failed`.

Transition: `active` bloquea nuevas construcciones; `confirmed` permite planificar tras refrescar cola; `failed` se reintenta solo si la accion fue segura.

## Relacion de aldea

- `farm_town_id`.
- `player_id`.
- `relation_status`.
- `lootable_at`.
- `last_looted_at`.
- `loot`.
- `resource_offer` y `resource_demand`.

A village is eligible only when relation is active and `lootable_at <= server_now`.

## Tarea programada

- `task_id` estable.
- `kind`: `construction` or `farm_collection`.
- `target_id`.
- `run_at`.
- `status`: `pending`, `running`, `succeeded`, `failed`.
- `attempts`.
- `last_error`.
- `last_confirmed_at`.

## Persistencia

Store only non-secret state. Never persist password, cookies, CSRF, authorization headers or raw request files. Write versioned JSON atomically.
