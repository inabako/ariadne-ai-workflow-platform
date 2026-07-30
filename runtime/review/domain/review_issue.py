from __future__ import annotations

from typing import Any

from runtime.review.constants import (
    DEFAULT_REVIEW_ISSUE_SEVERITY,
    REVIEW_ISSUE_ID_WIDTH,
    REVIEW_ISSUE_SEVERITY_RANK,
    REVIEW_ISSUE_SEVERITY_RANK_DEFAULT,
)


def issue_severity(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return DEFAULT_REVIEW_ISSUE_SEVERITY
    return max(
        (str(item.get("severity", DEFAULT_REVIEW_ISSUE_SEVERITY)) for item in findings),
        key=lambda value: REVIEW_ISSUE_SEVERITY_RANK.get(value, REVIEW_ISSUE_SEVERITY_RANK_DEFAULT),
    )


def build_review_issues(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for finding in findings:
        if str(finding.get("verdict", "")).lower() == "pass":
            continue
        if str(finding.get("status", "open")) not in {"open", "accepted-risk"}:
            continue
        claim = str(finding.get("claim", "")).strip().lower()
        category = str(finding.get("category", "other")).strip().lower()
        grouped.setdefault((category, claim), []).append(finding)

    issues = []
    for index, ((category, claim), grouped_findings) in enumerate(sorted(grouped.items()), start=1):
        severity = issue_severity(grouped_findings)
        blocking = any(bool(item.get("blocking")) for item in grouped_findings)
        issues.append(
            {
                "issue_id": f"RI-{index:0{REVIEW_ISSUE_ID_WIDTH}d}",
                "category": category,
                "claim": claim,
                "severity": severity,
                "blocking": blocking,
                "status": "open",
                "finding_ids": [str(item.get("finding_id", "")) for item in grouped_findings],
                "reviewer_positions": [
                    {
                        "reviewer": item.get("reviewer", ""),
                        "verdict": item.get("verdict", ""),
                        "requested_action": item.get("requested_action", ""),
                    }
                    for item in grouped_findings
                ],
                "required_evidence": sorted(
                    {
                        evidence
                        for item in grouped_findings
                        for evidence in item.get("evidence_refs", [])
                        if str(evidence).strip()
                    }
                ),
                "required_tests": sorted(
                    {
                        test
                        for item in grouped_findings
                        for test in item.get("required_tests", [])
                        if str(test).strip()
                    }
                ),
            }
        )
    return issues
