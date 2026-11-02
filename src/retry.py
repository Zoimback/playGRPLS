from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    limit: int = 3
    base_delay_seconds: int = 30

    def delay(self, attempt: int) -> int:
        if attempt < 0:
            raise ValueError("attempt cannot be negative")
        return self.base_delay_seconds * (2 ** attempt)

    def can_retry(self, attempt: int, ambiguous_mutation: bool = False) -> bool:
        return not ambiguous_mutation and attempt < self.limit


def is_transient_error(error: Exception) -> bool:
    return isinstance(error, (TimeoutError, ConnectionError, OSError))
