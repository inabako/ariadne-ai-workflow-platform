from __future__ import annotations

import json
from typing import Any

from .server import LocalModelMCPServer


class StdioDispatcher:
    def __init__(self, server: LocalModelMCPServer) -> None:
        self.server = server

    def dispatch_line(self, line: str) -> str:
        request = json.loads(line)
        response = self.dispatch(request)
        return json.dumps(response, ensure_ascii=False)

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        method = request.get("method")
        params = request.get("params") or {}
        request_id = request.get("id")
        try:
            if method == "prompts/list":
                result: Any = self.server.list_prompts()
            elif method == "prompts/get":
                result = self.server.get_prompt(params["name"], params.get("arguments", {}))
            elif method == "resources/list":
                result = self.server.list_resources()
            elif method == "resources/read":
                result = self.server.read_resource(params["uri"])
            elif method == "tools/list":
                result = self.server.list_tools()
            elif method == "tools/call":
                result = self.server.call_tool(params["name"], params.get("arguments", {}))
            else:
                return {"id": request_id, "error": {"code": "method_not_found", "message": str(method)}}
            return {"id": request_id, "result": result}
        except Exception as exc:
            return {"id": request_id, "error": {"code": "dispatch_error", "message": str(exc)}}

