from src.game_data import extract_building_orders, parse_town_snapshot


def test_parse_observed_building_backbone():
    response = {
        "backbone": {
            "models": [
                {"model_class_name": "Town", "data": {"id": 3915, "resources": {"wood": 100, "stone": 200, "iron": 300}, "production": {"wood": 60, "stone": 120, "iron": 60}, "storage": 1000, "available_population": 20}},
                {"model_class_name": "BuildingBuildData", "data": {"town_id": 3915, "building_data": {"lumber": {"level": 7, "next_level": 8, "can_upgrade": True, "enough_resources": True, "enough_storage": True, "resources_for": {"wood": 525, "stone": 385, "iron": 239}, "population_for": 4, "population_free": 20, "missing_dependencies": []}}}},
            ],
            "collections": [{"model_class_name": "BuildingOrders", "data": [{"d": {"id": 10, "town_id": 3915, "building_type": "lumber", "to_be_completed_at": 1700000100, "created_at": 1700000000, "building_time": 100}}]}],
        }
    }
    snapshot = parse_town_snapshot(response)
    orders = extract_building_orders(response, 3915)
    assert snapshot.town_id == 3915
    assert snapshot.buildings[0].building_id == "lumber"
    assert orders[0].to_be_completed_at == 1700000100
