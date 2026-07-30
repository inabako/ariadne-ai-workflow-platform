from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelPortResponse:
    model_id: str
    text: str
    tokens_used: int


class ModelPort(Protocol):
    def invoke(self, prompt: str, *, model_id: str, max_tokens: int = 512) -> ModelPortResponse:
        ...
