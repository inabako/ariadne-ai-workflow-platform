from __future__ import annotations

from .....application.dto.responses import ToolResponse


def map_tool_response(response: ToolResponse) -> dict[str, object]:
    return response.to_dict()
