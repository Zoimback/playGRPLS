from src.models import ScheduledTask
from src.scheduler import Scheduler
from src.state_store import StateStore


def test_restart_restores_pending_task_without_repeating_confirmed_action(tmp_path, fake_clock):
    store = StateStore(tmp_path / "state.json")
    first = Scheduler(store, clock=fake_clock)
    first.schedule(ScheduledTask("farm:1", "farm_collection", 1, fake_clock.value))
    first.complete("farm:1", next_run_at=fake_clock.value + 300)
    second = Scheduler(store, clock=fake_clock)
    assert second.tasks["farm:1"].status == "pending"
    assert second.tasks["farm:1"].run_at == fake_clock.value + 300
