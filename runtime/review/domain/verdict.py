from __future__ import annotations

from runtime.constants.runtime_values import SCHEMA_VERSION


from typing import Any


FINAL_VERDICTS = (
    "APPROVED",
    "APPROVED_WITH_RISK",
    "CHANGES_REQUIRED",
    "HUMAN_DECISION_REQUIRED",
    "REJECTED",
)


def decide(
    session: dict[str, Any],
    *,
    evidence_verified: bool,
    challenge_completed: bool,
    target_revision_consistent: bool,
    human_check: str = "pending",
) -> dict[str, Any]:
    findings = session.get("findings", [])
    issues = session.get("issues", [])
    packet = session.get("packet", {})
    required_reviewers = {str(item) for item in packet.get("required_reviewers", []) if str(item).strip()}
    completed_reviewers = {str(item.get("reviewer", "")) for item in findings if str(item.get("reviewer", "")).strip()}
    missing_reviewers = sorted(required_reviewers - completed_reviewers)

    blocking_issues = [item for item in issues if item.get("blocking") and item.get("status") == "open"]
    unresolved_high_issues = [
        item for item in issues if item.get("severity") in {"critical", "high"} and item.get("status") == "open"
    ]
    unsupported_required_claims = [
        item for item in findings if item.get("verdict") == "unsupported" and item.get("status") == "open"
    ]
    challenge_blockers = [
        item
        for item in session.get("challenge_rounds", [])
        if item.get("counterexample_found") and item.get("status") in {"completed", "human-check-required"}
    ]
    unresolved_nonblocking = [
        item
        for item in issues
        if item.get("status") == "open" and not item.get("blocking") and item.get("severity") not in {"critical", "high"}
    ]

    checks = {
        "blocking_issues": len(blocking_issues),
        "unresolved_high_issues": len(unresolved_high_issues),
        "unsupported_required_claims": len(unsupported_required_claims),
        "missing_required_reviewers": len(missing_reviewers),
        "evidence_verified": evidence_verified,
        "challenge_completed": challenge_completed,
        "target_revision_consistent": target_revision_consistent,
        "challenge_blockers": len(challenge_blockers),
    }

    reasons: list[str] = []
    if missing_reviewers:
        reasons.append("required reviewers have not produced structured findings")
    if unsupported_required_claims:
        reasons.append("unsupported required claims remain")
    if blocking_issues:
        reasons.append("blocking review issues remain open")
    if unresolved_high_issues:
        reasons.append("high or critical review issues remain open")
    if not evidence_verified:
        reasons.append("evidence gate has not been verified")
    if not challenge_completed:
        reasons.append("challenge round has not been completed")
    if not target_revision_consistent:
        reasons.append("target revision changed after review packet freeze")
    if challenge_blockers:
        reasons.append("challenge round found counterexamples that require review")

    if missing_reviewers or unsupported_required_claims:
        verdict = "HUMAN_DECISION_REQUIRED"
    elif blocking_issues:
        verdict = "CHANGES_REQUIRED"
    elif unresolved_high_issues:
        verdict = "HUMAN_DECISION_REQUIRED"
    elif not evidence_verified or not challenge_completed or not target_revision_consistent or challenge_blockers:
        verdict = "HUMAN_DECISION_REQUIRED"
    elif unresolved_nonblocking:
        if human_check == "approved":
            verdict = "APPROVED_WITH_RISK"
            reasons.append("non-blocking risks were accepted by human check")
        else:
            verdict = "HUMAN_DECISION_REQUIRED"
            reasons.append("non-blocking risk acceptance requires human check")
    else:
        verdict = "APPROVED"
        reasons.append("all review council approval checks passed")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "review-council-verdict",
        "verdict": verdict,
        "checks": checks,
        "missing_required_reviewers": missing_reviewers,
        "blocking_issue_ids": [str(item.get("issue_id", "")) for item in blocking_issues],
        "unresolved_high_issue_ids": [str(item.get("issue_id", "")) for item in unresolved_high_issues],
        "reason": "; ".join(reasons),
        "human_check": human_check,
    }
