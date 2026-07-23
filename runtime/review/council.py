from __future__ import annotations

import argparse
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from runtime.common import local_timestamp, read_json, relative_to_repo, slugify, utc_now_iso, write_json, write_markdown
from runtime.common import gate_restart
from runtime.constants.paths import (
    DUCKDB_INGESTION_EVIDENCE_DIR,
    DUCKDB_MIGRATION_EVIDENCE,
    EMBEDDINGS_INDEX,
    GENERATED_CHUNKS,
    GENERATED_INDEXES,
    GENERATED_NORMALIZED,
    GENERATED_OPTIMIZED_CHUNKS,
    RAG_BUILD_RUN_LATEST,
    RAG_INGESTION_POLICY_PATH,
    SOURCE_REVIEW_COUNCIL,
)
from runtime.constants.schemas import REVIEW_COUNCIL_RAG_BUILD_SCHEMA
from runtime.constants.schemas import REVIEW_COUNCIL_SPECIALIST_EXECUTION_SCHEMA
from runtime.observability.logger import RuntimeEventLogger
from runtime.rag import rag_build
from runtime.review.domain.finding import normalize_finding
from runtime.review.domain.review_issue import build_review_issues
from runtime.review.domain.review_packet import ReviewPacket, packet_hash
from runtime.review.domain.reviewer_selection import select_reviewers
from runtime.review.domain.specialist_agent import build_specialist_agent_packet
from runtime.review.domain.verdict import decide
from runtime.review.graph import build_langgraph_review_plan, evaluate_langgraph_review_state
from runtime.review.persistence.store import ReviewStore
from runtime.workflow import human_gate_policy


FINDING_HEADING_RE = re.compile(r"^\s{0,3}#{2,6}\s+.*(?:finding|review finding|指摘|レビュー指摘)", re.IGNORECASE)

FINDING_LABEL_ALIASES = {
    "category": ("category", "カテゴリ", "分類"),
    "severity": ("severity", "重大度", "重要度"),
    "claim": ("claim", "指摘", "内容", "主張"),
    "verdict": ("verdict", "判定", "結論"),
    "evidence_refs": ("evidence", "evidence_ref", "evidence refs", "証跡", "根拠"),
    "counterexample": ("counterexample", "反例"),
    "reasoning_summary": ("reasoning", "reason", "reasoning summary", "理由", "判断理由"),
    "requested_action": ("requested action", "requested_action", "対応", "要求対応", "是正"),
    "confidence": ("confidence", "確信度"),
    "required_tests": ("required test", "required tests", "required_test", "required_tests", "必要テスト"),
    "blocking": ("blocking", "block", "ブロック", "致命的"),
}

FINDING_LABEL_LOOKUP = {
    alias.lower(): key
    for key, aliases in FINDING_LABEL_ALIASES.items()
    for alias in aliases
}

REVIEW_HUMAN_GATE_DEFAULTS = {
    "review-council-final-verdict": {
        "id": "review-council-final-verdict",
        "label": "Review Council final verdict",
        "requires_human_check": True,
        "approved_value": "approved",
        "reason": "Final review verdict affects downstream implementation, release, and knowledge capture decisions.",
    },
    "review-council-risk-acceptance": {
        "id": "review-council-risk-acceptance",
        "label": "Review Council non-blocking risk acceptance",
        "requires_human_check": True,
        "approved_value": "approved",
        "reason": "Non-blocking review issues must be explicitly accepted before approval-with-risk.",
    },
    "review-council-counterexample": {
        "id": "review-council-counterexample",
        "label": "Review Council counterexample decision",
        "requires_human_check": True,
        "approved_value": "approved",
        "reason": "A surviving counterexample changes whether the review can proceed.",
    },
}


def _list_arg(args: argparse.Namespace, name: str) -> list[str]:
    return [str(item) for item in getattr(args, name, []) if str(item).strip()]


def _current_git_revision(repo_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=True,
        )
    except Exception:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _review_id() -> str:
    return f"review-{local_timestamp()}"


def _gate_restart(review_id: str, status: str) -> dict[str, Any]:
    if status in {"approved", "approved-with-risk"}:
        return gate_restart.build_gate_restart(
            "review-council-gate",
            restart_reason="review-council-approved",
            status_after_restart="pass",
        )
    if status == "rejected":
        return gate_restart.build_gate_restart(
            "review-council-gate",
            restart_reason="review-council-rejected",
            status_after_restart="fail",
        )
    return gate_restart.build_gate_restart(
        "review-council-gate",
        restart_reason="review-council",
        repair_available=True,
        repair_command=f"aiwfctl review status --review-id {review_id}",
        status_after_restart="unknown",
    )


def _log(repo_root: Path, event: str, **payload: Any) -> None:
    RuntimeEventLogger(repo_root=repo_root, component="review").emit(event, **payload)


def _path_check(repo_root: Path, value: str, *, kind: str = "file") -> dict[str, Any]:
    path = _resolve_path(repo_root, value)
    exists = path.exists()
    is_file = path.is_file()
    return {
        "path": value,
        "kind": kind,
        "exists": exists,
        "is_file": is_file,
        "size": path.stat().st_size if exists and is_file else 0,
    }


def _session_markdown(session: dict[str, Any]) -> str:
    packet = session.get("packet", {})
    verdict = session.get("verdict") or {}
    lines = [
        "# Ariadne Review Council Session",
        "",
        f"Review ID: `{session.get('review_id', '')}`",
        f"Work ID: `{session.get('work_id', '')}`",
        f"Status: `{session.get('status', '')}`",
        f"Target: `{packet.get('target', '')}`",
        f"Target Revision: `{packet.get('target_revision', '')}`",
        f"Packet Hash: `{session.get('packet_hash', '')}`",
        "",
        "## Intent",
        "",
        str(packet.get("intent", "")),
        "",
        "## Findings",
        "",
    ]
    findings = session.get("findings", [])
    if findings:
        lines.append("| ID | Reviewer | Severity | Verdict | Claim |")
        lines.append("| --- | --- | --- | --- | --- |")
        for item in findings:
            lines.append(
                f"| {item.get('finding_id', '')} | {item.get('reviewer', '')} | {item.get('severity', '')} | {item.get('verdict', '')} | {item.get('claim', '')} |"
            )
    else:
        lines.append("No structured findings have been registered.")
    lines.extend(["", "## Review Issues", ""])
    issues = session.get("issues", [])
    if issues:
        lines.append("| ID | Severity | Blocking | Claim |")
        lines.append("| --- | --- | --- | --- |")
        for item in issues:
            lines.append(
                f"| {item.get('issue_id', '')} | {item.get('severity', '')} | {str(item.get('blocking', False)).lower()} | {item.get('claim', '')} |"
            )
    else:
        lines.append("No review issues are open.")
    lines.extend(["", "## Verdict", "", f"`{verdict.get('verdict', 'not-decided')}`"])
    if verdict.get("reason"):
        lines.extend(["", verdict["reason"]])
    evidence_gate = session.get("evidence_gate")
    if isinstance(evidence_gate, dict):
        lines.extend(
            [
                "",
                "## Evidence Gate",
                "",
                f"Status: `{evidence_gate.get('status', '')}`",
                f"Missing Evidence: `{len(evidence_gate.get('missing_evidence', []))}`",
                f"Missing Required Tests: `{len(evidence_gate.get('missing_required_tests', []))}`",
            ]
        )
    challenge_rounds = session.get("challenge_rounds", [])
    if challenge_rounds:
        lines.extend(["", "## Challenge Rounds", ""])
        for item in challenge_rounds:
            lines.append(
                f"- `{item.get('challenge_id', '')}` {item.get('status', '')}: {item.get('summary', '')}"
            )
    return "\n".join(lines)


def _write_report(repo_root: Path, session: dict[str, Any]) -> str:
    store = ReviewStore(repo_root)
    report_dir = store.process_report_dir(session["work_id"])
    report_path = report_dir / f"review-council-{session['review_id']}.md"
    write_markdown(report_path, _session_markdown(session))
    return relative_to_repo(repo_root, report_path)


def _save_session(repo_root: Path, session: dict[str, Any]) -> dict[str, str]:
    session["updated_at"] = utc_now_iso()
    session["issues"] = build_review_issues(session.get("findings", []))
    session["gate_restart"] = _gate_restart(session["review_id"], session.get("status", "reviewing"))
    artifacts = ReviewStore(repo_root).save(session)
    artifacts["report"] = _write_report(repo_root, session)
    session["artifacts"] = artifacts
    ReviewStore(repo_root).save(session)
    return artifacts


