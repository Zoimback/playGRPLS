import pytest

from src.config import Settings, _bool, _csv_ints


def test_config_parsers():
    assert _csv_ints("1, 2") == (1, 2)
    assert _csv_ints("") == ()
    assert _bool("false") is False
    with pytest.raises(ValueError):
        _csv_ints("0")


def test_settings_validation():
    Settings(town_ids=(1,), farm_interval_seconds=1, construction_margin_seconds=0, retry_limit=0, request_timeout=1).validate()
    with pytest.raises(ValueError):
        Settings(farm_interval_seconds=0).validate()
    with pytest.raises(ValueError):
        Settings(construction_margin_seconds=-1).validate()
    with pytest.raises(ValueError):
        Settings(retry_limit=-1).validate()
    with pytest.raises(ValueError):
        Settings(request_timeout=0).validate()
    with pytest.raises(ValueError):
        Settings(username="", password="", dry_run=False).validate()
