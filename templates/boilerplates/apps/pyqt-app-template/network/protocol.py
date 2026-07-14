from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any


SUPPORTED_COMMANDS = {"DRIVE", "STOP", "VIDEO_TARGET", "PING", "PONG", "TELEMETRY"}


@dataclass(frozen=True)
class ProtocolMessage:
    command: str
    payload: dict[str, Any]


def encode_message(command: str, payload: dict[str, Any] | None = None) -> bytes:
    if command not in SUPPORTED_COMMANDS:
        raise ValueError(f"unsupported command: {command}")
    return json.dumps({"command": command, "payload": payload or {}}, separators=(",", ":")).encode("utf-8")


def decode_message(data: bytes) -> ProtocolMessage:
    raw = json.loads(data.decode("utf-8"))
    command = raw.get("command")
    if command not in SUPPORTED_COMMANDS:
        raise ValueError(f"unsupported command: {command}")
    payload = raw.get("payload") or {}
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    return ProtocolMessage(command=command, payload=payload)
