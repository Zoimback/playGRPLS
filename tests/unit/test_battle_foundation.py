from src.models import BanditTarget


def test_bandit_cooldown_is_server_data():
    target = BanditTarget(1, 19, 300, 400, True, {}, {})
    assert target.cooldown_duration == 300
    assert target.cooldown_at == 400


def test_zero_cooldown_is_valid_server_value():
    target = BanditTarget(1, 1, 0, 100, False, {}, {})
    assert target.cooldown_duration == 0
