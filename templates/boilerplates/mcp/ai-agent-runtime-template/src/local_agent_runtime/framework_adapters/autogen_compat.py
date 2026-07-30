from __future__ import annotations

from .base import FrameworkAdapterPattern


class AutoGenCompatibilityAdapter(FrameworkAdapterPattern):
    def __init__(self) -> None:
        super().__init__(adapter_name="autogen-compatibility", framework_name="AutoGen Compatibility")
