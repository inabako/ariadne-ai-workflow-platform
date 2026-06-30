from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    default_github_owner,
    ensure_work_tree,
    find_repo_root,
    load_artifact_index,
    load_env,
    local_timestamp,
    normalize_repository_value,
    read_json,
    relative_to_repo,
    repository_to_github_slug,
    slugify,
    upsert_artifact,
    utc_now_iso,
    write_json,
    write_markdown_bom,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Documentation sync workflow helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize docs-sync work context.")
    init_parser.add_argument("--repository", required=True)
    init_parser.add_argument("--target-branch", required=True)
    init_parser.add_argument("--work-id", default=None)
    init_parser.add_argument("--base-work-id", default="")
    init_parser.add_argument("--reuse-existing", action="store_true")
    init_parser.add_argument("--intent-summary", default="")
    init_parser.add_argument("--repo-root", default=None)

    template_parser = subparsers.add_parser("analysis-template", help="Create a docs drift analysis JSON scaffold.")
    template_parser.add_argument("--work-id", required=True)
    template_parser.add_argument("--analysis-path", default="")
    template_parser.add_argument("--repo-root", default=None)

    issue_parser = subparsers.add_parser("issue-body", help="Create a GitHub Issue body from docs drift analysis JSON.")
    issue_parser.add_argument("--work-id", required=True)
    issue_parser.add_argument("--analysis-path", default="")
    issue_parser.add_argument("--output", default="")
    issue_parser.add_argument("--repo-root", default=None)
    return parser


def branch_to_work_id(branch_name: str) -> str:
    return slugify(branch_name.replace("\\", "/").strip("/").replace("/", "-"))


def repository_name(repository: str, default_owner: str = "") -> str:
    slug = repository_to_github_slug(repository, default_owner)
    if slug:
        name = slug.rsplit("/", 1)[-1]
    else:
        name = Path(repository.replace("\\", "/").rstrip("/")).name
    if name.endswith(".git"):
        name = name[:-4]
    return slugify(name)


