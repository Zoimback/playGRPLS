from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .game_data import extract_farm_relations, extract_farm_towns
from .models import FarmTown, FarmTownRelation


@dataclass(frozen=True)
class FarmTownStatus:
    farm_town: FarmTown
    relation: FarmTownRelation | None
    eligible: bool
    reason: str


@dataclass(frozen=True)
class FarmCycleResult:
    next_run_at: int
    successful: list[int]
    failed: list[int]


def _active(value: Any) -> bool:
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


def evaluate_farm_towns(response: dict[str, Any], configured_ids: set[int], now: int, player_id: int) -> list[FarmTownStatus]:
    relations = {relation.farm_town_id: relation for relation in extract_farm_relations(response, player_id)}
    statuses = []
    for farm_town in extract_farm_towns(response):
        if farm_town.farm_town_id not in configured_ids:
            continue
        relation = relations.get(farm_town.farm_town_id)
        if relation is None:
            statuses.append(FarmTownStatus(farm_town, None, False, "missing_relation"))
        elif not _active(relation.relation_status):
            statuses.append(FarmTownStatus(farm_town, relation, False, "inactive_relation"))
        elif relation.lootable_at is None:
            statuses.append(FarmTownStatus(farm_town, relation, False, "lootable_at_missing"))
        elif relation.lootable_at > now:
            statuses.append(FarmTownStatus(farm_town, relation, False, "lootable_at_in_future"))
        else:
            statuses.append(FarmTownStatus(farm_town, relation, True, "eligible"))
    return statuses


def run_farm_cycle(api: Any, configured_ids: set[int], now: int, collect: Callable[[int], Any], interval_seconds: int = 300, player_id: int = 0) -> FarmCycleResult:
    if interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    statuses = evaluate_farm_towns(api.get_farm_town_data(), configured_ids, now, player_id)
    successful, failed = [], []
    for status in statuses:
        if not status.eligible:
            continue
        try:
            collect(status.farm_town.farm_town_id)
        except (RuntimeError, ValueError, OSError):
            failed.append(status.farm_town.farm_town_id)
        else:
            successful.append(status.farm_town.farm_town_id)
    return FarmCycleResult(now + interval_seconds, successful, failed)
