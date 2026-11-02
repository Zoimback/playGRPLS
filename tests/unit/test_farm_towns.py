from src.farm_towns import evaluate_farm_towns


def test_only_active_eligible_configured_farms_are_selected():
    response = {"backbone": {"models": [], "collections": [
        {"model_class_name": "FarmTowns", "data": [{"d": {"id": 1, "name": "ready"}}, {"d": {"id": 2, "name": "future"}}, {"d": {"id": 3, "name": "inactive"}}]},
        {"model_class_name": "FarmTownPlayerRelations", "data": [
            {"d": {"farm_town_id": 1, "player_id": 9, "relation_status": 1, "lootable_at": 100}},
            {"d": {"farm_town_id": 2, "player_id": 9, "relation_status": 1, "lootable_at": 200}},
            {"d": {"farm_town_id": 3, "player_id": 9, "relation_status": 0, "lootable_at": None}},
        ]},
    ]}}
    statuses = evaluate_farm_towns(response, {1, 2, 3}, now=150, player_id=9)
    assert [(item.farm_town.farm_town_id, item.eligible) for item in statuses] == [(1, True), (2, False), (3, False)]
    assert statuses[1].reason == "lootable_at_in_future"


def test_missing_relation_is_not_eligible():
    response = {"backbone": {"models": [], "collections": [{"model_class_name": "FarmTowns", "data": [{"d": {"id": 1, "name": "missing"}}]}]}}
    status = evaluate_farm_towns(response, {1}, now=100, player_id=9)[0]
    assert not status.eligible
    assert status.reason == "missing_relation"
