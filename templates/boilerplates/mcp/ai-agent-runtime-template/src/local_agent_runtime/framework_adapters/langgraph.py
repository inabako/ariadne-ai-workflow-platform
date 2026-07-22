from __future__ import annotations

from .base import FrameworkAdapterPattern


class LangGraphRuntimeAdapter(FrameworkAdapterPattern):
    def __init__(self) -> None:
        super().__init__(adapter_name="langgraph", framework_name="LangGraph")
