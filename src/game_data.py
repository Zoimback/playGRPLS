from __future__ import annotations

import math
from typing import Any

from .models import Building, BuildingOrder, FarmTown, FarmTownRelation, TownSnapshot

RESOURCES = ("wood", "stone", "iron")


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _duration(value: Any) -> int | None:
    if isinstance(value, (int, float)) and value >= 0:
        return int(value)
    if not isinstance(value, str):
        return None
    parts = value.split(":")
    if len(parts) != 3:
        return None
    try:
        hours, minutes, seconds = (int(part) for part in parts)
    except ValueError:
        return None
    if minutes >= 60 or seconds >= 60 or min(hours, minutes, seconds) < 0:
        return None
    return hours * 3600 + minutes * 60 + seconds


def _backbone(response: dict[str, Any]) -> dict[str, Any]:
    value = response.get("backbone", response)
    if not isinstance(value, dict):
        raise ValueError("backbone must be an object")
    return value


def _entries(response: dict[str, Any]):
    backbone = _backbone(response)
    for section in ("models", "collections"):
        values = backbone.get(section, [])
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, dict):
                yield item


def _records(response: dict[str, Any], class_name: str):
    wanted = class_name.casefold()
    for entry in _entries(response):
        name = str(entry.get("model_class_name", entry.get("class_name", ""))).casefold()
        if name != wanted:
            continue
        data = entry.get("data", [])
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            continue
        for item in data:
            if isinstance(item, dict):
                record = item.get("d", item)
                if isinstance(record, dict):
                    yield record


def _resource_map(value: Any) -> dict[str, float]:
    source = value if isinstance(value, dict) else {}
    return {resource: _number(source.get(resource)) for resource in RESOURCES}


def parse_town_snapshot(response: dict[str, Any]) -> TownSnapshot:
    town = next(iter(_records(response, "Town")), None)
    build_data = next(iter(_records(response, "BuildingBuildData")), None)
    if town is None or build_data is None:
        raise ValueError("Town and BuildingBuildData are required")
    building_data = build_data.get("building_data")
    if not isinstance(building_data, dict):
        raise ValueError("building_data must be an object")
    buildings = []
    for building_id, raw in building_data.items():
        if not isinstance(raw, dict):
            continue
        buildings.append(Building(
            building_id=str(building_id),
            level=int(_number(raw.get("level"))),
            next_level=_int(raw.get("next_level")),
            can_upgrade=bool(raw.get("can_upgrade", False)),
            enough_resources=bool(raw.get("enough_resources", False)),
            resources_for=_resource_map(raw.get("resources_for")),
            missing_dependencies=list(raw.get("missing_dependencies", [])),
            building_time_seconds=_duration(raw.get("building_time")),
            enough_storage=bool(raw.get("enough_storage", True)),
            population_for=_number(raw.get("population_for")),
            population_free=_number(raw.get("population_free", town.get("available_population"))),
            raw=raw,
        ))
    return TownSnapshot(
        town_id=int(_number(town.get("id"))),
        resources=_resource_map(town.get("resources")),
        production_per_hour=_resource_map(town.get("production")),
        storage_capacity=_number(town.get("storage")),
        population_free=_number(town.get("available_population")),
        buildings=buildings,
        building_orders=extract_building_orders(response, int(_number(town.get("id")))),
        raw=response,
    )


def extract_building_orders(response: dict[str, Any], town_id: int) -> list[BuildingOrder]:
    orders = []
    for raw in _records(response, "BuildingOrders"):
        if _int(raw.get("town_id")) != town_id:
            continue
        orders.append(BuildingOrder(
            order_id=raw.get("id", ""),
            town_id=town_id,
            building_type=str(raw.get("building_type", "")),
            to_be_completed_at=_int(raw.get("to_be_completed_at")),
            created_at=_int(raw.get("created_at")),
            building_time_seconds=_duration(raw.get("building_time")),
            raw=raw,
        ))
    return orders


def extract_farm_towns(response: dict[str, Any]) -> list[FarmTown]:
    return [FarmTown(int(_number(raw.get("id"))), str(raw.get("name", "")), raw.get("resource_offer"), raw.get("resource_demand"), raw) for raw in _records(response, "FarmTowns") if _int(raw.get("id")) is not None]


def extract_farm_relations(response: dict[str, Any], player_id: int) -> list[FarmTownRelation]:
    relations = []
    for raw in _records(response, "FarmTownPlayerRelations"):
        if _int(raw.get("player_id")) != player_id or _int(raw.get("farm_town_id")) is None:
            continue
        relations.append(FarmTownRelation(int(raw["farm_town_id"]), player_id, raw.get("relation_status"), _int(raw.get("lootable_at")), _int(raw.get("last_looted_at")), _number(raw.get("loot")), raw))
    return relations