def _packet_from_args(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    target_revision = getattr(args, "target_revision", "") or _current_git_revision(repo_root)
    packet_model = ReviewPacket(
        work_id=args.work_id,
        target=getattr(args, "target", ""),
        target_revision=target_revision,
        intent=args.intent,
        requirements=_list_arg(args, "requirement"),
        changed_files=_list_arg(args, "changed_file"),
        guardrails=_list_arg(args, "guardrail"),
        evidence=_list_arg(args, "evidence"),
        scope=_list_arg(args, "scope"),
        known_constraints=_list_arg(args, "known_constraint"),
        required_reviewers=_list_arg(args, "reviewer"),
    )
    return packet_model.to_dict()


def _command_value(value: str) -> str:
    return '"' + value.replace('"', '\\"') + '"'


def _append_command_args(parts: list[str], flag: str, values: list[str]) -> None:
    for value in values:
        parts.extend([flag, _command_value(value)])


def _split_inline_values(value: str) -> list[str]:
    normalized = value.strip().strip("[]")
    if not normalized:
        return []
    return [item.strip().strip("\"'`") for item in re.split(r"[,;、；]\s*", normalized) if item.strip()]


def _bool_from_text(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized in {"true", "yes", "y", "1", "blocking", "block", "blocked", "あり", "有", "はい", "致命的"}:
        return True
    if normalized in {"false", "no", "n", "0", "non-blocking", "non_blocking", "なし", "無", "いいえ"}:
        return False
    return None


def _coerce_choice(value: str, choices: tuple[str, ...], default: str) -> str:
    normalized = value.strip().lower()
    return normalized if normalized in choices else default


def _coerce_float(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _split_finding_sections(text: str) -> list[str]:
    sections: list[list[str]] = []
    current: list[str] = []
    matched_heading = False
    for line in text.splitlines():
        if FINDING_HEADING_RE.search(line):
            if current and any(item.strip() for item in current):
                sections.append(current)
            current = [line]
            matched_heading = True
            continue
        if matched_heading:
            current.append(line)
    if matched_heading and current and any(item.strip() for item in current):
        sections.append(current)
    return ["\n".join(section).strip() for section in sections if "\n".join(section).strip()] or [text.strip()]


def _extract_finding_labels(section: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in section.splitlines():
        match = re.match(r"^\s*(?:[-*]\s*)?`?([^`:：]+?)`?\s*[:：]\s*(.+?)\s*$", line)
        if not match:
            continue
        label = match.group(1).strip().strip("*_`").lower()
        key = FINDING_LABEL_LOOKUP.get(label)
        if key:
            values[key] = match.group(2).strip()
    return values


def _fallback_claim(section: str) -> str:
    paragraph: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if paragraph:
                break
            continue
        label_match = re.match(r"^\s*(?:[-*]\s*)?`?([^`:：]+?)`?\s*[:：]", stripped)
        if label_match and FINDING_LABEL_LOOKUP.get(label_match.group(1).strip().strip("*_`").lower()):
            continue
        paragraph.append(stripped.lstrip("-* "))
    return " ".join(paragraph).strip() or "Specialist report requires human triage."


def _finding_registration_command(session: dict[str, Any], draft: dict[str, Any]) -> str:
    parts = [
        "aiwfctl",
        "review",
        "add-finding",
        "--review-id",
        _command_value(str(session.get("review_id", ""))),
        "--reviewer",
        _command_value(str(draft.get("reviewer", ""))),
        "--category",
        _command_value(str(draft.get("category", ""))),
        "--severity",
        str(draft.get("severity", "")),
        "--claim",
        _command_value(str(draft.get("claim", ""))),
        "--verdict",
        str(draft.get("verdict", "")),
    ]
    _append_command_args(parts, "--evidence-ref", [str(item) for item in draft.get("evidence_refs", [])])
    if draft.get("counterexample"):
        parts.extend(["--counterexample", _command_value(str(draft["counterexample"]))])
    if draft.get("reasoning_summary"):
        parts.extend(["--reasoning-summary", _command_value(str(draft["reasoning_summary"]))])
    if draft.get("requested_action"):
        parts.extend(["--requested-action", _command_value(str(draft["requested_action"]))])
    parts.extend(["--confidence", str(draft.get("confidence", 0.8))])
    _append_command_args(parts, "--required-test", [str(item) for item in draft.get("required_tests", [])])
    parts.append("--blocking" if draft.get("blocking") else "--non-blocking")
    return " ".join(parts)


def _finding_draft_from_section(
    session: dict[str, Any],
    section: str,
    *,
    draft_id: str,
    reviewer: str,
    default_category: str,
    default_severity: str,
    default_verdict: str,
) -> dict[str, Any]:
    values = _extract_finding_labels(section)
    blocking = _bool_from_text(values.get("blocking", ""))
    raw = {
        "finding_id": draft_id,
        "reviewer": reviewer,
        "category": values.get("category", default_category),
        "severity": _coerce_choice(values.get("severity", ""), ("critical", "high", "medium", "low", "info"), default_severity),
        "claim": values.get("claim", "") or _fallback_claim(section),
        "verdict": _coerce_choice(
            values.get("verdict", ""),
            ("pass", "warn", "fail", "unsupported", "needs-qa", "changes-required"),
            default_verdict,
        ),
        "evidence_refs": _split_inline_values(values.get("evidence_refs", "")),
        "counterexample": values.get("counterexample", ""),
        "reasoning_summary": values.get("reasoning_summary", ""),
        "requested_action": values.get("requested_action", ""),
        "confidence": _coerce_float(values.get("confidence", ""), 0.8),
        "required_tests": _split_inline_values(values.get("required_tests", "")),
        "blocking": blocking,
    }
    finding = normalize_finding(raw)
    draft = {"draft_id": finding.pop("finding_id"), **finding}
    draft["registration_command"] = _finding_registration_command(session, draft)
    return draft


def _finding_draft_markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Review Council Finding Draft",
        "",
        f"Review ID: `{record.get('review_id', '')}`",
        f"Work ID: `{record.get('work_id', '')}`",
        f"Reviewer: `{record.get('reviewer', '')}`",
        f"Source Report: `{record.get('source_report', '')}`",
        "",
        "## Draft Findings",
        "",
    ]
    drafts = record.get("drafts", [])
    if not drafts:
        lines.append("- none")
    for draft in drafts:
        lines.extend(
            [
                f"### {draft.get('draft_id', '')}",
                "",
                f"- Severity: `{draft.get('severity', '')}`",
                f"- Verdict: `{draft.get('verdict', '')}`",
                f"- Blocking: `{str(draft.get('blocking', False)).lower()}`",
                f"- Claim: {draft.get('claim', '')}",
                "",
                "```powershell",
                str(draft.get("registration_command", "")),
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _reviewer_summary(session: dict[str, Any]) -> list[dict[str, Any]]:
    required = [str(item) for item in session.get("packet", {}).get("required_reviewers", [])]
    findings = session.get("findings", [])
    drafts = session.get("finding_drafts", [])
    specialist_runs = session.get("specialist_runs", [])
    handoffs = [str(item) for item in session.get("reviewer_handoffs", [])]
    reviewers = sorted(
        dict.fromkeys(
            [
                *required,
                *[str(item.get("reviewer", "")) for item in findings],
                *[str(item.get("reviewer", "")) for item in drafts],
                *[str(item.get("reviewer", "")) for item in specialist_runs],
            ]
        )
    )
    summary: list[dict[str, Any]] = []
    for reviewer in reviewers:
        reviewer_findings = [item for item in findings if str(item.get("reviewer", "")) == reviewer]
        reviewer_draft_count = sum(
            int(item.get("draft_count", 0)) for item in drafts if str(item.get("reviewer", "")) == reviewer
        )
        run = next((item for item in reversed(specialist_runs) if str(item.get("reviewer", "")) == reviewer), {})
        handoff_path = next((item for item in handoffs if f"-{reviewer}." in item or f"-{reviewer}/" in item), "")
        state = "completed" if reviewer_findings else "pending"
        if not reviewer_findings and reviewer_draft_count:
            state = "draft-ready"
        elif not reviewer_findings and run:
            state = str(run.get("status", "specialist-ready"))
        elif not reviewer_findings and handoff_path:
            state = "handoff-ready"
        summary.append(
            {
                "reviewer": reviewer,
                "required": reviewer in required,
                "state": state,
                "finding_count": len(reviewer_findings),
                "draft_count": reviewer_draft_count,
                "latest_specialist_run_status": str(run.get("status", "")) if run else "",
                "handoff_path": handoff_path,
            }
        )
    return summary


def _review_summary_record(session: dict[str, Any]) -> dict[str, Any]:
    findings = session.get("findings", [])
    issues = session.get("issues", [])
    evidence_gate = session.get("evidence_gate") or {}
    verdict = session.get("verdict") or {}
    reviewer_summary = _reviewer_summary(session)
    completed_reviewers = [
        item["reviewer"] for item in reviewer_summary if item.get("required") and int(item.get("finding_count", 0)) > 0
    ]
    required_reviewers = [str(item) for item in session.get("packet", {}).get("required_reviewers", [])]
    latest_run = (session.get("orchestration") or {}).get("latest_run")
    run = latest_run if isinstance(latest_run, dict) else evaluate_langgraph_review_state(session, run_id="summary")
    next_actions = [_operational_action(item, str(session.get("review_id", ""))) for item in run.get("next_actions", [])]
    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-summary",
        "status": "summarized",
        "review_id": session.get("review_id", ""),
        "work_id": session.get("work_id", ""),
        "created_at": utc_now_iso(),
        "snapshot": {
            "session_status": session.get("status", ""),
            "target": session.get("packet", {}).get("target", ""),
            "target_revision": session.get("packet", {}).get("target_revision", ""),
            "packet_hash": session.get("packet_hash", ""),
            "required_reviewers": required_reviewers,
            "completed_reviewers": completed_reviewers,
            "missing_reviewers": [item for item in required_reviewers if item not in completed_reviewers],
            "specialist_execution_count": len(session.get("specialist_executions", [])),
            "finding_draft_count": sum(int(item.get("draft_count", 0)) for item in session.get("finding_drafts", [])),
            "finding_count": len(findings),
            "issue_count": len(issues),
            "open_issue_count": len([item for item in issues if item.get("status") == "open"]),
            "blocking_issue_count": len([item for item in issues if item.get("status") == "open" and item.get("blocking")]),
            "challenge_count": len(session.get("challenge_rounds", [])),
            "reinspection_count": len(session.get("reinspections", [])),
            "human_gate_count": len(session.get("human_gates", [])),
            "human_check": session.get("human_check", ""),
            "challenge_completed": bool(session.get("challenge_completed", False)),
            "evidence_verified": bool(session.get("evidence_verified", False)),
            "evidence_gate_status": evidence_gate.get("status", ""),
            "verdict": verdict.get("verdict", ""),
        },
        "reviewers": reviewer_summary,
        "findings": [
            {
                "finding_id": item.get("finding_id", ""),
                "reviewer": item.get("reviewer", ""),
                "category": item.get("category", ""),
                "severity": item.get("severity", ""),
                "verdict": item.get("verdict", ""),
                "blocking": bool(item.get("blocking", False)),
                "status": item.get("status", ""),
                "claim": item.get("claim", ""),
                "requested_action": item.get("requested_action", ""),
                "evidence_refs": item.get("evidence_refs", []),
                "required_tests": item.get("required_tests", []),
            }
            for item in findings
        ],
        "issues": [
            {
                "issue_id": item.get("issue_id", ""),
                "category": item.get("category", ""),
                "severity": item.get("severity", ""),
                "blocking": bool(item.get("blocking", False)),
                "status": item.get("status", ""),
                "claim": item.get("claim", ""),
                "finding_ids": item.get("finding_ids", []),
                "required_evidence": item.get("required_evidence", []),
                "required_tests": item.get("required_tests", []),
            }
            for item in issues
        ],
        "gates": {
            "challenge_completed": bool(session.get("challenge_completed", False)),
            "evidence_verified": bool(session.get("evidence_verified", False)),
            "evidence_gate_status": evidence_gate.get("status", ""),
            "missing_evidence": evidence_gate.get("missing_evidence", []),
            "missing_required_tests": evidence_gate.get("missing_required_tests", []),
            "missing_artifacts": evidence_gate.get("missing_artifacts", []),
        },
        "verdict": verdict,
        "next_actions": next_actions,
        "selected_action": next_actions[0] if next_actions else None,
    }


def _review_summary_markdown(record: dict[str, Any]) -> str:
    snapshot = record.get("snapshot", {})
    lines = [
        "# Ariadne Review Council Summary",
        "",
        f"Review ID: `{record.get('review_id', '')}`",
        f"Work ID: `{record.get('work_id', '')}`",
        f"Session Status: `{snapshot.get('session_status', '')}`",
        f"Verdict: `{snapshot.get('verdict', '') or 'not-decided'}`",
        "",
        "## Snapshot",
        "",
        "| Item | Value |",
        "| --- | --- |",
    ]
    for key in [
        "target",
        "target_revision",
        "packet_hash",
        "specialist_execution_count",
        "finding_draft_count",
        "finding_count",
        "issue_count",
        "open_issue_count",
        "blocking_issue_count",
        "challenge_completed",
        "evidence_verified",
        "human_gate_count",
        "human_check",
        "evidence_gate_status",
    ]:
        lines.append(f"| {_md_cell(key)} | {_md_cell(snapshot.get(key, ''))} |")
    lines.extend(["", "## Reviewers", "", "| Reviewer | Required | State | Findings | Drafts |", "| --- | --- | --- | ---: | ---: |"])
    for item in record.get("reviewers", []):
        lines.append(
            f"| {_md_cell(item.get('reviewer', ''))} | {_md_cell(str(item.get('required', False)).lower())} | {_md_cell(item.get('state', ''))} | {int(item.get('finding_count', 0))} | {int(item.get('draft_count', 0))} |"
        )
    lines.extend(["", "## Open Issues", ""])
    open_issues = [item for item in record.get("issues", []) if item.get("status") == "open"]
    if open_issues:
        lines.append("| ID | Severity | Blocking | Claim |")
        lines.append("| --- | --- | --- | --- |")
        for item in open_issues:
            lines.append(
                f"| {_md_cell(item.get('issue_id', ''))} | {_md_cell(item.get('severity', ''))} | {_md_cell(str(item.get('blocking', False)).lower())} | {_md_cell(item.get('claim', ''))} |"
            )
    else:
        lines.append("No open review issues.")
    lines.extend(["", "## Next Actions", ""])
    next_actions = record.get("next_actions", [])
    if next_actions:
        for item in next_actions:
            command = item.get("agent_command") or item.get("command", "")
            lines.extend([f"- `{item.get('action', '')}`: {item.get('reason', '')}", "", "```powershell", str(command), "```", ""])
    else:
        lines.append("No next action is required.")
    return "\n".join(lines).rstrip() + "\n"


def _review_gate_definition(repo_root: Path, gate_id: str) -> dict[str, Any]:
    registry = human_gate_policy.load_registry(repo_root)
    try:
        return human_gate_policy.find_gate(registry, gate_id)
    except KeyError:
        if gate_id in REVIEW_HUMAN_GATE_DEFAULTS:
            return dict(REVIEW_HUMAN_GATE_DEFAULTS[gate_id])
        raise


def _latest_summary_artifacts(session: dict[str, Any]) -> dict[str, Any]:
    summaries = session.get("review_summaries", [])
    if not summaries:
        return {}
    latest = summaries[-1]
    return latest.get("artifacts", {}) if isinstance(latest, dict) else {}


def _latest_approved_human_gate(session: dict[str, Any], gate_id: str) -> dict[str, Any] | None:
    for item in reversed(session.get("human_gates", [])):
        if str(item.get("gate", "")) == gate_id and item.get("status") == "approved":
            return item
    return None


def _review_human_gate_markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Review Council Human Gate",
        "",
        f"Review ID: `{record.get('review_id', '')}`",
        f"Work ID: `{record.get('work_id', '')}`",
        f"Gate: `{record.get('gate', '')}`",
        f"Status: `{record.get('status', '')}`",
        f"Actual: `{record.get('actual', '')}`",
        f"Required: `{record.get('required', '')}`",
        "",
        "## Reason",
        "",
        str(record.get("reason", "")),
        "",
        "## Decision",
        "",
        f"Reviewer: `{record.get('reviewer', '')}`",
        "",
        str(record.get("decision_reason", "")) or "No decision reason was provided.",
        "",
        "## Review Summary",
        "",
    ]
    summary_artifacts = record.get("summary_artifacts", {})
    if summary_artifacts:
        lines.extend(f"- `{key}`: `{value}`" for key, value in summary_artifacts.items())
    else:
        lines.append("- none")
    if record.get("repair_command"):
        lines.extend(["", "## Repair Command", "", "```powershell", str(record["repair_command"]), "```"])
    return "\n".join(lines).rstrip() + "\n"


def _review_start_command(packet: dict[str, Any], review_id: str) -> str:
    parts = ["aiwfctl", "review", "start", "--work-id", _command_value(str(packet.get("work_id", "")))]
    if review_id:
        parts.extend(["--review-id", _command_value(review_id)])
    if packet.get("target"):
        parts.extend(["--target", _command_value(str(packet["target"]))])
    if packet.get("target_revision"):
        parts.extend(["--target-revision", _command_value(str(packet["target_revision"]))])
    parts.extend(["--intent", _command_value(str(packet.get("intent", "")))])
    _append_command_args(parts, "--requirement", [str(item) for item in packet.get("requirements", [])])
    _append_command_args(parts, "--changed-file", [str(item) for item in packet.get("changed_files", [])])
    _append_command_args(parts, "--guardrail", [str(item) for item in packet.get("guardrails", [])])
    _append_command_args(parts, "--evidence", [str(item) for item in packet.get("evidence", [])])
    _append_command_args(parts, "--scope", [str(item) for item in packet.get("scope", [])])
    _append_command_args(parts, "--known-constraint", [str(item) for item in packet.get("known_constraints", [])])
    _append_command_args(parts, "--reviewer", [str(item) for item in packet.get("required_reviewers", [])])
    return " ".join(parts)


def _review_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Ariadne Review Council Plan",
        "",
        f"Work ID: `{plan.get('work_id', '')}`",
        f"Status: `{plan.get('status', '')}`",
        f"Target: `{plan.get('packet', {}).get('target', '')}`",
        "",
        "## Intent",
        "",
        str(plan.get("packet", {}).get("intent", "")),
        "",
        "## Required Reviewers",
        "",
    ]
    for reviewer in plan.get("required_reviewers", []):
        selection = next((item for item in plan.get("reviewer_selection", []) if item.get("reviewer") == reviewer), {})
        lines.append(f"- `{reviewer}`: {selection.get('reason', '')}")
    lines.extend(["", "## Start Command", "", "```powershell", plan.get("start_command", ""), "```"])
    return "\n".join(lines)


def plan_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    packet = _packet_from_args(args, repo_root)
    selection = select_reviewers(packet, explicit_reviewers=_list_arg(args, "reviewer"))
    packet["required_reviewers"] = selection["required_reviewers"]
    review_id = getattr(args, "review_id", "") or _review_id()
    start_command = _review_start_command(packet, review_id)
    plan = {
        "schema_version": "1.0",
        "artifact_type": "review-council-plan",
        "status": "planned",
        "created_at": utc_now_iso(),
        "review_id": review_id,
        "work_id": args.work_id,
        "packet": packet,
        "packet_hash": packet_hash(packet),
        "required_reviewers": selection["required_reviewers"],
        "reviewer_selection": selection["selections"],
        "source_terms": selection["source_terms"],
        "start_command": start_command,
    }
    report_dir = ReviewStore(repo_root).process_report_dir(args.work_id)
    stamp = local_timestamp()
    json_path = report_dir / f"review-council-plan-{stamp}.json"
    md_path = report_dir / f"review-council-plan-{stamp}.md"
    plan["artifacts"] = {
        "plan_json": relative_to_repo(repo_root, json_path),
        "plan_report": relative_to_repo(repo_root, md_path),
    }
    write_json(json_path, plan)
    write_markdown(md_path, _review_plan_markdown(plan))
    _log(
        repo_root,
        "review_plan_created",
        review_id=review_id,
        work_id=args.work_id,
        output={"required_reviewers": selection["required_reviewers"]},
    )
    return plan


def start_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    packet = _packet_from_args(args, repo_root)
    if not packet.get("required_reviewers"):
        selection = select_reviewers(packet)
        packet["required_reviewers"] = selection["required_reviewers"]
    review_id = getattr(args, "review_id", "") or _review_id()
    session = {
        "schema_version": "1.0",
        "artifact_type": "review-council-session",
        "review_id": review_id,
        "work_id": args.work_id,
        "status": "packet-frozen",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "packet": packet,
        "packet_hash": packet_hash(packet),
        "findings": [],
        "issues": [],
        "challenge_rounds": [],
        "reinspections": [],
        "evidence_gate": None,
        "challenge_completed": False,
        "evidence_verified": False,
        "verdict": None,
        "orchestration": {
            "langgraph": build_langgraph_review_plan(
                {
                    "review_id": review_id,
                    "work_id": args.work_id,
                    "packet": packet,
                }
            )
        },
    }
    artifacts = _save_session(repo_root, session)
    _log(repo_root, "review_session_started", review_id=review_id, work_id=args.work_id, output={"status": session["status"]})
    _log(repo_root, "review_packet_frozen", review_id=review_id, work_id=args.work_id, output={"packet_hash": session["packet_hash"]})
    return {**session, "artifacts": artifacts}


def _reviewer_handoff_markdown(session: dict[str, Any], reviewer: str) -> str:
    packet = session.get("packet", {})
    lines = [
        f"# Review Council Handoff: {reviewer}",
        "",
        f"Review ID: `{session.get('review_id', '')}`",
        f"Work ID: `{session.get('work_id', '')}`",
        f"Reviewer: `{reviewer}`",
        f"Target: `{packet.get('target', '')}`",
        f"Target Revision: `{packet.get('target_revision', '')}`",
        f"Packet Hash: `{session.get('packet_hash', '')}`",
        "",
        "## Intent",
        "",
        str(packet.get("intent", "")),
        "",
        "## Scope",
        "",
    ]
    scope = packet.get("scope", []) or ["Review the packet from your specialist perspective."]
    lines.extend(f"- {item}" for item in scope)
    lines.extend(["", "## Changed Files", ""])
    changed_files = packet.get("changed_files", [])
    if changed_files:
        lines.extend(f"- `{item}`" for item in changed_files)
    else:
        lines.append("- none")
    lines.extend(["", "## Evidence", ""])
    evidence = packet.get("evidence", [])
    if evidence:
        lines.extend(f"- `{item}`" for item in evidence)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Required Output",
            "",
            "Register each structured finding through:",
            "",
            "```powershell",
            (
                f"aiwfctl review add-finding --review-id {session.get('review_id', '')} "
                f"--reviewer {reviewer} --category <category> --severity <severity> "
                "--claim \"<claim>\" --verdict <pass|warn|fail|unsupported|needs-qa|changes-required>"
            ),
            "```",
        ]
    )
    return "\n".join(lines)


