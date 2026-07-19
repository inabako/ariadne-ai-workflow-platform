from __future__ import annotations


class GatewayError(Exception):
    code = "gateway_error"


class AuthorizationError(GatewayError):
    code = "authorization_denied"


class ValidationError(GatewayError):
    code = "validation_error"


class RateLimitError(GatewayError):
    code = "rate_limit_exceeded"

