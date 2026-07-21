from __future__ import annotations


class MCPServerError(Exception):
    code = "server_error"


class SecurityPolicyError(MCPServerError):
    code = "security_policy_violation"


class CapabilityNotFoundError(MCPServerError):
    code = "capability_not_found"


class FileTooLargeError(MCPServerError):
    code = "file_too_large"


class ArtifactExistsError(MCPServerError):
    code = "artifact_exists"

