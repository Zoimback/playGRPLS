from src.game_api import build_building_payload


def test_build_building_payload_matches_observed_contract():
    payload = build_building_payload("lumber", 3915)
    assert payload == {
        "building_id": "lumber",
        "town_id": 3915,
        "tear_down": 0,
        "no_bar": 0,
        "build_for_gold": False,
        "nl_init": True,
    }
