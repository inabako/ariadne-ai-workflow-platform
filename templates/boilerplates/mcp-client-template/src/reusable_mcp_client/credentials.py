from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class CredentialProvider:
    prefix: str = "MCP_SERVER"

    def token_for(self, server_id: str) -> str | None:
        key = f"{self.prefix}_{server_id.upper().replace('-', '_')}_TOKEN"
        return os.environ.get(key)