def handoff_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    reviewers = _list_arg(args, "reviewer") or [str(item) for item in session.get("packet", {}).get("required_reviewers", [])]
    if not reviewers:
        raise ValueError("No reviewers are available for handoff.")
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    written: list[str] = []
    for reviewer in sorted(dict.fromkeys(reviewers)):
        path = output_dir / f"reviewer-packet-{reviewer}.md"
        write_markdown(path, _reviewer_handoff_markdown(session, reviewer))
        written.append(relative_to_repo(repo_root, path))
    session["reviewer_handoffs"] = written
    session["status"] = "handoff-ready"
    artifacts = _save_session(repo_root, session)
    artifacts["reviewer_handoffs"] = written
    _log(
        repo_root,
        "reviewer_handoff_created",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"reviewers": reviewers, "handoff_count": len(written)},
    )
    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-handoff",
        "status": "handoff-ready",
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "reviewers": reviewers,
        "reviewer_handoffs": written,
        "artifacts": artifacts,
    }


def _orchestration_markdown(run: dict[str, Any]) -> str:
    lines = [
        "# Ariadne Review Council Orchestration",
        "",
        f"Run ID: `{run.get('run_id', '')}`",
        f"Review ID: `{run.get('review_id', '')}`",
        f"Work ID: `{run.get('work_id', '')}`",
        f"Status: `{run.get('status', '')}`",
        f"Adapter: `{run.get('adapter', '')}`",
        f"LangGraph Available: `{str(run.get('available', False)).lower()}`",
        f"Execution Mode: `{run.get('execution_mode', '')}`",
        "",
        "## Graph Execution",
        "",
        f"Engine: `{run.get('graph_execution', {}).get('engine', '')}`",
        f"Compiled: `{str(run.get('graph_execution', {}).get('compiled', False)).lower()}`",
        "",
        "Trace:",
        "",
    ]
    trace = run.get("graph_execution", {}).get("trace", [])
    if trace:
        lines.extend(f"- `{item}`" for item in trace)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
        "## Node Results",
        "",
        "| Node | Status | Reason |",
        "| --- | --- | --- |",
        ]
    )
    for item in run.get("node_results", []):
        lines.append(f"| {item.get('node', '')} | {item.get('status', '')} | {item.get('reason', '')} |")
    lines.extend(["", "## Next Actions", ""])
    next_actions = run.get("next_actions", [])
    if next_actions:
        for item in next_actions:
            lines.extend(
                [
                    f"### {item.get('action', '')}",
                    "",
                    f"Reason: {item.get('reason', '')}",
                    "",
                    "```powershell",
                    str(item.get("command", "")),
                    "```",
                    "",
                ]
            )
    else:
        lines.append("No next action is required.")
    return "\n".join(lines).rstrip() + "\n"


