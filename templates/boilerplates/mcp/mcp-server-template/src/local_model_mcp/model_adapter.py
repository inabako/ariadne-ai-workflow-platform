from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelResponse:
    model_id: str
    text: str
    tokens_used: int


class LocalModelAdapter:
    def invoke(self, prompt: str, *, model_id: str, max_tokens: int = 512) -> ModelResponse:
        raise NotImplementedError


class MockModelAdapter(LocalModelAdapter):
    def invoke(self, prompt: str, *, model_id: str, max_tokens: int = 512) -> ModelResponse:
        text = f"[mock:{model_id}] {prompt[:max_tokens]}"
        return ModelResponse(model_id=model_id, text=text, tokens_used=min(len(prompt.split()), max_tokens))

