from src.construction import plan_construction, select_building
from src.models import Building, BuildingOrder


def building(name, level, cost, *, dependencies=None, population=1, free=10, can=True):
    return Building(name, level, level + 1, can, True, cost, dependencies or [], None, True, population, free)


def test_selects_lowest_level_and_keeps_server_order_on_tie():
    candidates = [building("first", 4, {"wood": 1}), building("second", 4, {"wood": 1}), building("third", 3, {"wood": 1})]
    assert select_building(candidates, {"wood": 10, "stone": 10, "iron": 10}).building_id == "third"
    assert select_building(candidates[:2], {"wood": 10, "stone": 10, "iron": 10}).building_id == "first"


def test_skips_dependencies_and_unaffordable_candidate():
    candidates = [building("blocked", 1, {"wood": 100}, dependencies=["main"]), building("payable", 2, {"wood": 5})]
    plan = plan_construction(candidates, [], 100, 60, {"wood": 10, "stone": 0, "iron": 0}, {"wood": 60, "stone": 0, "iron": 0}, 1000)
    assert plan.action.building_id == "payable"


def test_active_order_blocks_new_construction():
    order = BuildingOrder(1, 3915, "academy", 200, 100, 100)
    plan = plan_construction([], [order], 100, 60, {}, {}, 1000)
    assert plan.action is None
    assert plan.reason == "active_queue"
    assert plan.next_run_at == 260