def orchestrate_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    run_id = getattr(args, "run_id", "") or f"orc-{local_timestamp()}"
    run = evaluate_langgraph_review_state(session, run_id=run_id)
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    json_path = output_dir / f"orchestration-{run_id}.json"
    md_path = output_dir / f"orchestration-{run_id}.md"
    run["artifacts"] = {
        "orchestration_json": relative_to_repo(repo_root, json_path),
        "orchestration_report": relative_to_repo(repo_root, md_path),
    }
    write_json(json_path, run)
    write_markdown(md_path, _orchestration_markdown(run))
    orchestration = session.setdefault("orchestration", {})
    orchestration["langgraph"] = run.get("plan", {})
    orchestration["latest_run"] = run
    session.setdefault("orchestration_runs", []).append(
        {
            "run_id": run_id,
            "status": run["status"],
            "created_at": utc_now_iso(),
            "artifacts": run["artifacts"],
        }
    )
    session["status"] = run["status"]
    artifacts = _save_session(repo_root, session)
    artifacts.update(run["artifacts"])
    _log(
        repo_root,
        "review_orchestration_evaluated",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"run_id": run_id, "status": run["status"], "next_actions": len(run["next_actions"])},
    )
    return {**run, "artifacts": artifacts}


def _specialist_handoff_path(session: dict[str, Any], reviewer: str) -> str:
    suffix = f"reviewer-packet-{reviewer}.md"
    return next((str(path) for path in session.get("reviewer_handoffs", []) if str(path).endswith(suffix)), "")


def _specialist_run_markdown(packet: dict[str, Any]) -> str:
    lines = [
        "# Review Council Specialist Run",
        "",
        f"Review ID: `{packet.get('review_id', '')}`",
        f"Work ID: `{packet.get('work_id', '')}`",
        f"Reviewer: `{packet.get('reviewer', '')}`",
        f"Agent: `{packet.get('agent_id', '')}`",
        f"Status: `{packet.get('status', '')}`",
        f"Prompt: `{packet.get('prompt_path', '')}`",
        f"Handoff: `{packet.get('handoff_path', '')}`",
        f"Output: `{packet.get('output_path', '')}`",
        "",
        "## Role",
        "",
        str(packet.get("role", "")),
        "",
        "## Intent",
        "",
        str(packet.get("input", {}).get("intent", "")),
        "",
        "## Required Output",
        "",
        "Write a specialist review report, then register every structured finding through:",
        "",
        "```powershell",
        str(packet.get("required_output", {}).get("finding_registration_command", "")),
        "```",
    ]
    if packet.get("blocked_reason"):
        lines.extend(["", "## Blocked Reason", "", str(packet.get("blocked_reason", ""))])
    return "\n".join(lines).rstrip() + "\n"


def run_specialist_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    reviewer = str(args.reviewer).strip().lower()
    if not reviewer:
        raise ValueError("--reviewer is required.")
    handoff_path = _specialist_handoff_path(session, reviewer)
    if not handoff_path:
        handoff_result = handoff_review(
            argparse.Namespace(
                repo_root=str(repo_root),
                review_id=session["review_id"],
                work_id="",
                work_dir="",
                reviewer=[reviewer],
            )
        )
        handoff_path = str(handoff_result["reviewer_handoffs"][0])
        session = _load_from_args(args)
    prompt_path = ""
    probe_packet = build_specialist_agent_packet(session, reviewer=reviewer, prompt_exists=False, handoff_path=handoff_path)
    prompt_path = str(probe_packet.get("prompt_path", ""))
    prompt_exists = bool(prompt_path) and (repo_root / prompt_path).exists()
    packet = build_specialist_agent_packet(
        session,
        reviewer=reviewer,
        prompt_exists=prompt_exists,
        handoff_path=handoff_path,
    )
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    json_path = output_dir / f"specialist-run-{reviewer}.json"
    md_path = output_dir / f"specialist-run-{reviewer}.md"
    packet["artifacts"] = {
        "specialist_run_json": relative_to_repo(repo_root, json_path),
        "specialist_run_report": relative_to_repo(repo_root, md_path),
    }
    write_json(json_path, packet)
    write_markdown(md_path, _specialist_run_markdown(packet))
    session.setdefault("specialist_runs", [])
    session["specialist_runs"] = [
        item for item in session["specialist_runs"] if item.get("reviewer") != reviewer
    ]
    session["specialist_runs"].append(
        {
            "reviewer": reviewer,
            "agent_id": packet["agent_id"],
            "status": packet["status"],
            "prompt_path": packet["prompt_path"],
            "artifacts": packet["artifacts"],
            "updated_at": utc_now_iso(),
        }
    )
    session["status"] = "specialist-ready" if packet["status"] == "ready" else "specialist-blocked"
    artifacts = _save_session(repo_root, session)
    artifacts.update(packet["artifacts"])
    _log(
        repo_root,
        "specialist_run_prepared",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"reviewer": reviewer, "agent_id": packet["agent_id"], "status": packet["status"]},
    )
    return {**packet, "artifacts": artifacts}


