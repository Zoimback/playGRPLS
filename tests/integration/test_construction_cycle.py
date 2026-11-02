from types import SimpleNamespace

from src.config import Settings
from src.game_api import GameAPI


class FakeResponse:
    def __init__(self, value):
        self.value = value

    def raise_for_status(self):
        return None

    def json(self):
        return self.value


class FakeHTTP:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.response)


class FakeSession:
    def __init__(self, http):
        self.http = http

    def get_csrf_token(self):
        return "csrf-test"


def settings(tmp_path, dry_run):
    return Settings(
        town_ids=(3915,),
        dry_run=dry_run,
        state_path=tmp_path / "state.json",
    )


def test_dry_run_does_not_send_build_request(tmp_path):
    http = FakeHTTP({"json": {"success": "ok"}})
    api = GameAPI(FakeSession(http), settings(tmp_path, True))

    result = api.build_building("lumber", 3915)

    assert result["success"] == "dry_run"
    assert http.calls == []


def test_live_build_sends_observed_action(tmp_path):
    http = FakeHTTP({"json": "{\"success\": \"ok\", \"next_fetch_in\": 10}"})
    api = GameAPI(FakeSession(http), settings(tmp_path, False))

    result = api.build_building("lumber", 3915)

    assert result["success"] == "ok"
    assert len(http.calls) == 1
    url, kwargs = http.calls[0]
    assert "action=build_building" in url
    assert '"building_id":"lumber"' in kwargs["data"]["json"]
