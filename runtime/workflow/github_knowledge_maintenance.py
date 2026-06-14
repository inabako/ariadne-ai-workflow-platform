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


SCAN_MODES = ["repository", "issue", "pull-request", "recent", "full"]
REPAIR_MODES = ["proposal", "apply"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GitHub repository knowledge maintenance workflow helper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize GitHub knowledge maintenance context.")
    init_parser.add_argument("--repository", required=True, help="GitHub repository URL, slug, or repository name.")
    init_parser.add_argument("--target-branch", default="", help="Optional branch used as scan context.")
    init_parser.add_argument(
        "--scan-mode",
        nargs="+",
        choices=SCAN_MODES,
        default=["recent"],
        help="Scan modes to include in the collection plan.",
    )
    init_parser.add_argument("--repair-mode", choices=REPAIR_MODES, default="proposal")
    init_parser.add_argument("--rag-output", action="store_true", help="Prepare RAG candidate outputs.")
    init_parser.add_argument("--work-id", default=None)
    init_parser.add_argument("--reuse-existing", action="store_true")
    init_parser.add_argument("--intent-summary", default="")
    init_parser.add_argument("--repo-root", default=None)

    analysis_parser = subparsers.add_parser(
        "analysis-template", help="Create a GitHub knowledge analysis JSON scaffold."
    )
    analysis_parser.add_argument("--work-id", required=True)
    analysis_parser.add_argument("--analysis-path", default="")
    analysis_parser.add_argument("--repo-root", default=None)

    repair_parser = subparsers.add_parser("repair-plan", help="Create a human review repair plan from analysis JSON.")
    repair_parser.add_argument("--work-id", required=True)
    repair_parser.add_argument("--analysis-path", default="")
    repair_parser.add_argument("--output", default="")
    repair_parser.add_argument("--repo-root", default=None)

    sync_parser = subparsers.add_parser(
        "github-sync-plan", help="Create an approval-gated GitHub CLI/API sync plan from analysis JSON."
    )
    sync_parser.add_argument("--work-id", required=True)
    sync_parser.add_argument("--analysis-path", default="")
    sync_parser.add_argument("--output", default="")
    sync_parser.add_argument("--repo-root", default=None)

    rag_parser = subparsers.add_parser("rag-candidate", help="Create a RAG candidate note from analysis JSON.")
    rag_parser.add_argument("--work-id", required=True)
    rag_parser.add_argument("--analysis-path", default="")
    rag_parser.add_argument("--topic", default="")
    rag_parser.add_argument("--output", default="")
    rag_parser.add_argument("--publish-rag", action="store_true")
    rag_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    rag_parser.add_argument("--repo-root", default=None)
    return parser


def repository_name(repository: str, default_owner: str = "") -> str:
    slug = repository_to_github_slug(repository, default_owner)
    if slug:
        name = slug.rsplit("/", 1)[-1]
    else:
        name = Path(repository.replace("\\", "/").rstrip("/")).name
    if name.endswith(".git"):
        name = name[:-4]
    return slugify(name)


def default_work_id(repository: str, scan_mode: list[str], default_owner: str = "") -> str:
    repo_name = repository_name(repository, default_owner)
    mode = "full" if "full" in scan_mode else scan_mode[0]
    return f"github-knowledge-{repo_name}-{mode}"


def init_work(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    repository = normalize_repository_value(args.repository)
    repo_name = repository_name(repository, default_github_owner(settings))
    work_id = args.work_id or default_work_id(repository, args.scan_mode, default_github_owner(settings))
    work_dir = repo_root / "work" / work_id
    if work_dir.exists() and not args.reuse_existing:
        raise FileExistsError(
            f"Work directory already exists: {work_dir}. Confirm reuse, then rerun with --reuse-existing."
        )

    work_dir = ensure_work_tree(repo_root, work_id)
    context_dir = work_dir / "context"
    now = utc_now_iso()
    intent_summary = args.intent_summary or (
        f"Maintain GitHub knowledge assets for {repository} without changing Git history."
    )
    scan_modes = sorted(set(args.scan_mode), key=args.scan_mode.index)

    agent_context = {
        "schema_version": "1.0",
        "project": {
            "name": repo_name,
            "repository": repository,
            "environment": "",
        },
        "workflow": {
            "name": "github-knowledge-maintenance",
            "phase": "initialization",
            "risk_level": "low",
            "command": "/github-knowledge-maintenance",
        },
        "agent": {
            "name": "runtime-workflow",
            "role": "GitHub repository knowledge maintenance initialization",
            "input_artifacts": [],
            "output_artifacts": [
                relative_to_repo(repo_root, context_dir / "agent-context.json"),
                relative_to_repo(repo_root, context_dir / "artifact-index.json"),
            ],
        },
        "intent": {
            "summary": intent_summary,
            "non_goals": [
                "Do not rewrite Git history.",
                "Do not alter source code.",
                "Do not clone the repository unless GitHub CLI/API evidence is insufficient and the human approves.",
            ],
            "success_criteria": [
                "GitHub metadata collection plan is explicit.",
                "Knowledge assets and narrative gaps are recorded as JSON.",
                "Human-reviewed repair proposals are prepared.",
                "Approved GitHub documentation sync actions are separated from draft proposals.",
                "Knowledge DB and RAG candidates are generated when requested.",
            ],
        },
        "assumptions": [
            f"work_id={work_id}",
            f"target_repository={repository}",
            f"target_branch={args.target_branch}",
            f"scan_mode={','.join(scan_modes)}",
            f"repair_mode={args.repair_mode}",
            f"rag_output={bool(args.rag_output)}",
        ],
        "constraints": [
            "Git history is historical evidence and must not be rewritten.",
            "GitHub mutations require explicit human approval.",
            "Repair mode 'proposal' may not execute gh edit/comment commands.",
            "Repair mode 'apply' still requires item-level human approval before each mutation.",
            "Clone requires explicit human approval and a recorded reason.",
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
            "to_agent": "repository-discovery-agent",
            "workflow": "github-knowledge-maintenance",
            "phase": "initialization",
            "intent": intent_summary,
            "summary": f"Initialized GitHub knowledge maintenance work area {work_id}.",
            "decisions": [],
            "artifacts": [],
            "open_questions": [
                "Confirm whether GitHub mutation is allowed for this run.",
                "Confirm whether clone is allowed if GitHub API evidence is incomplete.",
            ],
            "risks": [],
            "required_next_actions": [
                "Create the analysis scaffold.",
                "Collect GitHub metadata with gh issue/pr/api commands.",
                "Record knowledge assets, narrative gaps, and repair proposals in JSON.",
            ],
            "stop_conditions": [
                "Stop before GitHub mutation until human approval is recorded.",
                "Stop before clone until human approval and reason are recorded.",
            ],
        },
    )

    index = load_artifact_index(work_dir, repo_name, "github-knowledge-maintenance")
    upsert_artifact(
        index,
        {
            "id": "AGENT-CONTEXT",
            "title": "GitHub Knowledge Maintenance Context",
            "path": relative_to_repo(repo_root, context_dir / "agent-context.json"),
            "type": "other",
            "status": "draft",
            "owner_agent": "runtime-workflow",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["repository-discovery-agent", "github-metadata-collector"],
            "summary": "Workflow context for GitHub repository knowledge maintenance.",
            "unresolved_items": [],
        },
    )
    write_json(context_dir / "artifact-index.json", index)
    return {
        "work_id": work_id,
        "work_dir": relative_to_repo(repo_root, work_dir),
        "repository": repository,
        "target_branch": args.target_branch,
        "scan_mode": scan_modes,
        "repair_mode": args.repair_mode,
        "rag_output": bool(args.rag_output),
    }


def default_analysis(work_dir: Path) -> dict[str, Any]:
    context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    assumptions = context.get("assumptions", [])
    assumption_map = {}
    for item in assumptions:
        if isinstance(item, str) and "=" in item:
            key, value = item.split("=", 1)
            assumption_map[key] = value
    return {
        "schema_version": "1.0",
        "workflow": "github-knowledge-maintenance",
        "work_id": work_dir.name,
        "repository": context.get("project", {}).get("repository", ""),
        "target_branch": assumption_map.get("target_branch", ""),
        "scan_mode": [mode for mode in assumption_map.get("scan_mode", "recent").split(",") if mode],
        "repair_mode": assumption_map.get("repair_mode", "proposal"),
        "rag_output": assumption_map.get("rag_output", "False").lower() == "true",
        "generated_at": utc_now_iso(),
        "summary": "TBD: summarize GitHub repository knowledge maintenance findings.",
        "collection_plan": [
            {
                "id": "COLLECT-001",
                "source_type": "issue",
                "command": "gh issue list --repo <owner/repo> --state all --limit 100",
                "purpose": "Collect issue intent and maintenance context.",
                "status": "planned",
            },
            {
                "id": "COLLECT-002",
                "source_type": "pull-request",
                "command": "gh pr list --repo <owner/repo> --state all --limit 100",
                "purpose": "Collect PR implementation narratives and review context.",
                "status": "planned",
            },
        ],
        "metadata_sources": [],
        "knowledge_assets": [],
        "narrative_gaps": [],
        "repair_proposals": [],
        "github_sync_actions": [],
        "knowledge_db_candidates": [],
        "rag_candidates": [],
        "open_questions": [],
        "guardrails": [
            "Do not rewrite Git history.",
            "Do not change source code.",
            "Do not run gh edit/comment/api mutation commands without human approval.",
            "Prefer GitHub CLI/API collection; clone only with explicit approval.",
        ],
    }


def analysis_path_for(work_dir: Path, raw_path: str) -> Path:
    return Path(raw_path).resolve() if raw_path else work_dir / "context" / "github-knowledge-analysis.json"


def register_artifact(repo_root: Path, work_dir: Path, artifact_id: str, title: str, path: Path, artifact_type: str) -> None:
    context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    project_name = context.get("project", {}).get("name", work_dir.name)
    index = load_artifact_index(work_dir, project_name, "github-knowledge-maintenance")
    now = utc_now_iso()
    upsert_artifact(
        index,
        {
            "id": artifact_id,
            "title": title,
            "path": relative_to_repo(repo_root, path),
            "type": artifact_type,
            "status": "draft",
            "owner_agent": "github-knowledge-maintenance",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["documentation-repair-agent", "knowledge-db-registrar"],
            "summary": title,
            "unresolved_items": [],
        },
    )
    write_json(work_dir / "context" / "artifact-index.json", index)


def create_analysis_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    output_path = analysis_path_for(work_dir, args.analysis_path)
    analysis = default_analysis(work_dir)
    write_json(output_path, analysis)
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-ANALYSIS", "GitHub Knowledge Analysis", output_path, "report")
    return {
        "analysis_path": relative_to_repo(repo_root, output_path),
        "knowledge_asset_count": 0,
        "narrative_gap_count": 0,
    }


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def field_list(items: list[dict[str, Any]], fields: list[str]) -> str:
    if not items:
        return "- None"
    lines: list[str] = []
    for item in items:
        title = item.get("title") or item.get("id") or "Untitled"
        lines.append(f"### {title}")
        lines.append("")
        for field in fields:
            value = item.get(field, "")
            if isinstance(value, list):
                value_text = markdown_list([str(entry) for entry in value])
                lines.extend([f"{field}:", "", value_text, ""])
            else:
                lines.append(f"- {field}: {value}")
        lines.append("")
    return "\n".join(lines).rstrip()


def load_analysis(repo_root: Path, work_id: str, raw_path: str) -> tuple[Path, Path, dict[str, Any]]:
    work_dir = repo_root / "work" / work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    path = analysis_path_for(work_dir, raw_path)
    if not path.exists():
        raise FileNotFoundError(f"GitHub knowledge analysis does not exist: {path}")
    analysis = read_json(path)
    if not isinstance(analysis, dict):
        raise ValueError(f"GitHub knowledge analysis must be a JSON object: {path}")
    return work_dir, path, analysis


def build_repair_plan(analysis: dict[str, Any]) -> str:
    proposals = analysis.get("repair_proposals", []) or []
    gaps = analysis.get("narrative_gaps", []) or []
    return "\n".join(
        [
            "# GitHub Knowledge Repair Plan",
            "",
            "## Intent",
            "",
            analysis.get("summary", "Maintain GitHub repository knowledge assets."),
            "",
            "## Repository",
            "",
            f"- Repository: `{analysis.get('repository', '')}`",
            f"- Target branch: `{analysis.get('target_branch', '')}`",
            f"- Repair mode: `{analysis.get('repair_mode', 'proposal')}`",
            "",
            "## Guardrails",
            "",
            markdown_list(analysis.get("guardrails", []) or []),
            "",
            "## Narrative Gaps",
            "",
            field_list(gaps, ["asset_ref", "gap_type", "severity", "evidence", "why_it_matters"]),
            "",
            "## Repair Proposals",
            "",
            field_list(proposals, ["target", "proposal_type", "reason", "before_summary", "after_summary", "approval_required"]),
            "",
            "## Human Review Checklist",
            "",
            "- Confirm each repair reason.",
            "- Confirm each target Issue, PR, comment, CAR, README, docs, or ADR.",
            "- Confirm before/after summary.",
            "- Confirm Git history will not change.",
            "- Confirm exact GitHub CLI/API command before execution.",
        ]
    )


def create_repair_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    output_path = (
        Path(args.output).resolve()
        if args.output
        else work_dir / "process-report" / f"github-knowledge-repair-plan-{local_timestamp()}.md"
    )
    write_markdown_bom(output_path, build_repair_plan(analysis))
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-REPAIR-PLAN", "GitHub Knowledge Repair Plan", output_path, "report")
    return {
        "repair_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "proposal_count": len(analysis.get("repair_proposals", []) or []),
    }


def build_sync_plan(analysis: dict[str, Any]) -> str:
    actions = analysis.get("github_sync_actions", []) or []
    lines = [
        "# GitHub Documentation Sync Plan",
        "",
        "This plan is not approval by itself. Run only the commands approved by the human reviewer.",
        "",
        "## Repository",
        "",
        f"- Repository: `{analysis.get('repository', '')}`",
        f"- Target branch: `{analysis.get('target_branch', '')}`",
        "",
        "## Proposed GitHub Actions",
        "",
    ]
    if not actions:
        lines.append("- None")
    for action in actions:
        lines.extend(
            [
                f"### {action.get('id', 'SYNC-XXX')}: {action.get('title', 'Untitled')}",
                "",
                f"- Target type: `{action.get('target_type', '')}`",
                f"- Target id: `{action.get('target_id', '')}`",
                f"- Operation: `{action.get('operation', '')}`",
                f"- Approval status: `{action.get('approval_status', 'pending')}`",
                "",
                "Reason:",
                "",
                action.get("reason", ""),
                "",
                "Draft command:",
                "",
                "```powershell",
                action.get("draft_command", "# Update github-knowledge-analysis.json with the exact gh command."),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Stop Rules",
            "",
            "- Do not execute commands marked `pending`.",
            "- Do not run commands that alter Git history.",
            "- Do not use `git rebase`, `git commit --amend`, or force push.",
            "- If the target or command differs from this plan, update the analysis JSON and re-review.",
        ]
    )
    return "\n".join(lines)


def create_sync_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    output_path = (
        Path(args.output).resolve()
        if args.output
        else work_dir / "process-report" / f"github-documentation-sync-plan-{local_timestamp()}.md"
    )
    write_markdown_bom(output_path, build_sync_plan(analysis))
    register_artifact(repo_root, work_dir, "GITHUB-DOCUMENTATION-SYNC-PLAN", "GitHub Documentation Sync Plan", output_path, "report")
    return {
        "sync_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "action_count": len(analysis.get("github_sync_actions", []) or []),
    }


def build_rag_candidate(analysis: dict[str, Any], topic: str) -> str:
    title = topic or f"github-knowledge-{repository_name(analysis.get('repository', 'repository'))}"
    return "\n".join(
        [
            "---",
            "schema_version: '1.0'",
            "document_type: github-repository-knowledge",
            f"repository: {analysis.get('repository', '')}",
            f"branch: {analysis.get('target_branch', '')}",
            "status: candidate",
            f"created_at: {utc_now_iso()}",
            "source: github-knowledge-maintenance",
            "---",
            "",
            f"# {title}",
            "",
            "## Summary",
            "",
            analysis.get("summary", ""),
            "",
            "## Knowledge Assets",
            "",
            field_list(analysis.get("knowledge_assets", []) or [], ["asset_type", "source_ref", "intent", "reuse_value"]),
            "",
            "## Narrative Gaps",
            "",
            field_list(analysis.get("narrative_gaps", []) or [], ["asset_ref", "gap_type", "severity", "why_it_matters"]),
            "",
            "## Repair Proposals",
            "",
            field_list(analysis.get("repair_proposals", []) or [], ["target", "proposal_type", "reason", "approval_required"]),
            "",
            "## RAG Candidates",
            "",
            field_list(analysis.get("rag_candidates", []) or [], ["candidate_type", "source_ref", "knowledge_value", "limits"]),
            "",
            "## Open Questions",
            "",
            field_list(analysis.get("open_questions", []) or [], ["question", "reason", "blocks"]),
        ]
    )


def create_rag_candidate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    if args.publish_rag and args.human_check != "approved":
        raise PermissionError("RAG publication requires --human-check approved.")
    topic = args.topic or f"github-knowledge-{repository_name(analysis.get('repository', 'repository'))}"
    if args.output:
        output_path = Path(args.output).resolve()
    elif args.publish_rag:
        output_path = repo_root / "rag" / "github-knowledge" / f"{local_timestamp()}_{slugify(topic)}.md"
    else:
        output_path = work_dir / "process-report" / f"github-knowledge-rag-candidate-{local_timestamp()}.md"
    write_markdown_bom(output_path, build_rag_candidate(analysis, topic))
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-RAG-CANDIDATE", "GitHub Knowledge RAG Candidate", output_path, "report")
    return {
        "rag_candidate": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "published": bool(args.publish_rag),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "init":
        return init_work(args)
    if args.command == "analysis-template":
        return create_analysis_template(args)
    if args.command == "repair-plan":
        return create_repair_plan(args)
    if args.command == "github-sync-plan":
        return create_sync_plan(args)
    if args.command == "rag-candidate":
        return create_rag_candidate(args)
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
