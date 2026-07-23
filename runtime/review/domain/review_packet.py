from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReviewPacket:
    work_id: str
    target: str
    target_revision: str
    intent: str
    requirements: list[str] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)
    guardrails: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    scope: list[str] = field(default_factory=list)
    known_constraints: list[str] = field(default_factory=list)
    required_reviewers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "work_id": self.work_id,
            "target": self.target,
            "target_revision": self.target_revision,
            "intent": self.intent,
            "requirements": self.requirements,
            "changed_files": self.changed_files,
            "guardrails": self.guardrails,
            "evidence": self.evidence,
            "scope": self.scope,
            "known_constraints": self.known_constraints,
            "required_reviewers": self.required_reviewers,
        }


def packet_hash(packet: dict[str, Any]) -> str:
    payload = json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
