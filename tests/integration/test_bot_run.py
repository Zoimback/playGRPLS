from src.main import Bot
from src.config import Settings
from src.scheduler import Scheduler
from src.state_store import StateStore


def test_bot_once_isolates_cycle_errors():
    class API:
        pass

    bot = Bot(API())
    result = bot.run_once(now=100)
    assert set(result) == {"construction", "farms"}
    assert result["construction"]["success"] is False
    assert result["farms"]["success"] is False


def test_scheduled_run_persists_independent_tasks(tmp_path, fake_clock):
    scheduler = Scheduler(StateStore(tmp_path / "state.json"), clock=fake_clock)
    configuration = Settings(town_ids=(1,), farm_town_ids=(), state_path=tmp_path / "state.json")
    bot = Bot(object(), configuration=configuration, scheduler=scheduler)

    result = bot.run_scheduled_once(fake_clock.value)

    assert set(result) == {"construction:1", "farms"}
    assert scheduler.tasks["construction:1"].status == "pending"
    assert scheduler.tasks["farms"].status == "pending"
