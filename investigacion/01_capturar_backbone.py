from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOSELENIUM = ROOT / "noselenium"
if str(NOSELENIUM) not in sys.path:
    sys.path.insert(0, str(NOSELENIUM))

from config import settings  # noqa: E402
from http_client.game_api import GrepolisAPI  # noqa: E402
from http_client.session import GrepolisSession  # noqa: E402

from common import write_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Captura un Backbone sin exponer secretos.")
    parser.add_argument("--output", type=Path, default=Path("investigacion/data/backbone.json"))
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    session = GrepolisSession()
    try:
        session.login()
        response = GrepolisAPI(session).get_backbone()
        write_json(args.output, response)
        print(f"Snapshot guardado en {args.output} ({len(response.get('backbone', {}).get('models', []))} modelos)")
    finally:
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())