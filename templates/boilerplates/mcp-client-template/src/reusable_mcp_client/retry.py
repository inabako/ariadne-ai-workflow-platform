from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    retryable_error_codes: tuple[str, ...] = ("timeout", "connection_lost")

    def should_retry(self, error_code: str, attempt: int) -> bool:
        return attempt < self.max_attempts and error_code in self.retryable_error_codes

