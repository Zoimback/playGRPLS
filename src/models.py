from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ResourceMap = dict[str, float]
TaskKind = Literal["construction", "farm_collection"]
TaskStatus = Literal["pending", "running", "succeeded", "failed"]


@dataclass(frozen=True)
class Building:
    building_id: str
    level: int
    next_level: int | None
    can_upgrade: bool
    enough_resources: bool
    resources_for: ResourceMap = field(default_factory=dict)
    missing_dependencies: list[Any] = field(default_factory=list)
    building_time_seconds: int | None = None
    enough_storage: bool = True
    population_for: float = 0.0
    population_free: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BuildingOrder:
    order_id: int | str
    town_id: int
    building_type: str
    to_be_completed_at: int | None
    created_at: int | None = None
    building_time_seconds: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class QueuePlan:
    actions: tuple[Building, ...]
    reserved_resources: ResourceMap = field(default_factory=dict)
    reason: str = "ready"


@dataclass(frozen=True)
class FarmTown:
    farm_town_id: int
    name: str
    resource_offer: str | None = None
    resource_demand: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FarmTownRelation:
    farm_town_id: int
    player_id: int
    relation_status: int | str | None
    lootable_at: int | None
    last_looted_at: int | None
    loot: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BanditTarget:
    target_id: int
    level: int
    cooldown_duration: int | None
    cooldown_at: int | None
    reward_available: bool
    reward: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TownSnapshot:
    town_id: int
    resources: ResourceMap
    production_per_hour: ResourceMap
    storage_capacity: float
    population_free: float
    buildings: list[Building]
    building_orders: list[BuildingOrder] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScheduledTask:
    task_id: str
    kind: TaskKind
    target_id: int
    run_at: int
    status: TaskStatus = "pending"
    attempts: int = 0
    last_error: str | None = None
    last_confirmed_at: int | None = None
    phase: int = 0


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    message: str
    next_run_at: int | None = None
    confirmed_at: int | None = None
