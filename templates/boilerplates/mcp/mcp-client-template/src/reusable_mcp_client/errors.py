from __future__ import annotations


class MCPClientError(Exception):
    code = "client_error"


class ServerNotFoundError(MCPClientError):
    code = "server_not_found"


class SessionNotConnectedError(MCPClientError):
    code = "session_not_connected"


class SecurityPolicyError(MCPClientError):
    code = "security_policy_violation"

