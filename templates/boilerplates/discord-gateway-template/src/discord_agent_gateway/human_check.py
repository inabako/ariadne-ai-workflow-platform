from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class HumanCheckToken:
    public_token: str
    job_id: str
    human_check_id: str
    expires_at: datetime


class HumanCheckTokenManager:
    def __init__(self, secret: str | None = None, ttl_seconds: int = 900) -> None:
        self.secret = secret or secrets.token_hex(16)
        self.ttl_seconds = ttl_seconds
        self._tokens: dict[str, HumanCheckToken] = {}

    def create(self, job_id: str, human_check_id: str) -> HumanCheckToken:
        nonce = secrets.token_hex(8)
        digest = hmac.new(self.secret.encode("utf-8"), f"{job_id}:{human_check_id}:{nonce}".encode("utf-8"), hashlib.sha256).hexdigest()
        public_token = f"hc_{nonce}_{digest[:16]}"
        token = HumanCheckToken(
            public_token=public_token,
            job_id=job_id,
            human_check_id=human_check_id,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds),
        )
        self._tokens[public_token] = token
        return token

    def verify(self, public_token: str) -> HumanCheckToken:
        token = self._tokens[public_token]
        if datetime.now(timezone.utc) >= token.expires_at:
            raise ValueError("human check token expired")
        return token

