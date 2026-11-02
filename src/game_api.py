from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode

import requests
from .logging_config import logger

from .config import Settings, settings
from .game_data import extract_building_orders, extract_farm_relations, extract_farm_towns, parse_town_snapshot


class AmbiguousMutationError(RuntimeError):
    """The server may have applied a mutation before the connection failed."""


def build_building_payload(building_id: str, town_id: int) -> dict[str, Any]:
    return {
        "building_id": building_id,
        "town_id": town_id,
        "tear_down": 0,
        "no_bar": 0,
        "build_for_gold": False,
        "nl_init": True,
    }


def farm_collection_payload(relation_id: int, farm_town_id: int, town_id: int) -> dict[str, Any]:
    return {
        "model_url": f"FarmTownPlayerRelation/{relation_id}",
        "action_name": "claim",
        "captcha": None,
        "arguments": {"farm_town_id": farm_town_id, "type": "resources", "option": 1},
        "town_id": town_id,
        "nl_init": True,
    }


class GameAPI:
    def __init__(self, grepolis_session: Any, configuration: Settings = settings) -> None:
        self.grepolis_session = grepolis_session
        self.http = grepolis_session.http
        self.settings = configuration

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "text/plain, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.settings.server_url,
            "Referer": f"{self.settings.server_url}/game/index",
        }

    def _csrf(self) -> str:
        token = self.grepolis_session.get_csrf_token()
        if not token:
            raise RuntimeError("CSRF token is unavailable")
        return token

    @staticmethod
    def _json_response(response: Any) -> dict[str, Any]:
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and isinstance(data.get("json"), str):
            data["json"] = json.loads(data["json"])
        if not isinstance(data, dict):
            raise ValueError("Grepolis response must be an object")
        return data

    def _game_data(self) -> dict[str, Any]:
        params = {"town_id": self.settings.town_ids[0], "action": "get", "h": self._csrf()}
        payload = {"types": [{"type": "backbone"}], "town_id": self.settings.town_ids[0], "nl_init": False}
        logger.debug("Requesting Backbone for town %s", self.settings.town_ids[0])
        response = self.http.post(
            f"{self.settings.server_url}/game/data?{urlencode(params)}",
            data={"json": json.dumps(payload, separators=(",", ":"))},
            headers=self._headers(),
            timeout=self.settings.request_timeout,
        )
        data = self._json_response(response)
        logger.debug("Backbone response received with HTTP %s", getattr(response, "status_code", "unknown"))
        inner = data.get("json")
        if isinstance(inner, dict) and "backbone" in inner:
            return inner
        return data

    def get_town_snapshot(self):
        return parse_town_snapshot(self._game_data())

    def get_building_orders(self):
        return extract_building_orders(self._game_data(), self.settings.town_ids[0])

    def build_building(self, building_id: str, town_id: int) -> dict[str, Any]:
        payload = build_building_payload(building_id, town_id)
        if self.settings.dry_run:
            logger.info("DRY_RUN: planned construction %s in town %s", building_id, town_id)
            return {"success": "dry_run", "payload": payload}
        params = {"town_id": town_id, "action": "build_building", "h": self._csrf()}
        try:
            response = self.http.post(
                f"{self.settings.server_url}/game/town_overviews?{urlencode(params)}",
                data={"json": json.dumps(payload, separators=(",", ":"))},
                headers=self._headers(),
                timeout=self.settings.request_timeout,
            )
        except (requests.Timeout, requests.ConnectionError) as exc:
            raise AmbiguousMutationError("Build result is unknown") from exc
        logger.info("Construction request completed with HTTP %s", getattr(response, "status_code", "unknown"))
        data = self._json_response(response)
        body = data.get("json", data)
        if not isinstance(body, dict) or "success" not in body:
            raise ValueError("Build response lacks success")
        return body

    def get_farm_town_data(self) -> dict[str, Any]:
        return self._game_data()

    def get_farm_towns(self):
        return extract_farm_towns(self.get_farm_town_data())

    def get_farm_relations(self):
        return extract_farm_relations(self.get_farm_town_data(), self.settings.player_id)

    def collect_farm_town(self, relation_id: int, farm_town_id: int, town_id: int) -> dict[str, Any]:
        payload = farm_collection_payload(relation_id, farm_town_id, town_id)
        if self.settings.dry_run:
            logger.info("DRY_RUN: planned farm collection for town %s", farm_town_id)
            return {"success": "dry_run", "payload": payload}
        params = {"town_id": town_id, "action": "execute", "h": self._csrf()}
        try:
            response = self.http.post(
                f"{self.settings.server_url}/game/frontend_bridge?{urlencode(params)}",
                data={"json": json.dumps(payload, separators=(",", ":"))},
                headers=self._headers(),
                timeout=self.settings.request_timeout,
            )
        except (requests.Timeout, requests.ConnectionError) as exc:
            raise AmbiguousMutationError("Farm result is unknown") from exc
        logger.info("Farm collection request completed with HTTP %s", getattr(response, "status_code", "unknown"))
        data = self._json_response(response)
        body = data.get("json", data)
        if not isinstance(body, dict) or "success" not in body:
            raise ValueError("Farm response lacks success")
        return body
