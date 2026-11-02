from src.game_api import farm_collection_payload


def test_five_minute_collection_payload_matches_observed_contract():
    assert farm_collection_payload(22670, 1562, 3915) == {
        "model_url": "FarmTownPlayerRelation/22670",
        "action_name": "claim",
        "captcha": None,
        "arguments": {"farm_town_id": 1562, "type": "resources", "option": 1},
        "town_id": 3915,
        "nl_init": True,
    }