class _CommandFormatValues(dict[str, str]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def _command_format_values(packet: dict[str, Any]) -> dict[str, str]:
    values = {
        "review_id": str(packet.get("review_id", "")),
        "work_id": str(packet.get("work_id", "")),
        "reviewer": str(packet.get("reviewer", "")),
        "agent_id": str(packet.get("agent_id", "")),
        "prompt": str(packet.get("prompt_path", "")),
        "handoff": str(packet.get("handoff_path", "")),
        "output": str(packet.get("output_path", "")),
        "packet_json": str(packet.get("artifacts", {}).get("specialist_run_json", "")),
        "packet_report": str(packet.get("artifacts", {}).get("specialist_run_report", "")),
    }
    quoted = {f"{key}_q": _command_value(value) for key, value in values.items()}
    return {**values, **quoted}


def _format_agent_command(template: str, packet: dict[str, Any]) -> str:
    try:
        return template.format_map(_CommandFormatValues(_command_format_values(packet)))
    except ValueError as exc:
        raise ValueError(f"Invalid specialist agent command template: {exc}") from exc


def _write_execution_text(path: Path, text: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path.stat().st_size


def _specialist_execution_markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Review Council Specialist Execution",
        "",
        f"Review ID: `{record.get('review_id', '')}`",
        f"Work ID: `{record.get('work_id', '')}`",
        f"Reviewer: `{record.get('reviewer', '')}`",
        f"Agent: `{record.get('agent_id', '')}`",
        f"Status: `{record.get('status', '')}`",
        f"Exit Code: `{record.get('exit_code', '')}`",
        f"Duration MS: `{record.get('duration_ms', '')}`",
        f"Report: `{record.get('output_path', '')}`",
        "",
        "## Command",
        "",
        "```text",
        str(record.get("command", "")),
        "```",
        "",
        "## Artifacts",
        "",
    ]
    artifacts = record.get("artifacts", {})
    if isinstance(artifacts, dict) and artifacts:
        lines.extend(f"- `{key}`: `{value}`" for key, value in artifacts.items())
    else:
        lines.append("- none")
    if record.get("reason"):
        lines.extend(["", "## Reason", "", str(record.get("reason", ""))])
    draft = record.get("draft_findings")
    if isinstance(draft, dict) and draft:
        lines.extend(
            [
                "",
                "## Draft Findings",
                "",
                f"- status: `{draft.get('status', '')}`",
                f"- draft_count: `{draft.get('draft_count', 0)}`",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _execution_block_record(
    repo_root: Path,
    session: dict[str, Any],
    packet: dict[str, Any],
    *,
    status: str,
    reason: str,
    command: str = "",
) -> dict[str, Any]:
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    stamp = local_timestamp()
    reviewer = str(packet.get("reviewer", "reviewer"))
    safe_reviewer = re.sub(r"[^a-z0-9_.-]+", "-", reviewer).strip("-") or "reviewer"
    json_path = output_dir / f"specialist-execution-{safe_reviewer}-{stamp}.json"
    md_path = output_dir / f"specialist-execution-{safe_reviewer}-{stamp}.md"
    record = {
        "schema_version": "1.0",
        "artifact_type": "review-council-specialist-execution",
        "schema": REVIEW_COUNCIL_SPECIALIST_EXECUTION_SCHEMA,
        "status": status,
        "reason": reason,
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "reviewer": reviewer,
        "agent_id": packet.get("agent_id", ""),
        "prompt_path": packet.get("prompt_path", ""),
        "handoff_path": packet.get("handoff_path", ""),
        "packet_path": packet.get("artifacts", {}).get("specialist_run_json", ""),
        "output_path": packet.get("output_path", ""),
        "command": command,
        "exit_code": None,
        "duration_ms": 0,
        "created_at": utc_now_iso(),
        "human_check_required": status == "human-check-required",
        "human_check_reasons": [reason] if status == "human-check-required" else [],
        "artifacts": {
            "specialist_execution_json": relative_to_repo(repo_root, json_path),
            "specialist_execution_report": relative_to_repo(repo_root, md_path),
        },
    }
    write_json(json_path, record)
    write_markdown(md_path, _specialist_execution_markdown(record))
    return record


def _record_specialist_execution(repo_root: Path, session: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    session.setdefault("specialist_executions", []).append(
        {
            "reviewer": record.get("reviewer", ""),
            "agent_id": record.get("agent_id", ""),
            "status": record.get("status", ""),
            "exit_code": record.get("exit_code"),
            "output_path": record.get("output_path", ""),
            "artifacts": record.get("artifacts", {}),
            "updated_at": utc_now_iso(),
        }
    )
    for item in session.get("specialist_runs", []):
        if item.get("reviewer") == record.get("reviewer"):
            item["status"] = record.get("status", "")
            item["execution_artifacts"] = record.get("artifacts", {})
            item["output_path"] = record.get("output_path", "")
            item["updated_at"] = utc_now_iso()
    if record.get("status") == "completed" and isinstance(record.get("draft_findings"), dict):
        session["status"] = "finding-draft-ready"
    elif record.get("status") == "completed":
        session["status"] = "specialist-completed"
    elif record.get("status") == "human-check-required":
        session["status"] = "human-decision-required"
    elif record.get("status") == "blocked":
        session["status"] = "specialist-blocked"
    else:
        session["status"] = "specialist-execution-failed"
    artifacts = _save_session(repo_root, session)
    artifacts.update(record.get("artifacts", {}))
    record["artifacts"] = artifacts
    return record


def execute_specialist_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    reviewer = str(args.reviewer).strip().lower()
    if not reviewer:
        raise ValueError("--reviewer is required.")
    packet = run_specialist_review(
        argparse.Namespace(
            repo_root=str(repo_root),
            review_id=session["review_id"],
            work_id="",
            work_dir=getattr(args, "work_dir", ""),
            reviewer=reviewer,
        )
    )
    session = _load_from_args(args)
    command_template = str(getattr(args, "agent_command", "") or os.environ.get("ARIADNE_SPECIALIST_AGENT_COMMAND", "")).strip()
    command = _format_agent_command(command_template, packet) if command_template else ""
    if getattr(args, "human_check", "pending") != "approved":
        record = _execution_block_record(
            repo_root,
            session,
            packet,
            status="human-check-required",
            reason="specialist_agent_execution_requires_human_check",
            command=command,
        )
        _log(
            repo_root,
            "human_check_requested",
            review_id=session["review_id"],
            work_id=session["work_id"],
            output={"reviewer": reviewer, "reason": record["reason"]},
        )
        return _record_specialist_execution(repo_root, session, record)
    if packet.get("status") != "ready":
        record = _execution_block_record(
            repo_root,
            session,
            packet,
            status="blocked",
            reason=str(packet.get("blocked_reason", "specialist_run_not_ready")),
            command=command,
        )
        return _record_specialist_execution(repo_root, session, record)
    if not command:
        record = _execution_block_record(
            repo_root,
            session,
            packet,
            status="blocked",
            reason="specialist_agent_command_missing",
        )
        return _record_specialist_execution(repo_root, session, record)

    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    stamp = local_timestamp()
    safe_reviewer = re.sub(r"[^a-z0-9_.-]+", "-", reviewer).strip("-") or "reviewer"
    json_path = output_dir / f"specialist-execution-{safe_reviewer}-{stamp}.json"
    md_path = output_dir / f"specialist-execution-{safe_reviewer}-{stamp}.md"
    stdout_path = output_dir / f"specialist-execution-{safe_reviewer}-{stamp}-stdout.txt"
    stderr_path = output_dir / f"specialist-execution-{safe_reviewer}-{stamp}-stderr.txt"
    packet_report_path = _resolve_path(repo_root, str(packet.get("artifacts", {}).get("specialist_run_report", "")))
    stdin_text = packet_report_path.read_text(encoding="utf-8-sig") if packet_report_path.exists() else ""
    timeout_seconds = int(getattr(args, "timeout_seconds", 1800))
    _log(
        repo_root,
        "reviewer_started",
        review_id=session["review_id"],
        work_id=session["work_id"],
        input={"reviewer": reviewer, "agent_id": packet.get("agent_id", ""), "timeout_seconds": timeout_seconds},
    )
    started = time.perf_counter()
    stdout_text = ""
    stderr_text = ""
    exit_code: int | None = None
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            input=stdin_text,
            text=True,
            capture_output=True,
            shell=True,
            timeout=timeout_seconds,
            check=False,
        )
        stdout_text = completed.stdout or ""
        stderr_text = completed.stderr or ""
        exit_code = int(completed.returncode)
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout_text = str(exc.stdout or "")
        stderr_text = str(exc.stderr or "")
        exit_code = None
    duration_ms = int((time.perf_counter() - started) * 1000)
    stdout_bytes = _write_execution_text(stdout_path, stdout_text)
    stderr_bytes = _write_execution_text(stderr_path, stderr_text)
    output_path = _resolve_path(repo_root, str(packet.get("output_path", "")))
    if not output_path.exists() and stdout_text.strip() and not timed_out:
        write_markdown(output_path, stdout_text)
    report_exists = output_path.exists() and output_path.is_file()
    status = "failed" if timed_out or exit_code != 0 or not report_exists else "completed"
    reason = ""
    if timed_out:
        reason = "specialist_agent_command_timeout"
    elif exit_code != 0:
        reason = f"specialist_agent_command_exit_{exit_code}"
    elif not report_exists:
        reason = "specialist_agent_report_missing"
    record = {
        "schema_version": "1.0",
        "artifact_type": "review-council-specialist-execution",
        "schema": REVIEW_COUNCIL_SPECIALIST_EXECUTION_SCHEMA,
        "status": status,
        "reason": reason,
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "reviewer": reviewer,
        "agent_id": packet.get("agent_id", ""),
        "prompt_path": packet.get("prompt_path", ""),
        "handoff_path": packet.get("handoff_path", ""),
        "packet_path": packet.get("artifacts", {}).get("specialist_run_json", ""),
        "output_path": relative_to_repo(repo_root, output_path),
        "command": command,
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "stdout_bytes": int(stdout_bytes),
        "stderr_bytes": int(stderr_bytes),
        "report_exists": report_exists,
        "created_at": utc_now_iso(),
        "human_check_required": False,
        "human_check_reasons": [],
        "artifacts": {
            "specialist_execution_json": relative_to_repo(repo_root, json_path),
            "specialist_execution_report": relative_to_repo(repo_root, md_path),
            "stdout": relative_to_repo(repo_root, stdout_path),
            "stderr": relative_to_repo(repo_root, stderr_path),
        },
    }
    if status == "completed" and not getattr(args, "skip_draft_findings", False):
        draft = draft_findings_review(
            argparse.Namespace(
                repo_root=str(repo_root),
                review_id=session["review_id"],
                work_id="",
                work_dir=getattr(args, "work_dir", ""),
                reviewer=reviewer,
                report=relative_to_repo(repo_root, output_path),
                category=reviewer,
                severity="medium",
                verdict="needs-qa",
            )
        )
        record["draft_findings"] = {
            "status": draft.get("status", ""),
            "draft_count": draft.get("draft_count", 0),
            "artifacts": draft.get("artifacts", {}),
        }
        session = _load_from_args(args)
    write_json(json_path, record)
    write_markdown(md_path, _specialist_execution_markdown(record))
    _log(
        repo_root,
        "reviewer_completed",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"reviewer": reviewer, "status": status, "exit_code": exit_code, "duration_ms": duration_ms},
    )
    return _record_specialist_execution(repo_root, session, record)


def _operational_action(action: dict[str, Any], review_id: str) -> dict[str, Any]:
    if action.get("action") == "register-specialist-finding" and action.get("reviewer"):
        reviewer = str(action["reviewer"])
        enriched = dict(action)
        enriched["agent_command"] = f"aiwfctl review run-specialist --review-id {review_id} --reviewer {reviewer}"
        return enriched
    return dict(action)


def next_action_review(args: argparse.Namespace) -> dict[str, Any]:
    session = _load_from_args(args)
    latest_run = (session.get("orchestration") or {}).get("latest_run")
    run = latest_run if isinstance(latest_run, dict) else evaluate_langgraph_review_state(session, run_id="next-action")
    review_id = str(session.get("review_id", ""))
    next_actions = [_operational_action(item, review_id) for item in run.get("next_actions", [])]
    selected_action = next_actions[0] if next_actions else None
    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-next-action",
        "status": "completed" if selected_action is None else "action-required",
        "review_id": review_id,
        "work_id": session.get("work_id", ""),
        "orchestration_status": run.get("status", ""),
        "selected_action": selected_action,
        "next_actions": next_actions,
        "reason": "No next action is required." if selected_action is None else selected_action.get("reason", ""),
    }


def draft_findings_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    reviewer = str(args.reviewer).strip().lower()
    if not reviewer:
        raise ValueError("--reviewer is required.")
    report_path = _resolve_path(repo_root, str(args.report))
    if not report_path.is_file():
        raise FileNotFoundError(f"Specialist review report does not exist: {report_path}")
    report_text = report_path.read_text(encoding="utf-8-sig")
    drafts = [
        _finding_draft_from_section(
            session,
            section,
            draft_id=f"DFT-{index:03d}",
            reviewer=reviewer,
            default_category=getattr(args, "category", "other"),
            default_severity=getattr(args, "severity", "medium"),
            default_verdict=getattr(args, "verdict", "needs-qa"),
        )
        for index, section in enumerate(_split_finding_sections(report_text), start=1)
        if section.strip()
    ]
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    stamp = local_timestamp()
    safe_reviewer = re.sub(r"[^a-z0-9_.-]+", "-", reviewer).strip("-") or "reviewer"
    json_path = output_dir / f"finding-draft-{safe_reviewer}-{stamp}.json"
    md_path = output_dir / f"finding-draft-{safe_reviewer}-{stamp}.md"
    source_report = relative_to_repo(repo_root, report_path)
    record = {
        "schema_version": "1.0",
        "artifact_type": "review-council-finding-draft",
        "status": "drafted",
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "reviewer": reviewer,
        "source_report": source_report,
        "draft_count": len(drafts),
        "drafts": drafts,
        "created_at": utc_now_iso(),
        "artifacts": {
            "finding_draft_json": relative_to_repo(repo_root, json_path),
            "finding_draft_report": relative_to_repo(repo_root, md_path),
        },
    }
    write_json(json_path, record)
    write_markdown(md_path, _finding_draft_markdown(record))
    session.setdefault("finding_drafts", []).append(
        {
            "reviewer": reviewer,
            "source_report": source_report,
            "draft_count": len(drafts),
            "artifacts": record["artifacts"],
            "updated_at": utc_now_iso(),
        }
    )
    session["status"] = "finding-draft-ready"
    artifacts = _save_session(repo_root, session)
    artifacts.update(record["artifacts"])
    _log(
        repo_root,
        "finding_draft_created",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"reviewer": reviewer, "draft_count": len(drafts)},
    )
    return {**record, "artifacts": artifacts}


def summary_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    record = _review_summary_record(session)
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    stamp = local_timestamp()
    summary_id = getattr(args, "summary_id", "") or f"summary-{stamp}"
    json_path = output_dir / f"{summary_id}.json"
    md_path = output_dir / f"{summary_id}.md"
    record["summary_id"] = summary_id
    record["artifacts"] = {
        "summary_json": relative_to_repo(repo_root, json_path),
        "summary_report": relative_to_repo(repo_root, md_path),
    }
    write_json(json_path, record)
    write_markdown(md_path, _review_summary_markdown(record))
    session.setdefault("review_summaries", []).append(
        {
            "summary_id": summary_id,
            "status": record["status"],
            "artifacts": record["artifacts"],
            "updated_at": utc_now_iso(),
        }
    )
    artifacts = _save_session(repo_root, session)
    artifacts.update(record["artifacts"])
    _log(
        repo_root,
        "review_summary_exported",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={
            "summary_id": summary_id,
            "finding_count": record["snapshot"]["finding_count"],
            "issue_count": record["snapshot"]["issue_count"],
        },
    )
    return {**record, "artifacts": artifacts}


