from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SEVERITIES = ("critical", "high", "medium", "low", "info")
FINDING_VERDICTS = ("pass", "warn", "fail", "unsupported", "needs-qa", "changes-required")
BLOCKING_VERDICTS = {"fail", "unsupported", "needs-qa", "changes-required"}


@dataclass(frozen=True)
class ReviewFinding:
    finding_id: str
    reviewer: str
    category: str
    severity: str
    claim: str
    verdict: str
    evidence_refs: list[str] = field(default_factory=list)
    counterexample: str = ""
    reasoning_summary: str = ""
    requested_action: str = ""
    confidence: float = 0.8
    required_tests: list[str] = field(default_factory=list)
    blocking: bool = False
    status: str = "open"

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "reviewer": self.reviewer,
            "category": self.category,
            "severity": self.severity,
            "claim": self.claim,
            "verdict": self.verdict,
            "evidence_refs": self.evidence_refs,
            "counterexample": self.counterexample,
            "reasoning_summary": self.reasoning_summary,
            "requested_action": self.requested_action,
            "confidence": self.confidence,
            "required_tests": self.required_tests,
            "blocking": self.blocking,
            "status": self.status,
        }


def default_blocking(severity: str, verdict: str) -> bool:
    return severity == "critical" or verdict in BLOCKING_VERDICTS


def normalize_finding(raw: dict[str, Any]) -> dict[str, Any]:
    severity = str(raw.get("severity", "")).strip().lower()
    verdict = str(raw.get("verdict", "")).strip().lower()
    if severity not in SEVERITIES:
        raise ValueError(f"Unknown severity: {severity}")
    if verdict not in FINDING_VERDICTS:
        raise ValueError(f"Unknown finding verdict: {verdict}")
    blocking = raw.get("blocking")
    if blocking is None:
        blocking = default_blocking(severity, verdict)
    return ReviewFinding(
        finding_id=str(raw.get("finding_id", "")).strip(),
        reviewer=str(raw.get("reviewer", "")).strip(),
        category=str(raw.get("category", "")).strip() or "other",
        severity=severity,
        claim=str(raw.get("claim", "")).strip(),
        verdict=verdict,
        evidence_refs=[str(item) for item in raw.get("evidence_refs", [])],
        counterexample=str(raw.get("counterexample", "")).strip(),
        reasoning_summary=str(raw.get("reasoning_summary", "")).strip(),
        requested_action=str(raw.get("requested_action", "")).strip(),
        confidence=float(raw.get("confidence", 0.8)),
        required_tests=[str(item) for item in raw.get("required_tests", [])],
        blocking=bool(blocking),
        status=str(raw.get("status", "open")).strip() or "open",
    ).to_dict()
