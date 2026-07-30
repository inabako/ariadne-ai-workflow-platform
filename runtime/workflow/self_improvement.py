from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    find_repo_root,
    load_artifact_index,
    local_timestamp,
    read_json,
    relative_to_repo,
    slugify,
    upsert_artifact,
    utc_now_iso,
    write_json,
    write_markdown_bom,
)
from runtime.constants.schemas import ARTIFACT_INDEX_SCHEMA  # noqa: E402
from runtime.constants.workflow_limits import SELF_IMPROVEMENT_EVENT_PREVIEW_LIMIT  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    context_dir_for_work_dir,
    process_report_dir_for_work_dir,
    test_evidence_dir_for_work_dir,
    work_dir_for_id,
)
from runtime.observability.logger import runtime_event_log_path  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


VALID_DECISIONS = {"accepted", "rejected", "deferred"}
TEMPLATE_DIR = Path("templates/workflows/self-improvement")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Self-improvement workflow helper.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    init_feedback = sub.add_parser("init-feedback", help="Create work/feedback README.")
    init_feedback.set_defaults(handler=run_init_feedback)

    create_feedback = sub.add_parser("create-feedback", help="Create a workflow feedback report.")
    create_feedback.add_argument("--target-workflow", required=True)
    create_feedback.add_argument("--reporter", default="Human")
    create_feedback.add_argument("--situation", required=True)
    create_feedback.add_argument("--friction", required=True)
    create_feedback.add_argument("--impact", default="")
    create_feedback.add_argument("--proposed-improvement", default="")
    create_feedback.add_argument("--evidence", action="append", default=[])
    create_feedback.add_argument("--priority", default="Medium", choices=["Low", "Medium", "High"])
    create_feedback.add_argument("--category", default="Workflow")
    create_feedback.add_argument("--runtime-trace-id", default="")
    create_feedback.add_argument("--runtime-log", default="")
    create_feedback.add_argument("--output", default="")
    create_feedback.set_defaults(handler=run_create_feedback)

    review = sub.add_parser("review-feedback", help="Append human review result to a feedback report.")
    review.add_argument("--feedback", required=True)
    review.add_argument("--decision", required=True, choices=sorted(VALID_DECISIONS))
    review.add_argument("--reviewer", required=True)
    review.add_argument("--reason", required=True)
    review.add_argument("--next-action", default="")
    review.set_defaults(handler=run_review_feedback)

    issue_body = sub.add_parser("issue-body", help="Create a GitHub Issue body from accepted feedback.")
    issue_body.add_argument("--feedback", required=True)
    issue_body.add_argument("--output", default="")
    issue_body.add_argument("--allow-unaccepted", action="store_true")
    issue_body.set_defaults(handler=run_issue_body)

    branch = sub.add_parser("branch-name", help="Generate the standard issue branch name.")
    branch.add_argument("--issue-number", required=True)
    branch.set_defaults(handler=run_branch_name)

    evidence = sub.add_parser("evidence-scaffold", help="Create self-improvement evidence directories.")
    evidence.add_argument("--work-id", required=True)
    evidence.set_defaults(handler=run_evidence_scaffold)
    return parser