def init_work(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    repository = normalize_repository_value(args.repository)
    repo_name = repository_name(repository, default_github_owner(settings))
    work_id = args.work_id or branch_to_work_id(args.target_branch)
    work_dir = repo_root / "work" / work_id
    if work_dir.exists() and not args.reuse_existing:
        raise FileExistsError(
            f"Work directory already exists: {work_dir}. Confirm reuse, then rerun with --reuse-existing."
        )
    work_dir = ensure_work_tree(repo_root, work_id)
    context_dir = work_dir / "context"
    now = utc_now_iso()
    intent_summary = args.intent_summary or (
        f"Synchronize docs with implementation for {repository} {args.target_branch}."
    )

    agent_context = {
        "schema_version": "1.0",
        "project": {
            "name": repo_name,
            "repository": repository,
            "environment": "",
        },
        "workflow": {
            "name": "docs-sync",
            "phase": "initialization",
            "risk_level": "low",
            "command": "/docs-sync",
        },
        "agent": {
            "name": "runtime-workflow",
            "role": "documentation sync workflow initialization",
            "input_artifacts": [],
            "output_artifacts": [
                relative_to_repo(repo_root, context_dir / "agent-context.json"),
                relative_to_repo(repo_root, context_dir / "artifact-index.json"),
            ],
        },
        "intent": {
            "summary": intent_summary,
            "non_goals": [
                "Do not change implementation code.",
                "Do not treat docs as authoritative when they conflict with implementation evidence.",
            ],
            "success_criteria": [
                "Docs drift analysis JSON is created.",
                "GitHub Issue is created from the JSON.",
                "Docs-only changes are committed on feature/issue-<number>.",
                "RAG candidates and archive readiness are prepared after push.",
            ],
        },
        "safety_context": {
            "stop_behavior_known": False,
            "communication_loss_behavior_known": False,
            "startup_safe_state_known": False,
            "shutdown_safe_state_known": False,
            "field_trial_allowed": False,
            "open_safety_questions": [
                "Confirm whether docs drift touches STOP, control authority, startup, shutdown, or communication loss behavior.",
            ],
        },
        "assumptions": [
            f"work_id={work_id}",
            f"base_work_id={args.base_work_id}" if args.base_work_id else "base_work_id=",
            f"target_repository={repository}",
            f"target_branch={args.target_branch}",
        ],
        "constraints": [
            "Do not edit files in the base checkout.",
            "Do not change implementation code in the issue branch.",
            "Do not push until human approval is recorded.",
            "Do not run RAG registration or close archive prepare/prune without human approval.",
        ],
    }
    write_json(context_dir / "agent-context.json", agent_context)
    for filename, value in [
        ("qa-records.json", []),
        ("finding-records.json", []),
        ("decision-records.json", []),
        ("test-evidence.json", []),
    ]:
        write_json(context_dir / filename, value)

    write_json(
        context_dir / "handoff-package.json",
        {
            "schema_version": "1.0",
            "from_agent": "runtime-workflow",
            "to_agent": "docs-drift-analyzer",
            "workflow": "docs-sync",
            "phase": "initialization",
            "intent": intent_summary,
            "summary": f"Initialized docs-sync work area {work_id}.",
            "decisions": [],
            "artifacts": [],
            "open_questions": agent_context["safety_context"]["open_safety_questions"],
            "risks": [],
            "required_next_actions": [
                "Prepare target repository and branch.",
                "Compare implementation and docs.",
                "Write docs-drift-analysis.json before Issue creation.",
            ],
            "stop_conditions": [
                "Stop before GitHub mutation, push, RAG registration, or close archive prepare/prune until human approval.",
            ],
        },
    )

    index = load_artifact_index(work_dir, repo_name, "docs-sync")
    upsert_artifact(
        index,
        {
            "id": "AGENT-CONTEXT",
            "title": "Docs Sync Context",
            "path": relative_to_repo(repo_root, context_dir / "agent-context.json"),
            "type": "other",
            "status": "draft",
            "owner_agent": "runtime-workflow",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["docs-drift-analyzer"],
            "summary": "Workflow context for documentation sync.",
            "unresolved_items": [],
        },
    )
    write_json(context_dir / "artifact-index.json", index)
    return {
        "work_id": work_id,
        "work_dir": relative_to_repo(repo_root, work_dir),
        "repository": repository,
        "target_branch": args.target_branch,
        "base_work_id": args.base_work_id,
    }


def default_analysis(work_dir: Path, repo_root: Path) -> dict[str, Any]:
    context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    scm_state = read_json(work_dir / "context" / "scm-state.json", default={}) or {}
    repository = scm_state.get("repository") or context.get("project", {}).get("repository", "")
    target_branch = scm_state.get("target_branch") or scm_state.get("current_branch") or ""
    docs_root = Path(scm_state.get("source_dir", "")) / "docs" if scm_state.get("source_dir") else work_dir / "source" / "repository" / "docs"
    return {
        "schema_version": "1.0",
        "workflow": "docs-sync",
        "work_id": work_dir.name,
        "repository": repository,
        "target_branch": target_branch,
        "source_commit": scm_state.get("current_commit", ""),
        "docs_root": relative_to_repo(repo_root, docs_root if docs_root.is_absolute() else repo_root / docs_root),
        "generated_at": utc_now_iso(),
        "summary": "TBD: summarize implementation/docs drift.",
        "implementation_sources": [],
        "docs_sources": [],
        "rag_context_refs": [],
        "issue_recommendation": {
            "title": "docs: sync documentation with implementation",
            "labels": ["documentation"],
            "acceptance_summary": "Docs reflect current implementation behavior and setup steps.",
        },
        "guardrails": [
            "Docs-only change.",
            "Do not change implementation code.",
            "Use implementation evidence as source of truth when docs conflict.",
        ],
        "drift_items": [],
        "open_questions": [],
    }


def create_analysis_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    analysis_path = Path(args.analysis_path).resolve() if args.analysis_path else work_dir / "context" / "docs-drift-analysis.json"
    analysis = default_analysis(work_dir, repo_root)
    write_json(analysis_path, analysis)
    register_analysis_artifact(repo_root, work_dir, analysis_path, "draft")
    return {
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "drift_item_count": 0,
    }


def register_analysis_artifact(repo_root: Path, work_dir: Path, analysis_path: Path, status: str) -> None:
    context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    project_name = context.get("project", {}).get("name", work_dir.name)
    index = load_artifact_index(work_dir, project_name, "docs-sync")
    now = utc_now_iso()
    upsert_artifact(
        index,
        {
            "id": "DOCS-DRIFT-ANALYSIS",
            "title": "Docs Drift Analysis",
            "path": relative_to_repo(repo_root, analysis_path),
            "type": "report",
            "status": status,
            "owner_agent": "docs-drift-analyzer",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["runtime-github", "docs-sync"],
            "summary": "Structured implementation/docs drift analysis.",
            "unresolved_items": [],
        },
    )
    write_json(work_dir / "context" / "artifact-index.json", index)


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def evidence_lines(evidence: list[dict[str, Any]]) -> str:
    if not evidence:
        return "- None"
    lines = []
    for item in evidence:
        path = item.get("path", "")
        reason = item.get("reason", "")
        symbol = item.get("symbol", "")
        suffix = f" ({symbol})" if symbol else ""
        lines.append(f"- `{path}`{suffix}: {reason}")
    return "\n".join(lines)


def build_issue_body(analysis: dict[str, Any]) -> str:
    recommendation = analysis.get("issue_recommendation", {}) or {}
    drift_items = analysis.get("drift_items", []) or []
    open_questions = analysis.get("open_questions", []) or []
    lines = [
        "## Intent",
        "",
        analysis.get("summary", "Synchronize docs with implementation."),
        "",
        "## Repository",
        "",
        f"- Repository: `{analysis.get('repository', '')}`",
        f"- Target branch: `{analysis.get('target_branch', '')}`",
        f"- Source commit: `{analysis.get('source_commit', '')}`",
        f"- Docs root: `{analysis.get('docs_root', '')}`",
        "",
        "## Guardrails",
        "",
        markdown_list(analysis.get("guardrails", []) or ["Docs-only change."]),
        "",
        "## Drift Items",
        "",
    ]
    if not drift_items:
        lines.append("- No drift items recorded. Update docs-drift-analysis.json before creating an Issue.")
    for item in drift_items:
        lines.extend(
            [
                f"### {item.get('id', 'DOCS-XXX')}: {item.get('title', 'Untitled')}",
                "",
                f"- Severity: `{item.get('severity', 'unknown')}`",
                f"- Status: `{item.get('status', 'unknown')}`",
                f"- Area: `{item.get('area', '')}`",
                "",
                "Implementation evidence:",
                "",
                evidence_lines(item.get("implementation_evidence", []) or []),
                "",
                "Docs evidence:",
                "",
                evidence_lines(item.get("docs_evidence", []) or []),
                "",
                "Expected docs updates:",
                "",
                markdown_list(item.get("expected_doc_updates", []) or []),
                "",
                "Acceptance criteria:",
                "",
                markdown_list(item.get("acceptance_criteria", []) or []),
                "",
            ]
        )
        if item.get("issue_body_note"):
            lines.extend(["Note:", "", str(item["issue_body_note"]), ""])
    lines.extend(
        [
            "## Open Questions",
            "",
        ]
    )
    if not open_questions:
        lines.append("- None")
    else:
        for question in open_questions:
            lines.append(
                f"- `{question.get('id', 'Q-XXX')}` {question.get('question', '')} "
                f"(blocks: {question.get('blocks', False)})"
            )
    lines.extend(
        [
            "",
            "## Acceptance Summary",
            "",
            recommendation.get("acceptance_summary", "Docs reflect the current implementation."),
            "",
            "## Source Artifact",
            "",
            "- `work/<target-branch>/context/docs-drift-analysis.json`",
        ]
    )
    return "\n".join(lines)


def create_issue_body(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    analysis_path = Path(args.analysis_path).resolve() if args.analysis_path else work_dir / "context" / "docs-drift-analysis.json"
    if not analysis_path.exists():
        raise FileNotFoundError(f"Docs drift analysis does not exist: {analysis_path}")
    analysis = read_json(analysis_path)
    drift_items = analysis.get("drift_items", []) if isinstance(analysis, dict) else []
    output_path = (
        Path(args.output).resolve()
        if args.output
        else work_dir / "process-report" / f"docs-sync-issue-body-{local_timestamp()}.md"
    )
    write_markdown_bom(output_path, build_issue_body(analysis))
    register_analysis_artifact(repo_root, work_dir, analysis_path, "draft")
    return {
        "issue_body": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "drift_item_count": len(drift_items),
        "recommended_title": (analysis.get("issue_recommendation", {}) or {}).get(
            "title", "docs: sync documentation with implementation"
        ),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "init":
        return init_work(args)
    if args.command == "analysis-template":
        return create_analysis_template(args)
    if args.command == "issue-body":
        return create_issue_body(args)
    raise ValueError(f"Unsupported command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
