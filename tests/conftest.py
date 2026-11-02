from __future__ import annotations

import pytest


class FakeClock:
    def __init__(self, value: int = 1_700_000_000) -> None:
        self.value = value

    def __call__(self) -> int:
        return self.value

    def advance(self, seconds: int) -> None:
        self.value += seconds


@pytest.fixture
def fake_clock() -> FakeClock:
    return FakeClock()