def human_gate_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    gate_id = str(getattr(args, "gate", "") or "review-council-final-verdict").strip()
    gate = _review_gate_definition(repo_root, gate_id)
    approved_value = str(gate.get("approved_value", "approved"))
    actual = str(getattr(args, "human_check", "pending"))
    status = "approved" if actual == approved_value or not gate.get("requires_human_check", True) else "blocked"
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    stamp = local_timestamp()
    safe_gate = re.sub(r"[^a-z0-9_.-]+", "-", gate_id.lower()).strip("-") or "human-gate"
    json_path = output_dir / f"human-gate-{safe_gate}-{stamp}.json"
    md_path = output_dir / f"human-gate-{safe_gate}-{stamp}.md"
    repair_command = ""
    if status == "blocked":
        repair_command = (
            f"aiwfctl review human-gate --review-id {session.get('review_id', '')} "
            f"--gate {gate_id} --human-check {approved_value}"
        )
    record = {
        "schema_version": "1.0",
        "artifact_type": "review-council-human-gate",
        "status": status,
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "gate": gate_id,
        "label": gate.get("label", ""),
        "required": approved_value,
        "actual": actual,
        "reason": gate.get("reason", ""),
        "reviewer": getattr(args, "reviewer", "Human"),
        "decision_reason": getattr(args, "reason", ""),
        "summary_artifacts": _latest_summary_artifacts(session),
        "created_at": utc_now_iso(),
        "repair_command": repair_command,
        "gate_restart": gate_restart.build_status_gate_restart(
            "review-council-human-gate",
            status=status,
            restart_reason=gate_id,
            repair_command=repair_command,
        ),
        "artifacts": {
            "human_gate_json": relative_to_repo(repo_root, json_path),
            "human_gate_report": relative_to_repo(repo_root, md_path),
        },
    }
    write_json(json_path, record)
    write_markdown(md_path, _review_human_gate_markdown(record))
    session.setdefault("human_gates", []).append(record)
    if status == "approved":
        session["human_check"] = approved_value
        session["status"] = "human-gate-approved"
    else:
        session["status"] = "human-decision-required"
    artifacts = _save_session(repo_root, session)
    artifacts.update(record["artifacts"])
    _log(
        repo_root,
        "review_human_gate_checked",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"gate": gate_id, "status": status, "actual": actual},
    )
    return {**record, "artifacts": artifacts}


def _knowledge_capture_markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Review Council Knowledge Capture",
        "",
        f"Review ID: `{record.get('review_id', '')}`",
        f"Work ID: `{record.get('work_id', '')}`",
        f"Status: `{record.get('status', '')}`",
        f"Verdict: `{record.get('verdict', '')}`",
        "",
        "## Summary",
        "",
        str(record.get("summary", "")),
        "",
        "## RAG Candidates",
        "",
    ]
    candidates = record.get("rag_candidates", [])
    if candidates:
        lines.append("| Kind | Path | Reason |")
        lines.append("| --- | --- | --- |")
        for item in candidates:
            lines.append(f"| {item.get('kind', '')} | `{item.get('path', '')}` | {item.get('reason', '')} |")
    else:
        lines.append("- none")
    lines.extend(["", "## Open Issues", ""])
    issues = record.get("open_issues", [])
    if issues:
        lines.extend(f"- `{item.get('issue_id', '')}` {item.get('severity', '')}: {item.get('claim', '')}" for item in issues)
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def capture_review_knowledge(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    verdict = session.get("verdict") or {}
    artifacts = session.get("artifacts", {})
    rag_candidates: list[dict[str, str]] = []
    for key in ("session", "report"):
        value = str(artifacts.get(key, "")).strip()
        if value:
            rag_candidates.append(
                {
                    "kind": f"review-{key}",
                    "path": value,
                    "reason": "Review Council session/report contains reusable review decisions and evidence links.",
                }
            )
    for run in session.get("orchestration_runs", []):
        run_artifacts = run.get("artifacts", {})
        for key, value in run_artifacts.items():
            if str(value).strip():
                rag_candidates.append(
                    {
                        "kind": key,
                        "path": str(value),
                        "reason": "Orchestration state explains review order, blockers, and next actions.",
                    }
                )
    for run in session.get("specialist_runs", []):
        run_artifacts = run.get("artifacts", {})
        for key, value in run_artifacts.items():
            if str(value).strip():
                rag_candidates.append(
                    {
                        "kind": key,
                        "path": str(value),
                        "reason": "Specialist run packet preserves reviewer prompt, scope, and required output contract.",
                    }
                )
    for summary in session.get("review_summaries", []):
        summary_artifacts = summary.get("artifacts", {})
        for key, value in summary_artifacts.items():
            if str(value).strip():
                rag_candidates.append(
                    {
                        "kind": key,
                        "path": str(value),
                        "reason": "Review summary exports the human-readable decision snapshot and next actions.",
                    }
                )
    for human_gate in session.get("human_gates", []):
        gate_artifacts = human_gate.get("artifacts", {})
        for key, value in gate_artifacts.items():
            if str(value).strip():
                rag_candidates.append(
                    {
                        "kind": key,
                        "path": str(value),
                        "reason": "Human Gate evidence records explicit approval or blocked review decisions.",
                    }
                )
    evidence_gate_record = session.get("evidence_gate") or {}
    if evidence_gate_record:
        for value in evidence_gate_record.get("evidence", []):
            rag_candidates.append(
                {
                    "kind": "review-evidence",
                    "path": str(value),
                    "reason": "Evidence referenced by Review Council should be available to future review workflows.",
                }
            )
    unique_candidates = list({item["path"]: item for item in rag_candidates}.values())
    record = {
        "schema_version": "1.0",
        "artifact_type": "review-council-knowledge-capture",
        "status": "captured",
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "captured_at": utc_now_iso(),
        "verdict": verdict.get("verdict", ""),
        "summary": verdict.get("reason", "") or "Review Council artifacts captured for future Knowledge/RAG reuse.",
        "rag_candidates": unique_candidates,
        "open_issues": [item for item in session.get("issues", []) if item.get("status") == "open"],
        "finding_count": len(session.get("findings", [])),
        "challenge_count": len(session.get("challenge_rounds", [])),
        "reinspection_count": len(session.get("reinspections", [])),
    }
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    stamp = local_timestamp()
    json_path = output_dir / f"knowledge-capture-{stamp}.json"
    md_path = output_dir / f"knowledge-capture-{stamp}.md"
    record["artifacts"] = {
        "knowledge_capture_json": relative_to_repo(repo_root, json_path),
        "knowledge_capture_report": relative_to_repo(repo_root, md_path),
    }
    write_json(json_path, record)
    write_markdown(md_path, _knowledge_capture_markdown(record))
    session["review_knowledge_capture"] = {
        "status": "captured",
        "captured_at": record["captured_at"],
        "artifacts": record["artifacts"],
        "rag_candidate_count": len(unique_candidates),
    }
    session["status"] = "knowledge-captured"
    artifacts = _save_session(repo_root, session)
    artifacts.update(record["artifacts"])
    _log(
        repo_root,
        "review_knowledge_captured",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"rag_candidate_count": len(unique_candidates)},
    )
    return {**record, "artifacts": artifacts}


def _latest_knowledge_capture_record(repo_root: Path, session: dict[str, Any]) -> dict[str, Any]:
    capture = session.get("review_knowledge_capture", {})
    artifacts = capture.get("artifacts", {}) if isinstance(capture, dict) else {}
    capture_json = str(artifacts.get("knowledge_capture_json", "")).strip()
    if not capture_json:
        return {}
    data = read_json(_resolve_path(repo_root, capture_json), default={})
    return data if isinstance(data, dict) else {}


def _review_rag_source_dir(repo_root: Path, session: dict[str, Any]) -> Path:
    work_id = slugify(str(session.get("work_id", "")))
    review_id = slugify(str(session.get("review_id", "")))
    return repo_root / SOURCE_REVIEW_COUNCIL / work_id / review_id


def _front_matter_value(value: Any) -> str:
    text = str(value).replace('"', "'").replace("\r", " ").replace("\n", " ").strip()
    return f'"{text}"'


def _front_matter_list(key: str, values: list[str]) -> list[str]:
    lines = [f"{key}:"]
    if values:
        lines.extend(f"- {_front_matter_value(item)}" for item in values)
    else:
        lines.append("- \"\"")
    return lines


