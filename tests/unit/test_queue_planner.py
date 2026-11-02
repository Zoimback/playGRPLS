from src.construction import plan_queue
from src.models import Building, BuildingOrder


def building(name, level, wood):
    return Building(name, level, level + 1, True, True, {"wood": wood}, [], None, True, 1, 10)


def test_queue_plans_two_orders_with_accumulated_resources():
    result = plan_queue(
        [building("main", 1, 6), building("farm", 2, 5), building("storage", 3, 5)],
        [], {"wood": 11, "stone": 0, "iron": 0}, queue_capacity=2,
    )
    assert [item.building_id for item in result.actions] == ["main", "farm"]
    assert result.reserved_resources["wood"] == 11


def test_queue_keeps_one_free_slot_when_first_order_active():
    order = BuildingOrder(1, 1, "main", 200)
    result = plan_queue([building("farm", 1, 5), building("storage", 2, 5)], [order], {"wood": 10}, queue_capacity=2)
    assert [item.building_id for item in result.actions] == ["farm"]


def test_queue_never_exceeds_capacity():
    orders = [BuildingOrder(1, 1, "main", 200), BuildingOrder(2, 1, "farm", 300)]
    result = plan_queue([building("storage", 1, 1)], orders, {"wood": 10}, queue_capacity=2)
    assert result.actions == ()
    assert result.reason == "queue_full"
