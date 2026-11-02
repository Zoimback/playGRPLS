from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import load_json


IGNORED_PATH_PREFIXES = ("backbone.benchmarks", "benchmarks")


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            result.update(flatten(item, child))
        return result
    if isinstance(value, list):
        return {prefix: value}
    return {prefix: value}


def compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    before = flatten(left)
    after = flatten(right)
    paths = sorted(
        path for path in set(before) | set(after)
        if not path.startswith(IGNORED_PATH_PREFIXES)
    )
    return {
        "changed": {path: {"before": before.get(path), "after": after.get(path)} for path in paths if before.get(path) != after.get(path)},
        "changed_count": sum(before.get(path) != after.get(path) for path in paths),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compara dos snapshots sin realizar peticiones.")
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(load_json(args.before), load_json(args.after)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())