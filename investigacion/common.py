from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SENSITIVE_KEY_PARTS = (
    "csrf",
    "cookie",
    "password",
    "secret",
    "token",
    "authorization",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as source:
        value = json.load(source)

    if not isinstance(value, dict):
        raise ValueError(f"El JSON raiz debe ser un objeto: {path}")
    return value


def redact(value: Any, parent_key: str = "") -> Any:
    if any(part in parent_key.casefold() for part in SENSITIVE_KEY_PARTS):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(key): redact(item, str(key)) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, parent_key) for item in value]
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as target:
        json.dump(redact(value), target, ensure_ascii=False, indent=2)
        target.write("\n")


def backbone_models(response: dict[str, Any]) -> list[dict[str, Any]]:
    backbone = response.get("backbone", response)
    if not isinstance(backbone, dict):
        raise ValueError("No se encuentra backbone como objeto")
    entries = []
    for section in ("models", "collections"):
        values = backbone.get(section)
        if not isinstance(values, list):
            continue
        entries.extend(
            {"_section": section, "_index": index, **model}
            for index, model in enumerate(values)
            if isinstance(model, dict)
        )
    if not entries:
        raise ValueError("No se encuentran backbone.models ni backbone.collections")
    return entries


def model_inventory(response: dict[str, Any]) -> list[dict[str, Any]]:
    inventory = []
    for index, model in enumerate(backbone_models(response)):
        data = model.get("data")
        inventory.append(
            {
                "section": model["_section"],
                "index": model["_index"],
                "class_name": model.get("model_class_name", model.get("class_name")),
                "model_keys": sorted(key for key in model if not key.startswith("_")),
                "data_keys": sorted(data) if isinstance(data, dict) else [],
                "data_type": type(data).__name__,
                "data_size": len(data) if isinstance(data, (dict, list)) else None,
            }
        )
    return inventory


def keyword_hits(response: dict[str, Any], keywords: tuple[str, ...]) -> list[dict[str, Any]]:
    hits = []
    for item in model_inventory(response):
        text = json.dumps(item, ensure_ascii=False).casefold()
        matches = [keyword for keyword in keywords if keyword.casefold() in text]
        if matches:
            hits.append({"section": item["section"], "index": item["index"], "matches": matches, "class_name": item["class_name"]})
    return hits