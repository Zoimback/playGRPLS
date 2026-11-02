from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from .models import Building, BuildingOrder


@dataclass(frozen=True)
class ConstructionPlan:
    action: Building | None
    next_run_at: int
    reason: str
    expected_finish_at: int | None = None


def _affordable(building: Building, current: dict[str, float]) -> bool:
    return all(float(current.get(resource, 0)) >= cost for resource, cost in building.resources_for.items())


def _eligible(building: Building) -> bool:
    return building.can_upgrade and not building.missing_dependencies and building.enough_storage and building.population_free >= building.population_for


def select_building(buildings: Iterable[Building], current: dict[str, float]) -> Building | None:
    for building in sorted(enumerate(buildings), key=lambda item: (item[1].level, item[0])):
        candidate = building[1]
        if _eligible(candidate) and _affordable(candidate, current):
            return candidate
    return None


def resource_wait_seconds(current: dict[str, float], required: dict[str, float], production_per_hour: dict[str, float], storage_capacity: float) -> int | None:
    waits = []
    for resource, amount in required.items():
        if amount > storage_capacity:
            return None
        deficit = amount - float(current.get(resource, 0))
        if deficit <= 0:
            continue
        hourly = float(production_per_hour.get(resource, 0))
        if hourly <= 0:
            return None
        waits.append(math.ceil(deficit * 3600 / hourly))
    return max(waits, default=0)


def plan_construction(buildings: Iterable[Building], orders: Iterable[BuildingOrder], now: int, margin_seconds: int, current: dict[str, float], production_per_hour: dict[str, float], storage_capacity: float) -> ConstructionPlan:
    if margin_seconds < 0:
        raise ValueError("margin_seconds cannot be negative")
    active = [order for order in orders if order.to_be_completed_at is not None]
    if active:
        finish = min(order.to_be_completed_at for order in active if order.to_be_completed_at is not None)
        return ConstructionPlan(None, max(now, finish + margin_seconds), "active_queue", finish)
    ordered = [building for _, building in sorted(enumerate(buildings), key=lambda item: (item[1].level, item[0])) if _eligible(building)]
    selected = select_building(ordered, current)
    if selected is not None:
        return ConstructionPlan(selected, now, "ready")
    waits = [(resource_wait_seconds(current, building.resources_for, production_per_hour, storage_capacity), building) for building in ordered]
    possible = [(wait, building) for wait, building in waits if wait is not None]
    if possible:
        wait, _ = min(possible, key=lambda item: (item[0], ordered.index(item[1])))
        return ConstructionPlan(None, now + wait, "resources")
    return ConstructionPlan(None, now + max(margin_seconds, 1), "blocked")
