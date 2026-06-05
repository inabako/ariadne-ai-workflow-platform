from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    default_github_owner,
    ensure_work_tree,
    find_repo_root,
    load_env,
    load_artifact_index,
    normalize_repository_value,
    relative_to_repo,
    repository_to_github_slug,
    slugify,
    upsert_artifact,
    utc_now_iso,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize work/<id> for corrective action fix flow.")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--target-branch", required=True)
    parser.add_argument("--work-id", default=None)
    parser.add_argument("--base-work-id", default="")
    parser.add_argument("--reuse-existing", action="store_true")
    parser.add_argument("--report-path", default="")
    parser.add_argument("--intent-summary", default="")
    parser.add_argument("--repo-root", default=None)
    return parser


def branch_to_work_id(branch_name: str) -> str:
    value = branch_name.replace("\\", "/").strip("/")
    if value.startswith("feature/issue-"):
        value = value.rsplit("/", 1)[-1]
    return slugify(value.replace("/", "-"))


def repository_name(repository: str, default_owner: str = "") -> str:
    slug = repository_to_github_slug(repository, default_owner)
    if slug:
        name = slug.rsplit("/", 1)[-1]
    else:
        name = Path(repository.replace("\\", "/").rstrip("/")).name
    if name.endswith(".git"):
        name = name[:-4]
    return slugify(name)


def run(args: argparse.Namespace) -> dict[str, object]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    repository = normalize_repository_value(args.repository)
    repo_name = repository_name(repository, default_github_owner(settings))
    work_id = args.work_id or branch_to_work_id(args.target_branch)
    work_dir = repo_root / "work" / work_id
    if work_dir.exists() and not args.reuse_existing:
        raise FileExistsError(
            f"Work directory already exists: {work_dir}. "
            "原本または作業フォルダが既にあります。内容を確認してから、再利用する場合のみ --reuse-existing を指定してください。"
        )
    work_dir = ensure_work_tree(repo_root, work_id)
    context_dir = work_dir / "context"
    now = utc_now_iso()
    intent_summary = args.intent_summary or (
        f"Create corrective action report for {repository} {args.target_branch}, "
        "then implement the approved improvements."
    )
    report_path = args.report_path
    report_rel = ""
    if report_path:
        report_rel = relative_to_repo(repo_root, Path(report_path).resolve())

    agent_context = {
        "schema_version": "1.0",
        "project": {
            "name": repo_name,
            "repository": repository,
            "environment": "",
        },
        "workflow": {
            "name": "corrective-action-fix",
            "phase": "initialization",
            "risk_level": "unknown",
            "command": "/corrective-action-fix",
        },
        "agent": {
            "name": "runtime-workflow",
            "role": "corrective action fix workflow initialization",
            "input_artifacts": [report_rel] if report_rel else [],
            "output_artifacts": [
                relative_to_repo(repo_root, context_dir / "agent-context.json"),
                relative_to_repo(repo_root, context_dir / "artifact-index.json"),
            ],
        },
        "intent": {
            "summary": intent_summary,
            "non_goals": [],
            "success_criteria": [
                "Corrective action report findings are converted into a GitHub Issue.",
                "An issue branch is created as feature/issue-<number>.",
                "Implementation, unit tests, and integration startup checks are completed.",
                "Human check for startup/integration is complete before push.",
            ],
        },
        "safety_context": {
            "stop_behavior_known": False,
            "communication_loss_behavior_known": False,
            "startup_safe_state_known": False,
            "shutdown_safe_state_known": False,
            "field_trial_allowed": False,
            "open_safety_questions": [
                "Confirm whether corrective actions touch STOP, control, startup, shutdown, or communication loss behavior.",
            ],
        },
        "assumptions": [
            f"work_id={work_id}",
            f"base_work_id={args.base_work_id}" if args.base_work_id else "base_work_id=",
            f"target_repository={repository}",
            f"repository_argument={args.repository}",
            f"target_branch={args.target_branch}",
        ],
        "constraints": [
            "Do not push until the human startup/integration check is explicitly approved.",
        ],
    }
    write_json(context_dir / "agent-context.json", agent_context)
    write_json(context_dir / "qa-records.json", [])
    write_json(context_dir / "finding-records.json", [])
    write_json(context_dir / "decision-records.json", [])
    write_json(context_dir / "test-evidence.json", [])
    write_json(
        context_dir / "handoff-package.json",
        {
            "schema_version": "1.0",
            "from_agent": "runtime-workflow",
            "to_agent": "corrective-action-fix",
            "workflow": "corrective-action-fix",
            "phase": "initialization",
            "intent": intent_summary,
            "summary": f"Initialized corrective action fix work area {work_id}.",
            "decisions": [],
            "artifacts": [report_rel] if report_rel else [],
            "open_questions": agent_context["safety_context"]["open_safety_questions"],
            "risks": [],
            "required_next_actions": [
                "Prepare target repository and branch.",
                "Create or reuse corrective action report.",
                "Build and load RAG before implementation.",
                "Create GitHub Issue and issue branch.",
            ],
            "stop_conditions": [
                "Stop before push until the human startup/integration check is approved.",
            ],
        },
    )

    index = load_artifact_index(work_dir, repo_name, "corrective-action-fix")
    upsert_artifact(
        index,
        {
            "id": "AGENT-CONTEXT",
            "title": "Corrective Action Fix Context",
            "path": relative_to_repo(repo_root, context_dir / "agent-context.json"),
            "type": "other",
            "status": "draft",
            "owner_agent": "runtime-workflow",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["corrective-action-fix"],
            "summary": "Workflow context for corrective action fix.",
            "unresolved_items": [],
        },
    )
    if report_rel:
        upsert_artifact(
            index,
            {
                "id": "CORRECTIVE-ACTION-REPORT",
                "title": Path(report_rel).name,
                "path": report_rel,
                "type": "report",
                "status": "draft",
                "owner_agent": "corrective-action-report",
                "created_at": now,
                "updated_at": now,
                "depends_on": [],
                "consumed_by": ["corrective-action-fix", "rag-build", "rag-load"],
                "summary": "Corrective action report used as implementation input.",
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
        "report_path": report_rel,
    }


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
