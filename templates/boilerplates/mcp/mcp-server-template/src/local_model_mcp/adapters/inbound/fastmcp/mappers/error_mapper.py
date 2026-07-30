from __future__ import annotations

from .....application.exceptions import ApplicationException
from .....domain.exceptions import DomainException
from .....errors import MCPServerError


def map_exception(exc: Exception) -> dict[str, str]:
    if isinstance(exc, MCPServerError):
        return {"status": "error", "error_code": exc.code, "message": str(exc)}
    if isinstance(exc, ApplicationException):
        return {"status": "error", "error_code": exc.code, "message": str(exc)}
    if isinstance(exc, DomainException):
        return {"status": "error", "error_code": exc.code, "message": str(exc)}
    return {"status": "error", "error_code": "adapter_error", "message": "adapter failed"}
