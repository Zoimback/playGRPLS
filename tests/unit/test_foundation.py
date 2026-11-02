from __future__ import annotations

from pathlib import Path

import pytest

from src.logging_config import redact
from src.models import ScheduledTask
from src.retry import RetryPolicy, is_transient_error
from src.scheduler import Scheduler
from src.state_store import StateStore


def test_redact_removes_secrets_and_csrf():
    value = redact({"password": "hidden", "url": "https://x.test?a=1&h=secret", "safe": 3})
    assert value == {"password": "[REDACTED]", "url": "https://x.test?a=1&h=[REDACTED]", "safe": 3}


def test_state_store_round_trip_and_atomic_path(tmp_path: Path):
    store = StateStore(tmp_path / "state.json")
    store.save({"tasks": {"farm:1": {"run_at": 10}}})
    assert store.load()["tasks"]["farm:1"]["run_at"] == 10
    assert not list(tmp_path.glob("*.tmp"))


def test_state_store_rejects_corrupt_state(tmp_path: Path):
    path = tmp_path / "state.json"
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(ValueError):
        StateStore(path).load()


def test_retry_policy_blocks_ambiguous_mutation():
    policy = RetryPolicy(limit=2, base_delay_seconds=5)
    assert policy.delay(2) == 20
    assert policy.can_retry(0)
    assert not policy.can_retry(0, ambiguous_mutation=True)
    assert is_transient_error(TimeoutError())


def test_scheduler_persists_and_restores_tasks(tmp_path: Path, fake_clock):
    store = StateStore(tmp_path / "state.json")
    scheduler = Scheduler(store, clock=fake_clock)
    scheduler.schedule(ScheduledTask("farm:1", "farm_collection", 1, fake_clock.value))
    assert [task.task_id for task in scheduler.due()] == ["farm:1"]
    scheduler.complete("farm:1", next_run_at=fake_clock.value + 300)
    restored = Scheduler(store, clock=fake_clock)
    assert restored.tasks["farm:1"].status == "pending"
    assert restored.tasks["farm:1"].run_at == fake_clock.value + 300


def test_scheduler_isolates_failed_task(tmp_path: Path, fake_clock):
    store = StateStore(tmp_path / "state.json")
    scheduler = Scheduler(store, clock=fake_clock)
    scheduler.schedule(ScheduledTask("construction:1", "construction", 1, fake_clock.value))
    scheduler.schedule(ScheduledTask("farm:1", "farm_collection", 1, fake_clock.value))
    scheduler.fail("construction:1", "network", next_run_at=fake_clock.value + 30)
    assert scheduler.tasks["farm:1"].status == "pending"

    def test_farm_task_phase_alternates_and_persists(tmp_path, fake_clock):
        store = StateStore(tmp_path / "state.json")
        scheduler = Scheduler(store, clock=fake_clock)
        scheduler.schedule(ScheduledTask("farms", "farm_collection", 0, fake_clock.value))
        scheduler.complete("farms", next_run_at=fake_clock.value + 1200)
        restored = Scheduler(store, clock=fake_clock)
        assert restored.tasks["farms"].phase == 1
        assert restored.tasks["farms"].run_at == fake_clock.value + 1200