def resolve_repo_root(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve() if args.repo_root else find_repo_root()


def feedback_dir(repo_root: Path) -> Path:
    return work_dir_for_id(repo_root, "feedback")


def template_path(repo_root: Path, name: str) -> Path:
    return repo_root / TEMPLATE_DIR / name


def read_template(repo_root: Path, name: str) -> str:
    path = template_path(repo_root, name)
    if not path.exists():
        raise FileNotFoundError(f"Template does not exist: {path}")
    return path.read_text(encoding="utf-8-sig")


def run_init_feedback(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args)
    path = feedback_dir(repo_root) / "README.md"
    if not path.exists():
        write_markdown_bom(path, feedback_readme())
    return {"feedback_readme": relative_to_repo(repo_root, path)}


def feedback_readme() -> str:
    return """# Workflow Feedback

`work/feedback/` は、Self-Improvement Workflowの実行時Feedback report置き場です。

細かい `inbox/`、`aggregated/`、`processed/`、`icebox/` は作りません。
各Feedback reportに `Review Status` と `Human Check` を追記し、採用 / 不採用 / 保留を同じファイルで管理します。

標準作成:

```powershell
uv run --project runtime python runtime/ctl/ctl.py --repo-root . self-improvement create-feedback `
  --target-workflow "/docs-sync" `
  --reporter "Human" `
  --situation "docs整備中" `
  --friction "参照すべきdocsが不明" `
  --impact "判断負荷が増えた"
```
"""


def parse_runtime_event_log_line(line: str) -> dict[str, Any] | None:
    parts = line.rstrip("\n").split(" | ", 3)
    if len(parts) != 4:
        return None
    timestamp, trace_id, sequence_text, payload_text = parts
    try:
        sequence = int(sequence_text)
        payload = json.loads(payload_text)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return {
        "timestamp": timestamp,
        "trace_id": trace_id,
        "sequence": sequence,
        "payload": payload,
    }


def resolve_runtime_log_path(repo_root: Path, raw_log_path: str) -> Path:
    if raw_log_path:
        return resolve_path(repo_root, raw_log_path)
    return runtime_event_log_path(repo_root)


def load_runtime_event_log(repo_root: Path, *, runtime_log: str, runtime_trace_id: str) -> dict[str, Any]:
    log_path = resolve_runtime_log_path(repo_root, runtime_log)
    result: dict[str, Any] = {
        "log_path": log_path,
        "trace_id": runtime_trace_id.strip(),
        "events": [],
        "malformed_lines": 0,
        "status": "ok",
    }
    if not log_path.exists():
        result["status"] = "missing_log"
        return result

    events: list[dict[str, Any]] = []
    malformed = 0
    for line in log_path.read_text(encoding="utf-8-sig").splitlines():
        parsed = parse_runtime_event_log_line(line)
        if parsed is None:
            malformed += 1
            continue
        events.append(parsed)

    trace_id = result["trace_id"]
    if not trace_id and events:
        trace_id = str(events[-1]["trace_id"])
        result["trace_id"] = trace_id
        result["selected_latest_trace"] = True

    matched = [event for event in events if not trace_id or event["trace_id"] == trace_id]
    result["events"] = matched
    result["total_events"] = len(events)
    result["malformed_lines"] = malformed
    if trace_id and not matched:
        result["status"] = "missing_trace"
    elif not matched:
        result["status"] = "empty_log"
    return result


def _counter_text(counter: Counter[str]) -> str:
    if not counter:
        return "None"
    return ", ".join(f"{key}: {value}" for key, value in counter.items())


def summarize_runtime_events(log_data: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    events = list(log_data.get("events", []))
    commands: list[str] = []
    statuses: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    durations: list[int] = []
    problem_events: list[dict[str, Any]] = []

    for event in events:
        payload = event.get("payload", {})
        command = str(payload.get("command", "")).strip()
        if command and command not in commands:
            commands.append(command)
        output = payload.get("output", {})
        if isinstance(output, dict):
            status = str(output.get("status", "")).strip()
            reason = str(output.get("reason", "")).strip()
            if status:
                statuses[status] += 1
            if reason:
                reasons[reason] += 1
            duration = output.get("duration_ms")
            if isinstance(duration, int):
                durations.append(duration)
            exit_code = output.get("exit_code")
            if (status and status != "completed") or (isinstance(exit_code, int) and exit_code != 0):
                problem_events.append(event)

    if "blocked" in statuses:
        outcome = "blocked"
    elif problem_events:
        outcome = "failed"
    elif events:
        outcome = "completed"
    else:
        outcome = log_data.get("status", "empty_log")

    return {
        "log_path": relative_to_repo(repo_root, Path(log_data["log_path"])),
        "trace_id": log_data.get("trace_id", ""),
        "event_count": len(events),
        "total_events": log_data.get("total_events", len(events)),
        "malformed_lines": log_data.get("malformed_lines", 0),
        "commands": commands,
        "statuses": statuses,
        "reasons": reasons,
        "duration_total_ms": sum(durations),
        "duration_max_ms": max(durations) if durations else 0,
        "first_timestamp": events[0]["timestamp"] if events else "",
        "last_timestamp": events[-1]["timestamp"] if events else "",
        "problem_events": problem_events,
        "outcome": outcome,
        "status": log_data.get("status", "ok"),
        "selected_latest_trace": bool(log_data.get("selected_latest_trace")),
    }


def render_runtime_problem_events(events: list[dict[str, Any]]) -> str:
    if not events:
        return "- None"
    lines: list[str] = []
    for event in events[:SELF_IMPROVEMENT_EVENT_PREVIEW_LIMIT]:
        payload = event.get("payload", {})
        output = payload.get("output", {}) if isinstance(payload.get("output", {}), dict) else {}
        lines.append(
            "- "
            f"seq={event.get('sequence'):05d} "
            f"event={payload.get('event', '')} "
            f"command={payload.get('command', '')} "
            f"status={output.get('status', '')} "
            f"reason={output.get('reason', '')} "
            f"exit_code={output.get('exit_code', '')} "
            f"duration_ms={output.get('duration_ms', '')}"
        )
    if len(events) > 10:
        lines.append(f"- ... truncated: {len(events) - 10} events")
    return "\n".join(lines)


def render_runtime_log_sections(args: argparse.Namespace, repo_root: Path) -> str:
    runtime_log = getattr(args, "runtime_log", "")
    runtime_trace_id = getattr(args, "runtime_trace_id", "")
    if not runtime_log and not runtime_trace_id:
        return ""

    log_data = load_runtime_event_log(repo_root, runtime_log=runtime_log, runtime_trace_id=runtime_trace_id)
    summary = summarize_runtime_events(log_data, repo_root)
    trace_note = "latest trace in log" if summary["selected_latest_trace"] else "requested trace"
    commands = ", ".join(f"`{command}`" for command in summary["commands"]) if summary["commands"] else "None"
    window = (
        f"{summary['first_timestamp']} -> {summary['last_timestamp']}"
        if summary["first_timestamp"] and summary["last_timestamp"]
        else "None"
    )
    return f"""
## Runtime Observation

- Log: `{summary["log_path"]}`
- Trace ID: `{summary["trace_id"] or "None"}` ({trace_note})
- Events: {summary["event_count"]} / {summary["total_events"]}
- Malformed Lines: {summary["malformed_lines"]}
- Window: {window}
- Commands: {commands}
- Statuses: {_counter_text(summary["statuses"])}
- Reasons: {_counter_text(summary["reasons"])}
- Duration: total={summary["duration_total_ms"]}ms, max={summary["duration_max_ms"]}ms

## Runtime Log Analysis

- Outcome: `{summary["outcome"]}`
- Log Status: `{summary["status"]}`
- Blocked/Failed Events:
{render_runtime_problem_events(summary["problem_events"])}
"""


def render_feedback_report(args: argparse.Namespace) -> str:
    evidence = "\n".join(f"- {item}" for item in args.evidence) if args.evidence else "- None"
    repo_root = resolve_repo_root(args)
    runtime_sections = render_runtime_log_sections(args, repo_root)
    return f"""# Workflow Feedback

## Target Workflow

{args.target_workflow}

## Reporter

{args.reporter}

## Situation

{args.situation}

## Friction

{args.friction}

## Impact

{args.impact or "TBD"}

## Proposed Improvement

{args.proposed_improvement or "TBD"}

## Evidence

{evidence}
{runtime_sections}

## Review Status

Proposed

## Human Check

- Decision:
- Reviewer:
- Reviewed At:
- Reason:
- Next Action:

## Priority

{args.priority}

## Category

{args.category}
"""


def run_create_feedback(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args)
    run_init_feedback(args)
    output = Path(args.output) if args.output else feedback_dir(repo_root) / default_feedback_name(args.target_workflow)
    output = output if output.is_absolute() else repo_root / output
    write_markdown_bom(output, render_feedback_report(args))
    return {"feedback": relative_to_repo(repo_root, output), "status": "proposed"}


def default_feedback_name(target_workflow: str) -> str:
    return f"{local_timestamp()}-{slugify(target_workflow).lower()}-feedback.md"


def resolve_path(repo_root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else repo_root / path


def set_heading_body(text: str, heading: str, body: str) -> str:
    pattern = re.compile(rf"(^## {re.escape(heading)}\s*\n)(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    replacement = f"## {heading}\n\n{body.rstrip()}\n\n"
    if pattern.search(text):
        return pattern.sub(replacement, text, count=1)
    return text.rstrip() + "\n\n" + replacement


def append_review_record(text: str, *, decision: str, reviewer: str, reason: str, next_action: str) -> str:
    body = "\n".join(
        [
            f"- Decision: {decision.title()}",
            f"- Reviewer: {reviewer}",
            f"- Reviewed At: {utc_now_iso()}",
            f"- Reason: {reason}",
            f"- Next Action: {next_action or 'None'}",
        ]
    )
    text = set_heading_body(text, "Review Status", decision.title())
    return set_heading_body(text, "Human Check", body)


def run_review_feedback(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args)
    path = resolve_path(repo_root, args.feedback)
    if not path.exists():
        raise FileNotFoundError(f"Feedback report does not exist: {path}")
    updated = append_review_record(
        path.read_text(encoding="utf-8-sig"),
        decision=args.decision,
        reviewer=args.reviewer,
        reason=args.reason,
        next_action=args.next_action,
    )
    write_markdown_bom(path, updated)
    return {"feedback": relative_to_repo(repo_root, path), "decision": args.decision}


def extract_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"^## (?P<title>.+?)\s*$", markdown, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[match.group("title").strip()] = markdown[start:end].strip()
    return sections


def feedback_decision(sections: dict[str, str]) -> str:
    status = sections.get("Review Status", "").strip().lower()
    if status in {"accepted", "rejected", "deferred"}:
        return status
    human_check = sections.get("Human Check", "").lower()
    for decision in VALID_DECISIONS:
        if f"decision: {decision}" in human_check:
            return decision
    return "proposed"


def build_issue_body_from_feedback(markdown: str, feedback_path: str) -> str:
    sections = extract_sections(markdown)
    target = sections.get("Target Workflow", "")
    category = sections.get("Category", "")
    priority = sections.get("Priority", "")
    title = sections.get("Proposed Improvement", "").splitlines()[0].strip() or "Workflow feedback improvement"
    return f"""# Self-Improvement Issue

## Summary

{title}

## Background

Target workflow: `{target}`

Situation:

{sections.get("Situation", "TBD")}

## Problem

{sections.get("Friction", "TBD")}

## Impact

{sections.get("Impact", "TBD")}

## Proposed Change

{sections.get("Proposed Improvement", "TBD")}

## Scope

- Workflow: `{target}`
- Category: `{category}`
- Priority: `{priority}`

## Ariadne Fit Check

- [ ] AIが迷わない環境に寄与するか
- [ ] 認知負荷を下げるか
- [ ] 品質を支える仕組みになるか
- [ ] 維持しやすいか
- [ ] 改善しやすいか
- [ ] 運用可能か
- [ ] 責務を曖昧にしないか
- [ ] Human Responsibilityを曖昧にしないか
- [ ] Ariadneの思想と矛盾しないか

## Acceptance Criteria

- [ ] 改善対象が明確である
- [ ] Ariadneの設計思想に反していない
- [ ] AIが迷わない環境に寄与している
- [ ] Human Responsibilityを曖昧にしていない
- [ ] 既存Workflowを壊していない
- [ ] 必要なDocsが更新されている
- [ ] 必要なテストが追加・更新されている
- [ ] Evidenceが保存されている

## Source Feedback

- `{feedback_path}`

## Related Evidence

{sections.get("Evidence", "- None")}
"""


def run_issue_body(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args)
    feedback_path = resolve_path(repo_root, args.feedback)
    if not feedback_path.exists():
        raise FileNotFoundError(f"Feedback report does not exist: {feedback_path}")
    markdown = feedback_path.read_text(encoding="utf-8-sig")
    sections = extract_sections(markdown)
    decision = feedback_decision(sections)
    if decision != "accepted" and not args.allow_unaccepted:
        raise RuntimeError("Feedback must be accepted before Issue body generation.")
    output = (
        resolve_path(repo_root, args.output)
        if args.output
        else feedback_path.with_name(feedback_path.stem + "-issue-body.md")
    )
    relative_feedback = relative_to_repo(repo_root, feedback_path)
    write_markdown_bom(output, build_issue_body_from_feedback(markdown, relative_feedback))
    return {
        "issue_body": relative_to_repo(repo_root, output),
        "feedback": relative_feedback,
        "decision": decision,
        "recommended_title": f"self-improvement: {slugify(sections.get('Proposed Improvement', 'workflow-feedback'))}",
    }


def run_branch_name(args: argparse.Namespace) -> dict[str, Any]:
    issue = str(args.issue_number).strip().lstrip("#")
    if not issue.isdigit():
        raise ValueError("issue-number must be numeric.")
    return {"issue_number": issue, "branch": f"feature/issue-{issue}", "work_id": f"issue-{issue}"}


def run_evidence_scaffold(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = resolve_repo_root(args)
    work_dir = work_dir_for_id(repo_root, args.work_id)
    process_dir = process_report_dir_for_work_dir(work_dir) / "self-improvement"
    evidence_dir = test_evidence_dir_for_work_dir(work_dir) / "self-improvement"
    context_dir = context_dir_for_work_dir(work_dir)
    process_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    context_dir.mkdir(parents=True, exist_ok=True)
    summary_path = process_dir / "README.md"
    if not summary_path.exists():
        write_markdown_bom(summary_path, "# Self-Improvement Process Report\n\nHuman Check、Issue本文、採用判断、変更範囲を保存します。\n")
    evidence_readme = evidence_dir / "README.md"
    if not evidence_readme.exists():
        write_markdown_bom(evidence_readme, "# Self-Improvement Test Evidence\n\n検証コマンド、結果、失敗時の保持情報を保存します。\n")
    index = load_artifact_index(work_dir, args.work_id, "self-improvement")
    now = utc_now_iso()
    for artifact_id, title, path in [
        ("SELF-IMPROVEMENT-PROCESS", "Self-Improvement Process Report", summary_path),
        ("SELF-IMPROVEMENT-EVIDENCE", "Self-Improvement Test Evidence", evidence_readme),
    ]:
        upsert_artifact(
            index,
            {
                "id": artifact_id,
                "title": title,
                "path": relative_to_repo(repo_root, path),
                "type": "report",
                "status": "draft",
                "owner_agent": "self-improvement",
                "created_at": now,
                "updated_at": now,
                "depends_on": [],
                "consumed_by": ["knowledge-capture"],
                "summary": title,
                "unresolved_items": [],
            },
        )
    artifact_index_path = context_dir / "artifact-index.json"
    write_json(artifact_index_path, index)
    register_context(
        repo_root,
        work_dir,
        work_id=args.work_id,
        context_type="artifact-index",
        path=artifact_index_path,
        required=True,
        generated_by="self-improvement",
        owner="workflow",
        schema=ARTIFACT_INDEX_SCHEMA,
    )
    return {
        "work_id": args.work_id,
        "process_report": relative_to_repo(repo_root, process_dir),
        "test_evidence": relative_to_repo(repo_root, evidence_dir),
        "artifact_index": relative_to_repo(repo_root, artifact_index_path),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    return args.handler(args)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
