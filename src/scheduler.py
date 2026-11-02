from __future__ import annotations

import time
from dataclasses import asdict
from typing import Callable

from .models import ScheduledTask
from .state_store import StateStore


class Scheduler:
    def __init__(self, store: StateStore, clock: Callable[[], int] | None = None) -> None:
        self.store = store
        self.clock = clock or (lambda: int(time.time()))
        self.tasks: dict[str, ScheduledTask] = {}
        self.restore()

    def restore(self) -> None:
        raw_tasks = self.store.load().get("tasks", {})
        self.tasks = {task_id: ScheduledTask(**data) for task_id, data in raw_tasks.items()}

    def schedule(self, task: ScheduledTask) -> None:
        self.tasks[task.task_id] = task
        self.persist()

    def due(self) -> list[ScheduledTask]:
        now = self.clock()
        return [task for task in self.tasks.values() if task.status == "pending" and task.run_at <= now]

    def next_run_at(self) -> int | None:
        pending = [task.run_at for task in self.tasks.values() if task.status == "pending"]
        return min(pending) if pending else None

    def start(self, task_id: str) -> ScheduledTask:
        task = self.tasks[task_id]
        if task.status != "pending":
            raise ValueError(f"Task is not pending: {task_id}")
        task.status = "running"
        self.persist()
        return task

    def complete(self, task_id: str, next_run_at: int | None = None) -> None:
        task = self.tasks[task_id]
        task.status = "succeeded"
        task.last_confirmed_at = self.clock()
        if task.kind == "farm_collection":
            task.phase = 1 - task.phase
        if next_run_at is not None:
            task.run_at = next_run_at
            task.status = "pending"
        self.persist()

    def fail(self, task_id: str, error: str, next_run_at: int | None = None) -> None:
        task = self.tasks[task_id]
        task.status = "failed"
        task.attempts += 1
        task.last_error = error
        if next_run_at is not None:
            task.run_at = next_run_at
            task.status = "pending"
        self.persist()

    def persist(self) -> None:
        self.store.save({"tasks": {task_id: asdict(task) for task_id, task in self.tasks.items()}})
