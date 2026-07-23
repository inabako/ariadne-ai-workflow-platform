from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SpecialistAgentRule:
    reviewer: str
    agent_id: str
    prompt_path: str
    report_name: str
    role: str


SPECIALIST_AGENT_RULES = (
    SpecialistAgentRule(
        "security",
        "security-reviewer-agent",
        ".github/agents/security-reviewer-agent.prompt.md",
        "specialist-review-security.md",
        "Review authentication, authorization, secrets, remote access, and command authority risk.",
    ),
    SpecialistAgentRule(
        "safety",
        "safety-reviewer-agent",
        ".github/agents/safety-reviewer-agent.prompt.md",
        "specialist-review-safety.md",
        "Review STOP path, safe state, control authority, watchdog, and safety-critical assumptions.",
    ),
    SpecialistAgentRule(
        "network",
        "network-reviewer-agent",
        ".github/agents/network-reviewer-agent.prompt.md",
        "specialist-review-network.md",
        "Review network boundary, route, protocol, latency, loss, and exposure assumptions.",
    ),
    SpecialistAgentRule(
        "runtime",
        "ariadne-runtime-agent",
        ".github/agents/ariadne-runtime-agent.prompt.md",
        "specialist-review-runtime.md",
        "Review process model, lifecycle, restart, recovery, health check, and workflow execution behavior.",
    ),
    SpecialistAgentRule(
        "deployment",
        "platform-deployment-specialist-agent",
        ".github/agents/platform-deployment-specialist-agent.prompt.md",
        "specialist-review-platform-deployment.md",
        "Review platform, deployment, startup, Windows/Linux, Docker, and environment assumptions.",
    ),
    SpecialistAgentRule(
        "observability",
        "observability-reviewer-agent",
        ".github/agents/observability-reviewer-agent.prompt.md",
        "specialist-review-observability.md",
        "Review logs, metrics, traces, evidence quality, incident traceability, and audit readiness.",
    ),
    SpecialistAgentRule(
        "testing",
        "test-fault-injection-specialist-agent",
        ".github/agents/test-fault-injection-specialist-agent.prompt.md",
        "specialist-review-testing.md",
        "Review test strategy, fault injection, regression coverage, and required evidence.",
    ),
)


def agent_rule_for_reviewer(reviewer: str) -> SpecialistAgentRule | None:
    normalized = reviewer.strip().lower()
    return next((item for item in SPECIALIST_AGENT_RULES if item.reviewer == normalized), None)


def build_specialist_agent_packet(
    session: dict[str, Any],
    *,
    reviewer: str,
    prompt_exists: bool,
    handoff_path: str = "",
) -> dict[str, Any]:
    normalized = reviewer.strip().lower()
    rule = agent_rule_for_reviewer(normalized)
    agent_id = rule.agent_id if rule else f"{normalized}-reviewer-agent"
    prompt_path = rule.prompt_path if rule else ""
    report_name = rule.report_name if rule else f"specialist-review-{normalized}.md"
    packet = session.get("packet", {})
    review_id = str(session.get("review_id", ""))
    work_id = str(session.get("work_id", ""))
    output_path = Path("work") / work_id / "process-report" / report_name
    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-specialist-run",
        "status": "ready" if rule and prompt_exists else "blocked",
        "review_id": review_id,
        "work_id": work_id,
        "reviewer": normalized,
        "agent_id": agent_id,
        "prompt_path": prompt_path,
        "prompt_exists": prompt_exists,
        "handoff_path": handoff_path,
        "output_path": output_path.as_posix(),
        "role": rule.role if rule else "No specialist agent mapping is registered for this reviewer.",
        "input": {
            "target": packet.get("target", ""),
            "target_revision": packet.get("target_revision", ""),
            "intent": packet.get("intent", ""),
            "requirements": packet.get("requirements", []),
            "changed_files": packet.get("changed_files", []),
            "guardrails": packet.get("guardrails", []),
            "evidence": packet.get("evidence", []),
            "scope": packet.get("scope", []),
            "known_constraints": packet.get("known_constraints", []),
        },
        "required_output": {
            "review_report": output_path.as_posix(),
            "finding_registration_command": (
                f"aiwfctl review add-finding --review-id {review_id} --reviewer {normalized} "
                "--category <category> --severity <severity> --claim \"<claim>\" --verdict <verdict> "
                f"--evidence-ref {output_path.as_posix()}"
            ),
        },
        "blocked_reason": "" if rule and prompt_exists else "specialist_agent_prompt_missing_or_unmapped",
    }
