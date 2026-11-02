import requests
import pytest

from src.config import Settings
from src.game_api import AmbiguousMutationError, GameAPI


class Response:
    def __init__(self, value, status=200): self.value, self.status = value, status
    def raise_for_status(self):
        if self.status >= 400: raise requests.HTTPError()
    def json(self): return self.value


class HTTP:
    def __init__(self, response): self.response, self.calls = response, []
    def post(self, url, **kwargs): self.calls.append((url, kwargs)); return self.response


class Session:
    def __init__(self, http, token="csrf"): self.http, self.token = http, token
    def get_csrf_token(self): return self.token


def config(tmp_path, dry_run=True):
    return Settings(town_ids=(3915,), farm_town_ids=(1562,), player_id=9, dry_run=dry_run, state_path=tmp_path / "state.json")


def backbone():
    return {"backbone": {"models": [{"model_class_name": "Town", "data": {"id": 3915, "resources": {}, "production": {}, "storage": 100, "available_population": 2}}, {"model_class_name": "BuildingBuildData", "data": {"building_data": {}}}], "collections": []}}


def test_reads_snapshot_and_orders(tmp_path):
    http = HTTP(Response(backbone()))
    api = GameAPI(Session(http), config(tmp_path))
    assert api.get_town_snapshot().town_id == 3915
    assert api.get_building_orders() == []
    assert len(http.calls) == 2


def test_farm_collection_dry_run_and_live(tmp_path):
    dry = GameAPI(Session(HTTP(Response({}))), config(tmp_path, True))
    assert dry.collect_farm_town(1, 1562, 3915)["success"] == "dry_run"
    http = HTTP(Response({"json": "{\"success\": \"ok\"}"}))
    live = GameAPI(Session(http), config(tmp_path, False))
    assert live.collect_farm_town(1, 1562, 3915)["success"] == "ok"
    assert "action=execute" in http.calls[0][0]


def test_missing_csrf_and_ambiguous_request(tmp_path):
    with pytest.raises(RuntimeError):
        GameAPI(Session(HTTP(Response({})), token=""), config(tmp_path, False)).build_building("lumber", 3915)
    class TimeoutHTTP:
        def post(self, url, **kwargs): raise requests.Timeout()
    api = GameAPI(Session(TimeoutHTTP()), config(tmp_path, False))
    with pytest.raises(AmbiguousMutationError):
        api.build_building("lumber", 3915)