def _review_rag_source_markdown(session: dict[str, Any], capture: dict[str, Any]) -> str:
    packet = session.get("packet", {})
    verdict = session.get("verdict") or {}
    evidence_gate_record = session.get("evidence_gate") or {}
    candidates = capture.get("rag_candidates", [])
    source_paths = [str(item.get("path", "")) for item in candidates if str(item.get("path", "")).strip()]
    tags = ["review-council", "specialist-review", "knowledge-capture"]
    areas = [str(item) for item in packet.get("scope", []) if str(item).strip()] or ["review"]
    front_matter = [
        "---",
        f"title: {_front_matter_value('Review Council ' + str(session.get('review_id', '')))}",
        "type: review-council",
        "artifact_type: review-council-rag-source",
        "source_type: internal-work",
        "source_kind: review-council",
        "source_owner: ariadne-review-council",
        "category: review",
        f"topic: {_front_matter_value(packet.get('target', '') or 'Review Council')}",
        "trust_level: project-evidence",
        f"project: {_front_matter_value('Ariadne')}",
        f"repository: {_front_matter_value(packet.get('target', ''))}",
        f"branch: {_front_matter_value('')}",
        f"commit: {_front_matter_value(packet.get('target_revision', '') or 'unknown')}",
        "workflow: review-council",
        "phase: knowledge-capture",
        "agent: runtime-review",
        f"status: {_front_matter_value(capture.get('status', session.get('status', 'captured')))}",
        f"created_at: {_front_matter_value(capture.get('captured_at', utc_now_iso()))}",
        *_front_matter_list("tags", tags),
        *_front_matter_list("areas", areas),
        *_front_matter_list("sources", source_paths),
        "---",
        "",
    ]
    lines = [
        *front_matter,
        "# Review Council Knowledge",
        "",
        f"Review ID: `{session.get('review_id', '')}`",
        f"Work ID: `{session.get('work_id', '')}`",
        f"Session Status: `{session.get('status', '')}`",
        f"Verdict: `{verdict.get('verdict', '') or 'not-decided'}`",
        "",
        "## Intent",
        "",
        str(packet.get("intent", "")) or "No intent was recorded.",
        "",
        "## Decision",
        "",
        str(verdict.get("reason", "")) or str(capture.get("summary", "")) or "No final verdict reason was recorded.",
        "",
        "## Findings",
        "",
    ]
    findings = session.get("findings", [])
    if findings:
        for item in findings:
            lines.extend(
                [
                    f"- `{item.get('finding_id', '')}` {item.get('severity', '')} / {item.get('verdict', '')}: {item.get('claim', '')}",
                    f"  - reviewer: `{item.get('reviewer', '')}`",
                    f"  - status: `{item.get('status', '')}`",
                    f"  - requested action: {item.get('requested_action', '') or 'none'}",
                ]
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Review Issues", ""])
    issues = session.get("issues", [])
    if issues:
        for item in issues:
            lines.append(
                f"- `{item.get('issue_id', '')}` {item.get('severity', '')}: {item.get('claim', '')} "
                f"(status: `{item.get('status', '')}`, blocking: `{str(item.get('blocking', False)).lower()}`)"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Gates", ""])
    lines.extend(
        [
            f"- challenge completed: `{str(bool(session.get('challenge_completed', False))).lower()}`",
            f"- evidence verified: `{str(bool(session.get('evidence_verified', False))).lower()}`",
            f"- evidence gate status: `{evidence_gate_record.get('status', '')}`",
            f"- human check: `{session.get('human_check', '')}`",
        ]
    )
    lines.extend(["", "## Source Artifacts", ""])
    if candidates:
        for item in candidates:
            lines.append(f"- `{item.get('kind', '')}`: `{item.get('path', '')}` - {item.get('reason', '')}")
    else:
        lines.append("- none")
    return "\n".join(lines).rstrip() + "\n"


def _review_rag_build_command(record: dict[str, Any]) -> str:
    parts = [
        "uv",
        "run",
        "--project",
        "runtime",
        "python",
        "runtime/ctl/ctl.py",
        "--repo-root",
        ".",
        "rag",
        "build",
        "--work-id",
        _command_value(str(record.get("work_id", ""))),
        "--source-dir",
        _command_value(str(record.get("source_dir", ""))),
        "--document-type",
        "review-council",
        "--output",
        _command_value(str(record.get("rag_build_output", ""))),
    ]
    if record.get("duckdb_migrate"):
        parts.append("--duckdb-migrate")
    return " ".join(parts)


def _review_rag_build_markdown(record: dict[str, Any]) -> str:
    lines = [
        "# Review Council RAG Build Bridge",
        "",
        f"Review ID: `{record.get('review_id', '')}`",
        f"Work ID: `{record.get('work_id', '')}`",
        f"Status: `{record.get('status', '')}`",
        f"Source Dir: `{record.get('source_dir', '')}`",
        f"Source Document: `{record.get('source_document', '')}`",
        "",
        "## Build Command",
        "",
        "```powershell",
        str(record.get("build_command", "")),
        "```",
        "",
        "## Candidate Checks",
        "",
    ]
    checks = record.get("candidate_checks", [])
    if checks:
        lines.append("| Kind | Path | Exists | Size |")
        lines.append("| --- | --- | --- | ---: |")
        for item in checks:
            lines.append(
                f"| {_md_cell(item.get('kind', ''))} | `{item.get('path', '')}` | "
                f"{str(item.get('exists', False)).lower()} | {int(item.get('size', 0))} |"
            )
    else:
        lines.append("- none")
    rag_result = record.get("rag_build_run")
    if isinstance(rag_result, dict) and rag_result:
        lines.extend(["", "## RAG Build Result", ""])
        lines.append(f"- status: `{rag_result.get('status', '')}`")
        lines.append(f"- run: `{rag_result.get('rag_build_run', '')}`")
        lines.append(f"- documents: `{rag_result.get('document_count', 0)}`")
        lines.append(f"- chunks: `{rag_result.get('chunk_count', 0)}`")
    return "\n".join(lines).rstrip() + "\n"


def rag_build_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    capture = _latest_knowledge_capture_record(repo_root, session)
    if getattr(args, "refresh_capture", False) or not capture:
        capture = capture_review_knowledge(args)
        session = _load_from_args(args)
    source_dir = _review_rag_source_dir(repo_root, session)
    source_path = source_dir / f"{slugify(str(session.get('review_id', 'review')))}.md"
    write_markdown(source_path, _review_rag_source_markdown(session, capture))
    candidates = capture.get("rag_candidates", [])
    candidate_checks = [
        {**_path_check(repo_root, str(item.get("path", "")), kind=str(item.get("kind", "rag-candidate"))), "reason": item.get("reason", "")}
        for item in candidates
        if str(item.get("path", "")).strip()
    ]
    stamp = local_timestamp()
    output_dir = ReviewStore(repo_root).process_report_dir(session["work_id"]) / "review-council"
    manifest_path = output_dir / f"rag-build-{stamp}.json"
    report_path = output_dir / f"rag-build-{stamp}.md"
    rag_build_output = str(getattr(args, "output", "")).strip() or str(RAG_BUILD_RUN_LATEST)
    record = {
        "schema_version": "1.0",
        "artifact_type": "review-council-rag-build",
        "schema": REVIEW_COUNCIL_RAG_BUILD_SCHEMA,
        "status": "ready",
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "created_at": utc_now_iso(),
        "source_dir": relative_to_repo(repo_root, source_dir),
        "source_document": relative_to_repo(repo_root, source_path),
        "document_type": "review-council",
        "knowledge_capture": capture.get("artifacts", {}),
        "rag_candidate_count": len(candidates),
        "candidate_checks": candidate_checks,
        "missing_candidate_count": len([item for item in candidate_checks if not item.get("exists")]),
        "run_requested": bool(getattr(args, "run", False)),
        "clean_output": bool(getattr(args, "clean_output", False)),
        "skip_optimization": bool(getattr(args, "skip_optimization", False)),
        "duckdb_migrate": bool(getattr(args, "duckdb_migrate", False)),
        "rag_build_output": rag_build_output,
        "artifacts": {
            "rag_build_json": relative_to_repo(repo_root, manifest_path),
            "rag_build_report": relative_to_repo(repo_root, report_path),
            "rag_source_document": relative_to_repo(repo_root, source_path),
        },
    }
    record["build_command"] = _review_rag_build_command(record)
    if record["run_requested"]:
        run_result = rag_build.run(
            argparse.Namespace(
                repo_root=str(repo_root),
                work_id=session["work_id"],
                work_dir=getattr(args, "work_dir", ""),
                source_dir=record["source_dir"],
                document_type="review-council",
                normalized_dir=str(getattr(args, "normalized_dir", "") or GENERATED_NORMALIZED),
                chunks_dir=str(getattr(args, "chunks_dir", "") or GENERATED_CHUNKS),
                optimized_chunks_dir=str(getattr(args, "optimized_chunks_dir", "") or GENERATED_OPTIMIZED_CHUNKS),
                indexes_dir=str(getattr(args, "indexes_dir", "") or GENERATED_INDEXES),
                embeddings_output=str(getattr(args, "embeddings_output", "") or EMBEDDINGS_INDEX),
                output=rag_build_output,
                ingestion_evidence_dir=str(getattr(args, "ingestion_evidence_dir", "") or DUCKDB_INGESTION_EVIDENCE_DIR),
                ingestion_policy=str(getattr(args, "ingestion_policy", "") or RAG_INGESTION_POLICY_PATH),
                skip_optimization=bool(getattr(args, "skip_optimization", False)),
                duckdb_migrate=bool(getattr(args, "duckdb_migrate", False)),
                duckdb_path=str(getattr(args, "duckdb_path", "") or rag_build.duckdb_store.DEFAULT_DB_PATH),
                duckdb_source_dir=str(getattr(args, "duckdb_source_dir", "")),
                duckdb_error_log=str(getattr(args, "duckdb_error_log", "") or rag_build.duckdb_store.DEFAULT_ERROR_LOG),
                duckdb_evidence_output=str(getattr(args, "duckdb_evidence_output", "") or DUCKDB_MIGRATION_EVIDENCE),
                duckdb_policy=str(getattr(args, "duckdb_policy", "")),
                project=str(getattr(args, "project", "") or "Ariadne"),
                repository=str(getattr(args, "repository", "") or session.get("packet", {}).get("target", "")),
                branch=str(getattr(args, "branch", "")),
                commit=str(getattr(args, "commit", "") or session.get("packet", {}).get("target_revision", "")),
                status=str(getattr(args, "status", "") or "captured"),
                chunk_size=int(getattr(args, "chunk_size", 1800)),
                chunk_overlap=int(getattr(args, "chunk_overlap", 180)),
                embedding_dimensions=int(getattr(args, "embedding_dimensions", 768)),
                clean_output=bool(getattr(args, "clean_output", False)),
                standardize_filenames=False,
                skip_standardize=True,
                replace_references=False,
                random_length=8,
            )
        )
        record["rag_build_run"] = run_result
        record["status"] = str(run_result.get("status", "completed"))
    write_json(manifest_path, record)
    write_markdown(report_path, _review_rag_build_markdown(record))
    session.setdefault("rag_builds", []).append(
        {
            "status": record["status"],
            "source_document": record["source_document"],
            "artifacts": record["artifacts"],
            "updated_at": utc_now_iso(),
            "run_requested": record["run_requested"],
        }
    )
    session["status"] = "rag-build-completed" if record["run_requested"] else "rag-build-ready"
    artifacts = _save_session(repo_root, session)
    artifacts.update(record["artifacts"])
    record["artifacts"] = artifacts
    _log(
        repo_root,
        "review_rag_build_bridged",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"status": record["status"], "run_requested": record["run_requested"], "source_document": record["source_document"]},
    )
    return record


def _load_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return ReviewStore(Path(args.repo_root).resolve()).load(
        review_id=getattr(args, "review_id", ""),
        work_id=getattr(args, "work_id", ""),
        work_dir=getattr(args, "work_dir", ""),
    )


def add_finding(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    finding_count = len(session.get("findings", [])) + 1
    blocking = None
    if getattr(args, "blocking", False):
        blocking = True
    if getattr(args, "non_blocking", False):
        blocking = False
    finding = normalize_finding(
        {
            "finding_id": getattr(args, "finding_id", "") or f"FND-{finding_count:03d}",
            "reviewer": args.reviewer,
            "category": args.category,
            "severity": args.severity,
            "claim": args.claim,
            "verdict": args.verdict,
            "evidence_refs": _list_arg(args, "evidence_ref"),
            "counterexample": getattr(args, "counterexample", ""),
            "reasoning_summary": getattr(args, "reasoning_summary", ""),
            "requested_action": getattr(args, "requested_action", ""),
            "confidence": getattr(args, "confidence", 0.8),
            "required_tests": _list_arg(args, "required_test"),
            "blocking": blocking,
        }
    )
    session.setdefault("findings", []).append(finding)
    session["status"] = "reviewing"
    artifacts = _save_session(repo_root, session)
    _log(
        repo_root,
        "finding_registered",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"finding_id": finding["finding_id"], "severity": finding["severity"], "verdict": finding["verdict"]},
    )
    return {**session, "artifacts": artifacts, "finding": finding}


def challenge_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    selected_issue_ids = _list_arg(args, "issue_id")
    issues = session.get("issues", [])
    selected_issues = [
        item for item in issues if not selected_issue_ids or str(item.get("issue_id", "")) in selected_issue_ids
    ]
    challenge_id = getattr(args, "challenge_id", "") or f"CHG-{len(session.get('challenge_rounds', [])) + 1:03d}"
    counterexample_found = bool(getattr(args, "counterexample_found", False))
    record = {
        "challenge_id": challenge_id,
        "status": "human-check-required" if counterexample_found else "completed",
        "challenger": getattr(args, "challenger", ""),
        "mode": getattr(args, "mode", "counterexample-check"),
        "issue_ids": [str(item.get("issue_id", "")) for item in selected_issues],
        "counterexample_found": counterexample_found,
        "summary": getattr(args, "summary", ""),
        "evidence_refs": _list_arg(args, "evidence_ref"),
        "target_issue_ids": [str(item.get("issue_id", "")) for item in selected_issues],
        "finding_ids": sorted(
            {
                str(finding_id)
                for item in selected_issues
                for finding_id in item.get("finding_ids", [])
                if str(finding_id).strip()
            }
        ),
        "challenge_plan": {
            "questions": [
                "Does any selected issue still have a concrete counterexample?",
                "Does the cited evidence actually support each reviewer claim?",
                "Could the current packet pass while violating its stated guardrails?",
            ],
            "counterexample_checks": [
                {
                    "issue_id": str(item.get("issue_id", "")),
                    "claim": str(item.get("claim", "")),
                    "expected_result": "no surviving counterexample",
                }
                for item in selected_issues
            ],
        },
        "created_at": utc_now_iso(),
    }
    session.setdefault("challenge_rounds", []).append(record)
    session["challenge_completed"] = not counterexample_found
    session["status"] = "human-decision-required" if counterexample_found else "challenge-completed"
    artifacts = _save_session(repo_root, session)
    _log(
        repo_root,
        "challenge_started",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"challenge_id": challenge_id, "issue_count": len(record["issue_ids"])},
    )
    if counterexample_found:
        _log(
            repo_root,
            "counterexample_found",
            review_id=session["review_id"],
            work_id=session["work_id"],
            output={"challenge_id": challenge_id, "summary": record["summary"]},
        )
    return {**record, "review_id": session["review_id"], "work_id": session["work_id"], "artifacts": artifacts}


