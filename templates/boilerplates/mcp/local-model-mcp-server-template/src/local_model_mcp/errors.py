from __future__ import annotations


class MCPServerError(Exception):
    code = "server_error"


class SecurityPolicyError(MCPServerError):
    code = "security_policy_violation"


class CapabilityNotFoundError(MCPServerError):
    code = "capability_not_found"

