from src.construction import resource_wait_seconds


def test_wait_respects_production_and_storage():
    wait = resource_wait_seconds({"wood": 0, "stone": 100, "iron": 100}, {"wood": 100}, {"wood": 60}, 1000)
    assert wait == 6000


def test_zero_production_or_cost_above_storage_is_unbuildable():
    assert resource_wait_seconds({"wood": 0}, {"wood": 10}, {"wood": 0}, 1000) is None
    assert resource_wait_seconds({"wood": 0}, {"wood": 1001}, {"wood": 3600}, 1000) is None
