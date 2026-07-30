from __future__ import annotations

from .config import ServerConfig

__all__ = ["LocalModelMCPServer", "ServerConfig", "create_server"]


def __getattr__(name: str):
    if name in {"LocalModelMCPServer", "create_server"}:
        from .server import LocalModelMCPServer, create_server

        return {"LocalModelMCPServer": LocalModelMCPServer, "create_server": create_server}[name]
    raise AttributeError(name)
