from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests

from .config import Settings, settings
from .logging_config import logger


class _InputParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inputs: list[dict[str, str | bool]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() != "input":
            return
        values = dict(attrs)
        self.inputs.append({
            "name": values.get("name", ""),
            "type": values.get("type", "text").casefold(),
            "value": values.get("value", ""),
            "checked": "checked" in values,
            "disabled": "disabled" in values,
        })


class GrepolisSession:
    def __init__(self, configuration: Settings = settings) -> None:
        self.settings = configuration
        self.http = requests.Session()
        self.http.headers.update({"User-Agent": "GrepolisBot/1.0", "Accept": "text/html,application/json,*/*"})
        self.game_url = configuration.server_url.rstrip("/")
        self.csrf_token: str | None = None
        self.logged_in = False

    @staticmethod
    def _origin(url: str) -> str:
        parsed = urlsplit(url)
        return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))

    def _request(self, method: str, url: str, **kwargs):
        kwargs.setdefault("timeout", self.settings.request_timeout)
        return self.http.request(method, url, **kwargs)

    def _parse_inputs(self, html: str):
        parser = _InputParser()
        parser.feed(html)
        return parser.inputs

    @staticmethod
    def _unwrap_json(value):
        for _ in range(5):
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                    continue
                except json.JSONDecodeError:
                    return value
            if isinstance(value, dict) and "json" in value:
                value = value["json"]
                continue
            break
        return value

    def login(self) -> None:
        logger.info("Starting Grepolis login for world %s", self.settings.world)
        self.settings.validate()
        portal = self.settings.portal_url
        login_page = f"{portal}/"
        self._request("GET", login_page).raise_for_status()
        logger.debug("Portal session initialized")
        response = self._request("POST", f"{portal}/api/login", json={"username": self.settings.username, "password": self.settings.password, "useRememberMe": True}, headers={"Content-Type": "application/json", "Origin": portal, "Referer": login_page})
        response.raise_for_status()
        logger.debug("Central login accepted")
        redirect = response.json().get("redirectUrl")
        if not redirect:
            raise RuntimeError("Login did not return redirectUrl")
        start_response = self._request("GET", redirect, headers={"Referer": login_page}, allow_redirects=True)
        start_response.raise_for_status()
        start_origin = self._origin(start_response.url)
        inputs = self._parse_inputs(start_response.text)
        username = next((str(item["value"]) for item in inputs if item["name"] == "name" and item["type"] == "text"), self.settings.username)
        passwordhash = next((str(item["value"]) for item in inputs if item["name"] == "passwordhash"), "")
        worlds = self._request("POST", f"{start_origin}/start/index?action=login_from_start_page", data={"json": json.dumps({"name": username, "password": "", "passwordhash": passwordhash, "autologin": False, "window_size": "1920x1080"})}, headers={"X-Requested-With": "XMLHttpRequest", "Origin": start_origin, "Referer": start_response.url})
        worlds.raise_for_status()
        available = self._unwrap_json(worlds.json())
        if not isinstance(available, dict):
            raise RuntimeError("World response is not a JSON object")
        target = next((item for item in available.get("worlds", []) if str(item.get("id")) == self.settings.world), None)
        if not target or not target.get("playing_on"):
            raise RuntimeError(f"World unavailable: {self.settings.world}")
        fields = []
        for item in inputs:
            name = str(item["name"])
            if not name or item["disabled"] or item["type"] in {"submit", "button", "reset", "file"}:
                continue
            if item["type"] in {"checkbox", "radio"} and not item["checked"]:
                continue
            value = str(item["value"])
            if name == "world": value = self.settings.world
            if name == "action": value = "login_to_game_world"
            fields.append((name, value))
        if not any(name == "world" for name, _ in fields): fields.append(("world", self.settings.world))
        if not any(name == "action" for name, _ in fields): fields.append(("action", "login_to_game_world"))
        selected = self._request("POST", f"{start_origin}/start?action=login_to_game_world", data=fields, headers={"Origin": start_origin, "Referer": f"{start_origin}/start/index"}, allow_redirects=False)
        selected.raise_for_status()
        location = selected.headers.get("Location")
        if not location:
            raise RuntimeError("World selection did not redirect")
        game_response = self._request("GET", urljoin(selected.url, location), allow_redirects=True)
        game_response.raise_for_status()
        self.game_url = self._origin(game_response.url)
        self.refresh_csrf_token()
        self.logged_in = True
        logger.info("Grepolis session ready")

    def refresh_csrf_token(self) -> str:
        logger.debug("Refreshing CSRF token")
        response = self._request("GET", f"{self.game_url}/game/index")
        response.raise_for_status()
        patterns = [r'"csrfToken"\s*:\s*"([^"]+)"', r"Game\.csrfToken\s*=\s*['\"]([^'\"]+)"]
        for pattern in patterns:
            match = re.search(pattern, response.text, re.IGNORECASE)
            if match:
                self.csrf_token = match.group(1)
                return self.csrf_token
        raise RuntimeError("CSRF token not found")

    def get_csrf_token(self) -> str:
        return self.csrf_token or self.refresh_csrf_token()

    def close(self) -> None:
        self.http.close()
        self.logged_in = False
