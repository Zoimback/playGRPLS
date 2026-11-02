# Investigacion Grepolis

Estas herramientas son de solo lectura. Sirven para descubrir el contrato real de Grepolis antes de implementar acciones que construyan edificios o recojan aldeas.

## Uso

Desde la raiz del repositorio y con el entorno virtual activado:

```powershell
python investigacion/01_capturar_backbone.py --output investigacion/data/backbone.json
python investigacion/02_inventariar_backbone.py investigacion/data/backbone.json --output investigacion/data/inventory.json
python investigacion/03_comparar_backbones.py investigacion/data/antes.json investigacion/data/despues.json
python -m pytest investigacion/test_research_tools.py -q
```

La captura usa el login existente y carga las variables de `noselenium/.env` a traves de `noselenium/config.py`; nunca se abre ni se imprime ese archivo. Los JSON escritos redactedan claves que puedan contener CSRF, cookies, contrasenas, tokens o autorizacion.

## Que investigar

1. Capturar dos Backbones separados por una accion manual controlada.
2. Inventariar modelos y campos antes de asumir que siempre hay 23 modelos.
3. Comparar snapshots para localizar cambios de recursos, poblacion, `BuildingOrders`, aldeas y relaciones del jugador.
4. Confirmar con varias ciudades y estados: cola vacia, cola ocupada, recursos insuficientes, dependencias pendientes y aldeas no saqueables.

## Contratos que deben quedar probados antes de actuar

- **Construccion:** `building_data`, `can_upgrade`, `next_level`, costes, poblacion, dependencias y `BuildingOrders`.
- **Recursos:** `resources`, `production` y capacidad de almacenamiento; son fotografias y deben consultarse de nuevo antes de decidir.
- **Aldeas:** modelos `FarmTowns` y `FarmTownPlayerRelations`, incluyendo `lootable_at`, `relation_status`, `loot` y `expansion_stage`.
- **Acciones futuras:** descubrir mediante comparacion la peticion, payload, identificador de ciudad/aldea, token y respuesta. No implementar POST de mutacion solo porque un campo aparezca en el Backbone.

## Artefactos

No se deben versionar capturas reales: pueden contener identificadores, estado de cuenta o tokens. La carpeta `investigacion/data/` esta ignorada por Git cuando se use para capturas locales. El fixture incluido es deliberadamente pequeno y no contiene datos de una cuenta.

## Hallazgos de captura real

- La respuesta tuvo 23 modelos y 30 colecciones.
- `BuildingBuildData` contiene 22 edificios. Cada edificio expone `level`, `next_level`, `can_upgrade`, `enough_resources`, `enough_storage`, `resources_for`, `population_for`, `population_free` y `missing_dependencies`.
- `BuildingOrders` contiene la cola activa. La captura observo una orden de `academy`, con `town_id`, `to_be_completed_at`, `created_at`, costes y `building_time`.
- Tras la mejora manual del aserradero, una consulta posterior devolvio dos ordenes: `academy` y `lumber`. La cola debe consultarse antes de cada decision.
- `FarmTowns` contiene seis aldeas. `FarmTownPlayerRelations` contiene seis relaciones del jugador, con `lootable_at`, `relation_status`, `loot`, `expansion_stage` y `lootcap_reset_at`.
- `Town` devolvio recursos, produccion, poblacion, almacenamiento y poblacion disponible.
- Dos capturas seguidas cambiaron recursos y relojes, pero no probaron acciones. Hace falta capturar antes y despues de una construccion o saqueo manual controlado para descubrir el POST de mutacion.
- El JavaScript oficial llama `BuildingOrder.buildUp` con `execute("buildUp", {building_id, town_id, build_for_gold})`. Esto define el comando logico, pero no confirma aun la URL HTTP ni la envoltura CSRF.
- La interfaz de aldeas contiene controles `claim_resources`, `btn_trade` y `btn_upgrade`. Sus payloads de red siguen sin confirmarse.

## Accion de construccion confirmada

La mejora manual del aserradero produjo esta peticion:

```text
POST https://es148.grepolis.com/game/town_overviews?town_id=3915&action=build_building&h=<CSRF>
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
```

El campo `json` enviado fue:

```json
{
	"building_id": "lumber",
	"town_id": 3915,
	"tear_down": 0,
	"no_bar": 0,
	"build_for_gold": false,
	"nl_init": true
}
```

La respuesta HTTP fue `200` y devolvio `success`, `building_data`, `available_population`, `is_building_order_queue_full`, `notifications` y `next_fetch_in`. El token CSRF debe obtenerse de la sesion actual y nunca guardarse como constante.

## Recogida de aldea confirmada

La recogida manual de recursos de la aldea `1562` produjo esta peticion:

```text
POST https://es148.grepolis.com/game/frontend_bridge?town_id=3915&action=execute&h=<CSRF>
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
```

El campo `json` enviado fue:

```json
{
	"model_url": "FarmTownPlayerRelation/22670",
	"action_name": "claim",
	"captcha": null,
	"arguments": {
		"farm_town_id": 1562,
		"type": "resources",
		"option": 1
	},
	"town_id": 3915,
	"nl_init": true
}
```

La respuesta HTTP fue `200` y devolvio `success`, `next_fetch_in` y `notifications`. En la prueba manual, `option: 1` fue la opcion de recogida de 5 minutos.

## Reglas candidatas para el bot

- **Construir:** refrescar ciudad y cola; no construir si existe una orden con `to_be_completed_at`; elegir solo edificios con `can_upgrade`, sin `missing_dependencies`, con `enough_resources`, `enough_storage` y poblacion suficiente.
- **Esperar recursos:** calcular tiempo con `resources`, `resources_for` y `production`. Volver a consultar antes de enviar cualquier accion.
- **Recolectar:** refrescar relaciones; actuar solo con `relation_status > 0` y `lootable_at <= ahora`. Tratar `relation_status = 0` o `lootable_at = null` como no elegible.
- **No mutar todavía:** el Backbone demuestra estado, no contrato de escritura. Falta observar URL, `action`, payload, respuesta y efecto posterior de una accion manual.

## Siguiente experimento controlado

1. Activar DevTools Network en una cuenta de prueba.
2. Capturar una mejora manual de edificio y una recoleccion manual de aldea.
3. Guardar solo metodo, URL sin token, nombres de campos, tipos de respuesta y cambios de Backbone.
4. Repetir con `DRY_RUN=true` hasta validar idempotencia, errores y expiracion de CSRF.

Los activos descargados quedan en `investigacion/data/assets/`, ignorados por Git. Pueden contener estado de sesion; no compartirlos.