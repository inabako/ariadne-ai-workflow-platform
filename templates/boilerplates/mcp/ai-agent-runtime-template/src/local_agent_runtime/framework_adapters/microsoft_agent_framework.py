from __future__ import annotations

from .base import FrameworkAdapterPattern


class MicrosoftAgentFrameworkRuntimeAdapter(FrameworkAdapterPattern):
    def __init__(self) -> None:
        super().__init__(
            adapter_name="microsoft-agent-framework",
            framework_name="Microsoft Agent Framework",
        )
