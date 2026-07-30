from __future__ import annotations

from ....application.ports.outbound.model_port import ModelPortResponse
from ....model_adapter import LocalModelAdapter


class LocalModelPortAdapter:
    def __init__(self, adapter: LocalModelAdapter) -> None:
        self.adapter = adapter

    def invoke(self, prompt: str, *, model_id: str, max_tokens: int = 512) -> ModelPortResponse:
        response = self.adapter.invoke(prompt, model_id=model_id, max_tokens=max_tokens)
        return ModelPortResponse(
            model_id=response.model_id,
            text=response.text,
            tokens_used=response.tokens_used,
        )
