from __future__ import annotations

import logging
import re
from typing import Any

SENSITIVE_PARTS = ("password", "cookie", "csrf", "token", "authorization", "secret")


def redact(value: Any, key: str = "") -> Any:
    if any(part in key.casefold() for part in SENSITIVE_PARTS):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(item_key): redact(item, str(item_key)) for item_key, item in value.items()}
    if isinstance(value, list):
        return [redact(item, key) for item in value]
    if isinstance(value, str):
        return re.sub(r"([?&]h=)[^&\s]+", r"\1[REDACTED]", value)
    return value


def configure_logging(level: int = logging.INFO) -> None:
    """Configure console logging without exposing request secrets."""
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)


logger = logging.getLogger("grepolis")
