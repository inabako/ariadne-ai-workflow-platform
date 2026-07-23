from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReviewerRule:
    reviewer: str
    keywords: tuple[str, ...]
    reason: str


REVIEWER_RULES = (
    ReviewerRule(
        "security",
        (
            "auth",
            "authorization",
            "authentication",
            "credential",
            "secret",
            "token",
            "permission",
            "remote",
            "github",
            "scm",
        ),
        "security, authorization, credential, or remote mutation risk is present",
    ),
    ReviewerRule(
        "safety",
        ("stop", "emergency", "motor", "robot", "sensor", "power", "drive", "control", "unsafe"),
        "safety-critical control or physical operation assumptions may be affected",
    ),
    ReviewerRule(
        "network",
        ("network", "tcp", "udp", "quic", "websocket", "port", "vpn", "tls", "firewall", "nat", "relay"),
        "network boundary, protocol, or exposure assumptions may be affected",
    ),
    ReviewerRule(
        "runtime",
        ("runtime", "ctl", "cli", "python", "subprocess", "thread", "async", "process", "logging", "workflow"),
        "runtime behavior, process ownership, or workflow execution may be affected",
    ),
    ReviewerRule(
        "deployment",
        ("docker", "systemd", "iac", "terraform", "deploy", "windows", "linux", "msys2", "path", "powershell"),
        "deployment, platform, or environment assumptions may be affected",
    ),
    ReviewerRule(
        "observability",
        ("log", "logs", "metric", "metrics", "trace", "telemetry", "evidence", "feedback", "audit"),
        "observability, traceability, or evidence quality may be affected",
    ),
    ReviewerRule(
        "testing",
        ("test", "pytest", "coverage", "qtest", "playwright", "fault", "integration", "verification"),
        "test strategy, verification depth, or regression protection may be affected",
    ),
)


def _tokens(values: list[str]) -> set[str]:
    joined = " ".join(values).replace("\\", "/").lower()
    separators = "/:;,.()[]{}_-"
    for separator in separators:
        joined = joined.replace(separator, " ")
    return {token for token in joined.split() if token}


def select_reviewers(packet: dict[str, Any], *, explicit_reviewers: list[str] | None = None) -> dict[str, Any]:
    source_values: list[str] = []
    for key in (
        "target",
        "intent",
        "target_revision",
    ):
        value = str(packet.get(key, "")).strip()
        if value:
            source_values.append(value)
    for key in (
        "requirements",
        "changed_files",
        "guardrails",
        "evidence",
        "scope",
        "known_constraints",
    ):
        source_values.extend(str(item) for item in packet.get(key, []) if str(item).strip())

    token_set = _tokens(source_values)
    explicit = {reviewer.strip() for reviewer in explicit_reviewers or [] if reviewer.strip()}
    selections: list[dict[str, Any]] = []
    for rule in REVIEWER_RULES:
        matched = sorted(set(rule.keywords) & token_set)
        if matched or rule.reviewer in explicit:
            selections.append(
                {
                    "reviewer": rule.reviewer,
                    "reason": "explicit reviewer requested" if rule.reviewer in explicit and not matched else rule.reason,
                    "matched_terms": matched,
                    "source": "explicit" if rule.reviewer in explicit and not matched else "rule",
                }
            )

    known_reviewers = {rule.reviewer for rule in REVIEWER_RULES}
    for reviewer in sorted(explicit - known_reviewers):
        selections.append(
            {
                "reviewer": reviewer,
                "reason": "explicit reviewer requested",
                "matched_terms": [],
                "source": "explicit",
            }
        )

    if not selections:
        selections.append(
            {
                "reviewer": "runtime",
                "reason": "default runtime reviewer is required when no stronger domain signal is present",
                "matched_terms": [],
                "source": "default",
            }
        )

    required_reviewers = sorted({item["reviewer"] for item in selections})
    return {
        "required_reviewers": required_reviewers,
        "selections": sorted(selections, key=lambda item: item["reviewer"]),
        "source_terms": sorted(token_set),
    }
