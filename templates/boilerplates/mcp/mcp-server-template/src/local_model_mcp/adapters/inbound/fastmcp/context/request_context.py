from __future__ import annotations

from typing import Any

from .....application.dto.requests import RequestContext


def map_request_context(raw_context: Any | None = None) -> RequestContext:
    if raw_context is None:
        return RequestContext()
    request_id = str(getattr(raw_context, "request_id", "") or "")
    trace_id = str(getattr(raw_context, "trace_id", "") or "")
    client_name = getattr(raw_context, "client_name", None)
    return RequestContext(
        request_id=request_id,
        trace_id=trace_id,
        client_name=str(client_name) if client_name else None,
        metadata={},
    )
