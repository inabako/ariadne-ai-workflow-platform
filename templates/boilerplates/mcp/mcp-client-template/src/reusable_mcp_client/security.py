from __future__ import annotations

from pathlib import PurePath

from .errors import SecurityPolicyError


def validate_resource_uri(uri: str) -> None:
    if uri.startswith("file://"):
        raise SecurityPolicyError("file:// resources are disabled by default")
    if PurePath(uri).is_absolute() or "\\" in uri:
        raise SecurityPolicyError("resource URIs must not be interpreted as local paths")


def mask_secrets(arguments: dict[str, object]) -> dict[str, object]:
    masked: dict[str, object] = {}
    for key, value in arguments.items():
        lowered = key.lower()
        masked[key] = "***" if any(fragment in lowered for fragment in ("token", "password", "secret", "api_key")) else value
    return masked

