from __future__ import annotations

from pathlib import Path

from .errors import SecurityPolicyError


def reject_binary_file(path: Path, sample_size: int = 4096) -> None:
    sample = path.read_bytes()[:sample_size]
    if b"\x00" in sample:
        raise SecurityPolicyError("binary files are denied")


def require_text_content(content: str, max_bytes: int) -> None:
    if len(content.encode("utf-8")) > max_bytes:
        raise SecurityPolicyError("content exceeds configured byte limit")

