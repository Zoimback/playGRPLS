from pathlib import Path

from src.logging_config import redact


SECRET_NAMES = {".env", "build_building.network-request", "build_building.network-response", "farm_collect.network-request", "farm_collect.network-response"}


def test_redaction_removes_runtime_secrets():
    value = redact({"cookie": "secret", "csrf_token": "secret", "password": "secret", "safe": "ok"})
    assert value == {"cookie": "[REDACTED]", "csrf_token": "[REDACTED]", "password": "[REDACTED]", "safe": "ok"}


def test_secret_artifacts_are_ignored_by_repository_rules():
    gitignore = Path(".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert "investigacion/data/" in gitignore
