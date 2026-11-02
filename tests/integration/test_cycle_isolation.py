from src.models import ScheduledTask
from src.scheduler import Scheduler
from src.state_store import StateStore


def test_failed_construction_does_not_stop_farm_task(tmp_path, fake_clock):
    scheduler = Scheduler(StateStore(tmp_path / "state.json"), clock=fake_clock)
    scheduler.schedule(ScheduledTask("construction:1", "construction", 1, fake_clock.value))
    scheduler.schedule(ScheduledTask("farm:1", "farm_collection", 1, fake_clock.value))
    scheduler.fail("construction:1", "network", next_run_at=fake_clock.value + 30)
    assert scheduler.tasks["farm:1"].status == "pending"
