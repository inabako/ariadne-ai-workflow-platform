from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass

from .model_adapter import LocalModelAdapter, ModelResponse


@dataclass(frozen=True)
class OllamaRequest:
    endpoint: str
    model: str
    prompt: str
    stream: bool = False

    def body(self) -> bytes:
        return json.dumps({"model": self.model, "prompt": self.prompt, "stream": self.stream}).encode("utf-8")


class OllamaAdapter(LocalModelAdapter):
    def __init__(self, endpoint: str = "http://127.0.0.1:11434/api/generate", timeout_seconds: int = 60) -> None:
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def build_request(self, prompt: str, *, model_id: str) -> OllamaRequest:
        return OllamaRequest(endpoint=self.endpoint, model=model_id, prompt=prompt)

    def invoke(self, prompt: str, *, model_id: str, max_tokens: int = 512) -> ModelResponse:
        request_model = self.build_request(prompt[:max_tokens], model_id=model_id)
        request = urllib.request.Request(
            request_model.endpoint,
            data=request_model.body(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return ModelResponse(
            model_id=model_id,
            text=str(payload.get("response", "")),
            tokens_used=min(len(prompt.split()), max_tokens),
        )

