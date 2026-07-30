from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    retryable_reasons: tuple[str, ...] = ("temporary_model_error", "mcp_timeout", "transient_io")

    def can_retry(self, reason: str, attempt: int) -> bool:
        return attempt < self.max_attempts and reason in self.retryable_reasons