def _resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _required_evidence(session: dict[str, Any], extra: list[str]) -> list[str]:
    values: list[str] = []
    packet = session.get("packet", {})
    values.extend(str(item) for item in packet.get("evidence", []) if str(item).strip())
    for finding in session.get("findings", []):
        values.extend(str(item) for item in finding.get("evidence_refs", []) if str(item).strip())
    for issue in session.get("issues", []):
        values.extend(str(item) for item in issue.get("required_evidence", []) if str(item).strip())
    values.extend(extra)
    return sorted(dict.fromkeys(values))


def _required_tests(session: dict[str, Any], extra: list[str]) -> list[str]:
    values: list[str] = []
    for finding in session.get("findings", []):
        values.extend(str(item) for item in finding.get("required_tests", []) if str(item).strip())
    for issue in session.get("issues", []):
        values.extend(str(item) for item in issue.get("required_tests", []) if str(item).strip())
    values.extend(extra)
    return sorted(dict.fromkeys(values))


def _default_test_spec_paths(repo_root: Path, work_id: str) -> list[Path]:
    base = repo_root / "work" / work_id / "test-specifications"
    if not base.exists():
        return []
    return sorted(path for path in base.glob("*.md") if path.is_file())


def _test_text(repo_root: Path, paths: list[str], work_id: str) -> str:
    resolved = [_resolve_path(repo_root, item) for item in paths] if paths else _default_test_spec_paths(repo_root, work_id)
    texts: list[str] = []
    for path in resolved:
        if path.exists() and path.is_file():
            texts.append(path.read_text(encoding="utf-8-sig"))
    return "\n".join(texts).lower()


def evidence_gate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    evidence_paths = _required_evidence(session, _list_arg(args, "evidence"))
    evidence_results = [_path_check(repo_root, value, kind="evidence") for value in evidence_paths]
    missing_evidence = [item["path"] for item in evidence_results if not item["exists"]]
    required_tests = _required_tests(session, _list_arg(args, "required_test"))
    test_text = _test_text(repo_root, _list_arg(args, "test_spec"), session["work_id"])
    missing_required_tests = [value for value in required_tests if value.lower() not in test_text]
    artifact_values = [str(value) for value in session.get("artifacts", {}).values() if str(value).strip()]
    for run in session.get("orchestration_runs", []):
        artifact_values.extend(str(value) for value in run.get("artifacts", {}).values() if str(value).strip())
    for run in session.get("specialist_runs", []):
        artifact_values.extend(str(value) for value in run.get("artifacts", {}).values() if str(value).strip())
    artifact_checks = [_path_check(repo_root, value, kind="review-artifact") for value in sorted(dict.fromkeys(artifact_values))]
    missing_artifacts = [item["path"] for item in artifact_checks if not item["exists"]]
    status = "verified" if not missing_evidence and not missing_required_tests and not missing_artifacts else "blocked"
    record = {
        "schema_version": "1.0",
        "artifact_type": "review-council-evidence-gate",
        "status": status,
        "review_id": session["review_id"],
        "work_id": session["work_id"],
        "checked_at": utc_now_iso(),
        "evidence": evidence_paths,
        "evidence_results": evidence_results,
        "missing_evidence": missing_evidence,
        "required_tests": required_tests,
        "missing_required_tests": missing_required_tests,
        "artifact_checks": artifact_checks,
        "missing_artifacts": missing_artifacts,
    }
    session["evidence_gate"] = record
    session["evidence_verified"] = status == "verified"
    session["status"] = "evidence-verified" if status == "verified" else "evidence-blocked"
    artifacts = _save_session(repo_root, session)
    _log(
        repo_root,
        "evidence_gate_completed",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"status": status, "missing_evidence": len(missing_evidence), "missing_required_tests": len(missing_required_tests)},
    )
    return {**record, "artifacts": artifacts}


def reinspect_review(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    finding_ids = set(_list_arg(args, "finding_id"))
    if not finding_ids:
        raise ValueError("--finding-id is required.")
    updated: list[str] = []
    previous_statuses: dict[str, str] = {}
    for finding in session.get("findings", []):
        if str(finding.get("finding_id", "")) in finding_ids:
            previous_statuses[str(finding.get("finding_id", ""))] = str(finding.get("status", ""))
            finding["status"] = args.status
            if getattr(args, "evidence_ref", []):
                evidence_refs = list(finding.get("evidence_refs", []))
                evidence_refs.extend(_list_arg(args, "evidence_ref"))
                finding["evidence_refs"] = sorted(dict.fromkeys(evidence_refs))
            updated.append(str(finding.get("finding_id", "")))
    if not updated:
        raise KeyError(f"Unknown finding id: {', '.join(sorted(finding_ids))}")
    related_issues = [
        item
        for item in session.get("issues", [])
        if set(str(finding_id) for finding_id in item.get("finding_ids", [])) & set(updated)
    ]
    evidence_results = [_path_check(repo_root, value, kind="reinspection-evidence") for value in _list_arg(args, "evidence_ref")]
    record = {
        "reinspection_id": f"RIN-{len(session.get('reinspections', [])) + 1:03d}",
        "reviewer": getattr(args, "reviewer", ""),
        "finding_ids": updated,
        "issue_ids": [str(item.get("issue_id", "")) for item in related_issues],
        "previous_statuses": previous_statuses,
        "status": args.status,
        "summary": getattr(args, "summary", ""),
        "evidence_refs": _list_arg(args, "evidence_ref"),
        "evidence_results": evidence_results,
        "created_at": utc_now_iso(),
    }
    session.setdefault("reinspections", []).append(record)
    session["status"] = "reinspection-completed"
    artifacts = _save_session(repo_root, session)
    _log(
        repo_root,
        "reinspection_completed",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"reinspection_id": record["reinspection_id"], "finding_ids": updated, "status": args.status},
    )
    return {**record, "review_id": session["review_id"], "work_id": session["work_id"], "artifacts": artifacts}


def status_review(args: argparse.Namespace) -> dict[str, Any]:
    session = _load_from_args(args)
    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-status",
        "review_id": session.get("review_id", ""),
        "work_id": session.get("work_id", ""),
        "status": session.get("status", ""),
        "specialist_execution_count": len(session.get("specialist_executions", [])),
        "finding_draft_count": sum(int(item.get("draft_count", 0)) for item in session.get("finding_drafts", [])),
        "finding_count": len(session.get("findings", [])),
        "issue_count": len(session.get("issues", [])),
        "human_gate_count": len(session.get("human_gates", [])),
        "human_check": session.get("human_check", ""),
        "required_reviewers": session.get("packet", {}).get("required_reviewers", []),
        "reviewer_handoffs": session.get("reviewer_handoffs", []),
        "verdict": (session.get("verdict") or {}).get("verdict", ""),
        "challenge_completed": bool(session.get("challenge_completed", False)),
        "evidence_verified": bool(session.get("evidence_verified", False)),
        "artifacts": session.get("artifacts", {}),
        "gate_restart": session.get("gate_restart", {}),
    }


def list_issues(args: argparse.Namespace) -> dict[str, Any]:
    session = _load_from_args(args)
    return {
        "schema_version": "1.0",
        "artifact_type": "review-council-issues",
        "review_id": session.get("review_id", ""),
        "work_id": session.get("work_id", ""),
        "issues": session.get("issues", []),
        "issue_count": len(session.get("issues", [])),
    }


def inspect_review(args: argparse.Namespace) -> dict[str, Any]:
    return _load_from_args(args)


def decide_verdict(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve()
    session = _load_from_args(args)
    evidence_verified = bool(getattr(args, "evidence_verified", False)) or bool(session.get("evidence_verified", False))
    challenge_completed = bool(getattr(args, "challenge_completed", False)) or bool(session.get("challenge_completed", False))
    target_consistent = getattr(args, "target_revision_consistent", False)
    if not target_consistent:
        packet_revision = str(session.get("packet", {}).get("target_revision", ""))
        current_revision = _current_git_revision(repo_root)
        target_consistent = packet_revision in {"", "unknown"} or current_revision in {"unknown", packet_revision}
    human_check = getattr(args, "human_check", "pending")
    if human_check != "approved" and _latest_approved_human_gate(session, "review-council-risk-acceptance"):
        human_check = "approved"
    verdict = decide(
        session,
        evidence_verified=evidence_verified,
        challenge_completed=challenge_completed,
        target_revision_consistent=target_consistent,
        human_check=human_check,
    )
    session["verdict"] = verdict
    session["status"] = verdict["verdict"].lower().replace("_", "-")
    artifacts = _save_session(repo_root, session)
    _log(
        repo_root,
        "review_verdict_decided",
        review_id=session["review_id"],
        work_id=session["work_id"],
        output={"verdict": verdict["verdict"], "status": session["status"]},
    )
    return {**verdict, "review_id": session["review_id"], "work_id": session["work_id"], "artifacts": artifacts}
