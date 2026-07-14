from __future__ import annotations

from dataclasses import dataclass

from .errors import SecurityPolicyError


@dataclass(frozen=True)
class HTTPSecurityPolicy:
    allowed_hosts: tuple[str, ...] = ("127.0.0.1", "localhost")
    allowed_origins: tuple[str, ...] = ("http://127.0.0.1", "http://localhost")

    def validate(self, *, host: str, origin: str | None = None) -> None:
        if host not in self.allowed_hosts:
            raise SecurityPolicyError(f"host is not allowed: {host}")
        if origin is not None and origin not in self.allowed_origins:
            raise SecurityPolicyError(f"origin is not allowed: {origin}")

