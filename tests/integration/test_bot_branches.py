from src.config import Settings
from src.main import Bot
from src.models import Building, BuildingOrder, FarmTownRelation, TownSnapshot


class API:
    def get_town_snapshot(self):
        return TownSnapshot(1, {"wood": 10, "stone": 10, "iron": 10}, {"wood": 60, "stone": 60, "iron": 60}, 1000, 10, [Building("lumber", 1, 2, True, True, {"wood": 5}, [], None, True, 1, 10)], [])
    def build_building(self, building_id, town_id): return {"success": "dry_run", "next_fetch_in": 10}
    def get_farm_town_data(self): return {"backbone": {"models": [], "collections": []}}
    def get_farm_relations(self): return [FarmTownRelation(1, 9, 1, 100, 50)]


def test_bot_runs_ready_construction_and_empty_farms(tmp_path):
    bot = Bot(API(), Settings(town_ids=(1,), farm_town_ids=(), player_id=9, state_path=tmp_path / "state.json"))
    result = bot.run_once(100)
    assert result["construction"]["building_id"] == "lumber"
    assert result["farms"]["successful"] == []
