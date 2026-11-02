from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


ROOT_DIR = Path(__file__).resolve().parents[1]
if load_dotenv:
    env_candidates = (
        ROOT_DIR / "src" / ".env",
        ROOT_DIR / ".env",
        ROOT_DIR / "noselenium" / ".env",
    )
    env_file = next((path for path in env_candidates if path.exists()), None)
    if env_file is not None:
        load_dotenv(env_file, override=True)


def _csv_ints(value: str) -> tuple[int, ...]:
    if not value.strip():
        return ()
    try:
        result = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise ValueError("IDs must be comma-separated integers") from exc
    if any(item <= 0 for item in result):
        raise ValueError("IDs must be positive")
    return result


def _bool(value: str) -> bool:
    return value.strip().casefold() not in {"0", "false", "no", "off"}


@dataclass(frozen=True)
class Settings:
    username: str = os.getenv("GREEPOLIS_USERNAME", "")
    password: str = os.getenv("GREEPOLIS_PASSWORD", "")
    world: str = os.getenv("GREEPOLIS_WORLD", "es148")
    server_url: str = os.getenv("GREEPOLIS_SERVER_URL", "https://es148.grepolis.com").rstrip("/")
    portal_url: str = os.getenv("GREEPOLIS_PORTAL_URL", "https://es-play.grepolis.com").rstrip("/")
    town_ids: tuple[int, ...] = _csv_ints(os.getenv("GREEPOLIS_TOWN_IDS", os.getenv("GREEPOLIS_TOWN_ID", "")))
    farm_town_ids: tuple[int, ...] = _csv_ints(os.getenv("GREEPOLIS_FARM_TOWN_IDS", ""))
    player_id: int = int(os.getenv("GREEPOLIS_PLAYER_ID", "0") or 0)
    dry_run: bool = _bool(os.getenv("DRY_RUN", "true"))
    farm_interval_seconds: int = int(os.getenv("FARM_INTERVAL_SECONDS", "300"))
    farm_short_interval_seconds: int = int(os.getenv("FARM_SHORT_INTERVAL_SECONDS", "1200"))
    farm_long_interval_seconds: int = int(os.getenv("FARM_LONG_INTERVAL_SECONDS", "5400"))
    construction_margin_seconds: int = int(os.getenv("CONSTRUCTION_MARGIN_SECONDS", os.getenv("SCHEDULER_MARGIN_SECONDS", "60")))
    retry_limit: int = int(os.getenv("RETRY_LIMIT", "3"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    queue_capacity: int = int(os.getenv("CONSTRUCTION_QUEUE_CAPACITY", "2"))
    battle_safety_threshold: float = float(os.getenv("BATTLE_SAFETY_THRESHOLD", "1.0"))
    state_path: Path = Path(os.getenv("STATE_PATH", "data/state.json"))

    def validate(self) -> None:
        if self.farm_interval_seconds <= 0:
            raise ValueError("FARM_INTERVAL_SECONDS must be positive")
        if self.farm_short_interval_seconds <= 0 or self.farm_long_interval_seconds <= 0:
            raise ValueError("Farm alternation intervals must be positive")
        if self.construction_margin_seconds < 0:
            raise ValueError("CONSTRUCTION_MARGIN_SECONDS cannot be negative")
        if self.retry_limit < 0:
            raise ValueError("RETRY_LIMIT cannot be negative")
        if self.request_timeout <= 0:
            raise ValueError("REQUEST_TIMEOUT must be positive")
        if self.queue_capacity <= 0:
            raise ValueError("CONSTRUCTION_QUEUE_CAPACITY must be positive")
        if not 0 <= self.battle_safety_threshold <= 1:
            raise ValueError("BATTLE_SAFETY_THRESHOLD must be between 0 and 1")
        if self.dry_run is False and (not self.username or not self.password):
            raise ValueError("Credentials are required when DRY_RUN is false")

    def resolved_state_path(self) -> Path:
        return self.state_path if self.state_path.is_absolute() else ROOT_DIR / self.state_path


settings = Settings()
