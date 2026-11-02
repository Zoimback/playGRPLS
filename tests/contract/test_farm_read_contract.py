from src.game_data import extract_farm_relations, extract_farm_towns


def response():
    return {"backbone": {"models": [], "collections": [
        {"model_class_name": "FarmTowns", "data": [{"d": {"id": 1562, "name": "Nadraga", "resource_offer": "iron", "resource_demand": "stone"}}]},
        {"model_class_name": "FarmTownPlayerRelations", "data": [{"d": {"id": 22670, "farm_town_id": 1562, "player_id": 2738917, "relation_status": 1, "lootable_at": 1700000100, "last_looted_at": 1700000000, "loot": 324}}]},
    ]}}


def test_parse_farm_town_and_relation():
    towns = extract_farm_towns(response())
    relations = extract_farm_relations(response(), 2738917)
    assert towns[0].farm_town_id == 1562
    assert relations[0].lootable_at == 1700000100
    assert relations[0].loot == 324
