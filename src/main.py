from __future__ import annotations

import argparse
import logging
import signal
import time
from dataclasses import replace
from typing import Any

from .config import settings
from .construction import plan_construction
from .farm_towns import evaluate_farm_towns
from .game_api import AmbiguousMutationError, GameAPI
from .logging_config import configure_logging, logger
from .models import ScheduledTask
from .platform_scheduler import install as install_platform_scheduler
from .platform_scheduler import schedule_at
from .platform_scheduler import uninstall as uninstall_platform_scheduler
from .scheduler import Scheduler
from .session import GrepolisSession
from .state_store import StateStore


class Bot:
    def __init__(self, api: Any, configuration=settings, scheduler: Scheduler | None = None) -> None:
        self.api = api
        self.settings = configuration
        self.scheduler = scheduler

    def run_once(self, now: int | None = None) -> dict[str, dict[str, Any]]:
        timestamp = int(time.time()) if now is None else now
        logger.debug("Starting manual cycle at %s", timestamp)
        result: dict[str, dict[str, Any]] = {}
        try:
            result["construction"] = self.run_construction(timestamp)
        except Exception as exc:  # boundary isolates one independent cycle
            logger.exception("Construction cycle failed")
            result["construction"] = {"success": False, "error": str(exc)}
        try:
            result["farms"] = self.run_farms(timestamp)
        except Exception as exc:  # boundary isolates one independent cycle
            logger.exception("Farm cycle failed")
            result["farms"] = {"success": False, "error": str(exc)}
        return result

    def ensure_tasks(self, now: int) -> None:
        if self.scheduler is None:
            return
        for town_id in self.settings.town_ids:
            task_id = f"construction:{town_id}"
            if task_id not in self.scheduler.tasks:
                self.scheduler.schedule(ScheduledTask(task_id, "construction", town_id, now))
        farm_id = "farms"
        if farm_id not in self.scheduler.tasks:
            self.scheduler.schedule(ScheduledTask(farm_id, "farm_collection", 0, now))

    def run_scheduled_once(self, now: int) -> dict[str, dict[str, Any]]:
        if self.scheduler is None:
            return self.run_once(now)
        self.ensure_tasks(now)
        results: dict[str, dict[str, Any]] = {}
        due_tasks = list(self.scheduler.due())
        logger.debug("Scheduler checked at %s; due tasks: %s", now, [task.task_id for task in due_tasks])
        for task in due_tasks:
            logger.info("Starting task %s", task.task_id)
            self.scheduler.start(task.task_id)
            try:
                result = self.run_construction(now) if task.kind == "construction" else self.run_farms(now)
                next_run = result.get("next_run_at", now + self.settings.farm_interval_seconds)
                self.scheduler.complete(task.task_id, int(next_run))
            except AmbiguousMutationError as exc:
                if self.reconcile(task, now):
                    result = {"success": True, "reconciled": True}
                    self.scheduler.complete(task.task_id, now + self.settings.construction_margin_seconds)
                else:
                    result = {"success": False, "ambiguous": True, "error": str(exc)}
                    self.scheduler.fail(task.task_id, str(exc), now + self.settings.construction_margin_seconds)
            except Exception as exc:
                logger.exception("Scheduled task failed: %s", task.task_id)
                result = {"success": False, "error": str(exc)}
                self.scheduler.fail(task.task_id, str(exc), now + 30)
            results[task.task_id] = result
        return results

    def reconcile(self, task: ScheduledTask, now: int) -> bool:
        if task.kind == "construction":
            return any(order.to_be_completed_at is not None for order in self.api.get_building_orders())
        return any(relation.lootable_at is not None and relation.lootable_at > now for relation in self.api.get_farm_relations())

    def run_construction(self, now: int) -> dict[str, Any]:
        snapshot = self.api.get_town_snapshot()
        logger.debug("Construction state: town=%s buildings=%s orders=%s", snapshot.town_id, len(snapshot.buildings), len(snapshot.building_orders))
        plan = plan_construction(snapshot.buildings, snapshot.building_orders, now, self.settings.construction_margin_seconds, snapshot.resources, snapshot.production_per_hour, snapshot.storage_capacity)
        logger.info("Construction decision: reason=%s next_run_at=%s building=%s", plan.reason, plan.next_run_at, plan.action.building_id if plan.action else None)
        if plan.action is None:
            return {"success": True, "reason": plan.reason, "next_run_at": plan.next_run_at}
        response = self.api.build_building(plan.action.building_id, snapshot.town_id)
        return {"success": True, "reason": plan.reason, "building_id": plan.action.building_id, "response": response, "next_run_at": now + int(response.get("next_fetch_in", self.settings.construction_margin_seconds))}

    def run_farms(self, now: int) -> dict[str, Any]:
        response = self.api.get_farm_town_data()
        configured_ids = set(self.settings.farm_town_ids)
        if not configured_ids:
            logger.warning("No farm towns configured; set GREEPOLIS_FARM_TOWN_IDS")
        statuses = evaluate_farm_towns(response, configured_ids, now, self.settings.player_id)
        logger.info("Farm state: configured=%s eligible=%s unavailable=%s", sorted(configured_ids), [status.farm_town.farm_town_id for status in statuses if status.eligible], [f"{status.farm_town.farm_town_id}:{status.reason}" for status in statuses if not status.eligible])
        successful, failed = [], []
        relations = {item.farm_town_id: item for item in self.api.get_farm_relations()}
        for status in statuses:
            if not status.eligible:
                continue
            relation = relations.get(status.farm_town.farm_town_id)
            try:
                relation_id = int(relation.raw["id"])
                self.api.collect_farm_town(relation_id, status.farm_town.farm_town_id, self.settings.town_ids[0])
                successful.append(status.farm_town.farm_town_id)
            except (KeyError, RuntimeError, ValueError, OSError):
                logger.exception("Farm collection failed for %s", status.farm_town.farm_town_id)
                failed.append(status.farm_town.farm_town_id)
        return {"success": True, "configured": sorted(configured_ids), "successful": successful, "failed": failed, "next_run_at": now + self.settings.farm_interval_seconds}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Grepolis bot in safe dry-run mode by default.")
    parser.add_argument("--once", action="store_true", help="run both independent cycles once")
    parser.add_argument("--dry-run", action="store_true", help="force dry-run mode")
    parser.add_argument("--logs", action="store_true", help="show detailed execution logs")
    parser.add_argument("--install-scheduler", action="store_true", help="install a one-shot system trigger every minute")
    parser.add_argument("--uninstall-scheduler", action="store_true", help="remove the system trigger")
    args = parser.parse_args()
    configure_logging(logging.DEBUG if args.logs else logging.INFO)
    if args.install_scheduler:
        logger.info(install_platform_scheduler())
        return 0
    if args.uninstall_scheduler:
        logger.info(uninstall_platform_scheduler())
        return 0
    configuration = replace(settings, dry_run=True) if args.dry_run else settings
    if configuration.dry_run:
        logger.info("DRY_RUN enabled")
    session = GrepolisSession(configuration)
    stop = False

    def request_stop(_signum, _frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, request_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, request_stop)
    try:
        session.login()
        scheduler = Scheduler(StateStore(configuration.resolved_state_path()))
        bot = Bot(GameAPI(session, configuration), configuration=configuration, scheduler=scheduler)
        if args.once:
            logger.info("Cycle result: %s", bot.run_once(int(time.time())))
            return 0
        result = bot.run_scheduled_once(int(time.time()))
        next_run = scheduler.next_run_at()
        if next_run is not None:
            logger.info("Next scheduled execution: %s", next_run)
            schedule_at(next_run)
        logger.info("Scheduled cycle result: %s", result)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
