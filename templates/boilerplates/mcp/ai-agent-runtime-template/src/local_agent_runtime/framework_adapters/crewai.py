from __future__ import annotations

from .base import FrameworkAdapterPattern


class CrewAIRuntimeAdapter(FrameworkAdapterPattern):
    def __init__(self) -> None:
        super().__init__(adapter_name="crewai", framework_name="CrewAI")
