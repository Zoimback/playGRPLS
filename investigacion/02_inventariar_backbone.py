from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import keyword_hits, load_json, model_inventory


KEYWORDS = ("building", "construction", "queue", "order", "finish", "remaining", "farm", "loot")


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume modelos y campos de un snapshot local.")
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    response = load_json(args.snapshot)
    report = {
        "snapshot": str(args.snapshot),
        "model_count": len(model_inventory(response)),
        "models": model_inventory(response),
        "keyword_hits": keyword_hits(response, KEYWORDS),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())