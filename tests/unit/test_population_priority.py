from src.construction import plan_construction
from src.models import Building


def make_building(name, level, cost, population=1, free=10, can_upgrade=True):
    return Building(name, level, level + 1, can_upgrade, True, cost, [], None, True, population, free)


def test_zero_population_prioritizes_valid_farm():
    buildings = [
        make_building("main", 1, {"wood": 1}),
        make_building("farm", 3, {"wood": 1}),
    ]
    plan = plan_construction(
        buildings, [], 100, 60,
        {"wood": 10, "stone": 10, "iron": 10},
        {"wood": 60, "stone": 60, "iron": 60},
        1000,
        population_zero=True,
    )
    assert plan.action is not None
    assert plan.action.building_id == "farm"


def test_zero_population_does_not_choose_blocked_farm():
    buildings = [make_building("farm", 1, {"wood": 1}, can_upgrade=False)]
    plan = plan_construction(
        buildings, [], 100, 60,
        {"wood": 10}, {"wood": 60}, 1000,
        population_zero=True,
    )
    assert plan.action is None
    assert plan.reason == "blocked"
