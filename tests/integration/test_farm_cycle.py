from src.farm_towns import run_farm_cycle


def test_farm_cycle_continues_after_one_collection_failure():
    class API:
        def get_farm_town_data(self):
            return {"backbone": {"models": [], "collections": [
                {"model_class_name": "FarmTowns", "data": [{"d": {"id": 1, "name": "one"}}, {"d": {"id": 2, "name": "two"}}]},
                {"model_class_name": "FarmTownPlayerRelations", "data": [
                    {"d": {"farm_town_id": 1, "player_id": 9, "relation_status": 1, "lootable_at": 100}},
                    {"d": {"farm_town_id": 2, "player_id": 9, "relation_status": 1, "lootable_at": 100}},
                ]},
            ]}}

    called = []

    def collect(farm_town_id):
        called.append(farm_town_id)
        if farm_town_id == 1:
            raise RuntimeError("temporary")

    result = run_farm_cycle(API(), {1, 2}, now=100, collect=collect, player_id=9)
    assert called == [1, 2]
    assert result.failed == [1]
    assert result.successful == [2]
