from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class StateStore:
    def __init__(self, path: Path, version: int = 1) -> None:
        self.path = path
        self.version = version

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": self.version, "tasks": {}}
        try:
            with self.path.open("r", encoding="utf-8") as source:
                state = json.load(source)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid state file: {self.path}") from exc
        if not isinstance(state, dict) or not isinstance(state.get("tasks", {}), dict):
            raise ValueError("State must contain a tasks object")
        return state

    def save(self, state: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        payload = dict(state)
        payload["version"] = self.version
        with temporary.open("w", encoding="utf-8", newline="\n") as target:
            json.dump(payload, target, ensure_ascii=False, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, self.path)
