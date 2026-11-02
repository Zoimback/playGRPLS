from src.logging_config import redact
from src.main import Bot
from src.models import BuildingOrder, FarmTownRelation, ScheduledTask
from src.retry import RetryPolicy


def test_dry_run_and_redaction_contract():
    assert redact({"csrf": "abc", "cookie": "def", "url": "https://x?h=abc"}) == {"csrf": "[REDACTED]", "cookie": "[REDACTED]", "url": "https://x?h=[REDACTED]"}
    assert not RetryPolicy(limit=2).can_retry(0, ambiguous_mutation=True)


def test_retry_limit_is_bounded():
    policy = RetryPolicy(limit=2)
    assert policy.can_retry(0)
    assert policy.can_retry(1)
    assert not policy.can_retry(2)


def test_ambiguous_construction_reconciles_from_server_queue():
    class API:
        def get_building_orders(self):
            return [BuildingOrder(1, 3915, "lumber", 200)]

    bot = Bot(API())
    assert bot.reconcile(ScheduledTask("construction:3915", "construction", 3915, 100), 100)


def test_ambiguous_farm_reconciles_from_server_cooldown():
    class API:
        def get_farm_relations(self):
            return [FarmTownRelation(1562, 9, 1, 400, 100)]

    bot = Bot(API())
    assert bot.reconcile(ScheduledTask("farms", "farm_collection", 0, 100), 100)
