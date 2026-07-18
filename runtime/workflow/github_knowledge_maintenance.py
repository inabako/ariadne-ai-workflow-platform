from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shlex
import shutil
import string
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    default_github_owner,
    ensure_work_tree,
    find_repo_root,
    gate_restart,
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
    write_markdown,
)
from runtime.constants.paths import REGISTRY_DB_PATH, SOURCE_GITHUB_KNOWLEDGE  # noqa: E402
from runtime.constants.schemas import (  # noqa: E402
    AGENT_CONTEXT_SCHEMA,
    ARTIFACT_INDEX_SCHEMA,
    DECISION_RECORD_SCHEMA,
    FINDING_RECORD_SCHEMA,
    GITHUB_KNOWLEDGE_ANALYSIS_SCHEMA,
    GITHUB_OPERATION_GATE_SCHEMA,
    HANDOFF_PACKAGE_SCHEMA,
    QA_RECORD_SCHEMA,
    TEST_EVIDENCE_SCHEMA,
    TOOL_SELECTION_SCHEMA,
)
from runtime.constants.workspace import (  # noqa: E402
    context_dir_for_work_dir,
    context_file,
    context_path_pattern,
    git_worktree_dir_for_work_dir,
    git_worktree_path_pattern,
    process_report_dir_for_work_dir,
    work_dir_for_id,
)
from runtime.workflow.context_first import (  # noqa: E402
    context_entry,
    context_path,
    load_manifest,
    manifest_path_for_work_dir,
    register_context,
)


SCAN_MODES = ["repository", "issue", "pull-request", "recent", "full"]
REPAIR_MODES = ["proposal", "apply"]
RAG_SOURCE_ID_ALPHABET = string.ascii_uppercase + string.digits


def github_knowledge_gate_restart(
    gate: str,
    *,
    status: str,
    restart_reason: str,
    repair_available: bool = False,
    repair_command: str = "",
) -> dict[str, Any]:
    return gate_restart.build_gate_restart(
        gate,
        restart_reason=restart_reason,
        repair_available=repair_available,
        repair_command=repair_command,
        status_after_restart="pass" if status in {"pass", "ready", "applied", "verified", "dry-run"} else "fail",
    )


def github_git_responsibility_boundary() -> dict[str, Any]:
    return {
        "github_api": {
            "responsibility": "GitHub remote metadata and hosted collaboration state.",
            "allowed": [
                "Issue / Pull Request / comment / label / release collection",
                "GitHub-hosted documentation sync after approval",
                "remote branch ref and expected SHA verification",
            ],
            "not_allowed": [
                "commit graph rewrite",
                "rebase",
                "commit message rewrite",
                "local tree verification",
            ],
        },
        "git_cli_local": {
            "responsibility": "Local Git object graph construction and verification that GitHub API cannot perform.",
            "authentication_required": False,
            "allowed": [
                "read local commit graph and file history",
                "create non-interactive rewrite/replay branches",
                "verify before/after SHA mapping",
                "verify old/new tree equality or intended tree delta",
            ],
            "not_allowed": [
                "GitHub Issue / PR body edits",
                "GitHub comment edits",
                "remote fetch",
                "remote push",
                "interactive editor driven rebase in runtime automation",
            ],
        },
        "git_cli_remote": {
            "responsibility": "Authenticated remote Git transport for reflecting a verified local graph to GitHub.",
            "authentication_required": True,
            "allowed": [
                "fetch approved remote refs",
                "ls-remote approved remote refs",
                "push an already verified local graph to the approved remote branch",
                "force-with-lease only when the exact remote branch and expected old SHA are approved",
            ],
            "not_allowed": [
                "GitHub Issue / PR body edits",
                "GitHub comment edits",
                "commit graph construction",
                "interactive editor driven rebase in runtime automation",
            ],
            "auth_sources": [
                "Git credential manager",
                "HTTPS token configured for git",
                "repository .env GITHUB_TOKEN routed by repo-local SCM helpers when supported",
            ],
        },
        "approval_model": {
            "human_check_count": "one",
            "rule": (
                "One approval package must include target repository, target branch, rewrite action, "
                "local verification commands, rollback plan, and exact remote update command. "
                "After that approval, runtime may perform local rewrite, verification, and the approved remote update."
            ),
        },
    }


def git_cli_preflight() -> dict[str, Any]:
    git_path = shutil.which("git")
    return {
        "tool": "git",
        "required": True,
        "available": bool(git_path),
        "detected_path": git_path or "",
        "install_hint": "Install Git for Windows and ensure git is on PATH.",
        "install_command": "winget install --id Git.Git -e",
    }


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

    integrity_parser = subparsers.add_parser(
        "artifact-integrity",
        help="Verify analysis JSON and generated Markdown artifacts with strict UTF-8/file-content checks.",
    )
    integrity_parser.add_argument("--work-id", required=True)
    integrity_parser.add_argument("--analysis-path", default="")
    integrity_parser.add_argument("--output", default="")
    integrity_parser.add_argument("--fail-on-finding", action="store_true")
    integrity_parser.add_argument("--repo-root", default=None)

    repair_parser = subparsers.add_parser("repair-plan", help="Create a human review repair plan from analysis JSON.")
    repair_parser.add_argument("--work-id", required=True)
    repair_parser.add_argument("--analysis-path", default="")
    repair_parser.add_argument("--output", default="")
    repair_parser.add_argument("--repo-root", default=None)

    detect_rebase_parser = subparsers.add_parser(
        "detect-rebase-candidates",
        help="Detect small commit-history leakage candidates and write them to analysis JSON.",
    )
    detect_rebase_parser.add_argument("--work-id", required=True)
    detect_rebase_parser.add_argument("--analysis-path", default="")
    detect_rebase_parser.add_argument("--git-repo", default="")
    detect_rebase_parser.add_argument("--base", default="HEAD~30")
    detect_rebase_parser.add_argument("--head", default="HEAD")
    detect_rebase_parser.add_argument("--max-commits", type=int, default=80)
    detect_rebase_parser.add_argument("--max-files", type=int, default=3)
    detect_rebase_parser.add_argument("--all-history", action="store_true", help="Scan the full reachable history from --head.")
    detect_rebase_parser.add_argument("--append", action="store_true")
    detect_rebase_parser.add_argument("--repo-root", default=None)

    rebase_parser = subparsers.add_parser(
        "rebase-plan",
        help="Create a high-risk review plan for small commit-history rebase repairs.",
    )
    rebase_parser.add_argument("--work-id", required=True)
    rebase_parser.add_argument("--analysis-path", default="")
    rebase_parser.add_argument("--output", default="")
    rebase_parser.add_argument("--repo-root", default=None)

    rebase_review_parser = subparsers.add_parser(
        "rebase-review-intake",
        help="Ingest a Human Review OK/NG checklist and record approved history rewrite candidates.",
    )
    rebase_review_parser.add_argument("--work-id", required=True)
    rebase_review_parser.add_argument("--analysis-path", default="")
    rebase_review_parser.add_argument("--plan-path", default="")
    rebase_review_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    rebase_review_parser.add_argument(
        "--ok-repair-goal",
        choices=[
            "auto",
            "absorb-into-existing-commit",
            "drop-empty-or-noise-commit",
            "split-into-independent-commit",
            "keep-with-evidence",
            "no-rewrite",
        ],
        default="auto",
    )
    rebase_review_parser.add_argument("--allow-partial", action="store_true")
    rebase_review_parser.add_argument("--repo-root", default=None)

    message_plan_parser = subparsers.add_parser(
        "message-repair-plan",
        help="Create a high-risk commit message repair review plan after rebase verification.",
    )
    message_plan_parser.add_argument("--work-id", required=True)
    message_plan_parser.add_argument("--analysis-path", default="")
    message_plan_parser.add_argument("--git-repo", default="")
    message_plan_parser.add_argument("--source-ref", default="")
    message_plan_parser.add_argument("--max-commits", type=int, default=200)
    message_plan_parser.add_argument("--output", default="")
    message_plan_parser.add_argument("--repo-root", default=None)

    message_review_parser = subparsers.add_parser(
        "message-review-intake",
        help="Ingest a commit message repair OK/NG checklist and record approved message overrides.",
    )
    message_review_parser.add_argument("--work-id", required=True)
    message_review_parser.add_argument("--analysis-path", default="")
    message_review_parser.add_argument("--plan-path", default="")
    message_review_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    message_review_parser.add_argument("--allow-partial", action="store_true")
    message_review_parser.add_argument("--repo-root", default=None)

    rebase_apply_parser = subparsers.add_parser(
        "rebase-apply",
        help="Execute approved small commit-history rebase commands after human approval.",
    )
    rebase_apply_parser.add_argument("--work-id", required=True)
    rebase_apply_parser.add_argument("--candidate-id", required=True)
    rebase_apply_parser.add_argument("--analysis-path", default="")
    rebase_apply_parser.add_argument("--git-repo", default="")
    rebase_apply_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    rebase_apply_parser.add_argument("--dry-run", action="store_true")
    rebase_apply_parser.add_argument("--repo-root", default=None)

    rebase_package_parser = subparsers.add_parser(
        "rebase-replay-package",
        help="Generate a schema-compliant rebase replay package from approved history rewrite candidates.",
    )
    rebase_package_parser.add_argument("--work-id", required=True)
    rebase_package_parser.add_argument("--candidate-id", action="append", default=[])
    rebase_package_parser.add_argument("--analysis-path", default="")
    rebase_package_parser.add_argument("--output", default="")
    rebase_package_parser.add_argument("--target-branch", default="")
    rebase_package_parser.add_argument("--source-ref", default="")
    rebase_package_parser.add_argument("--remote", default="origin")
    rebase_package_parser.add_argument("--expected-remote-sha", default="")
    rebase_package_parser.add_argument("--allow-push", action="store_true")
    rebase_package_parser.add_argument("--apply-mode", choices=["direct", "git-3way", "auto-3way"], default="direct")
    rebase_package_parser.add_argument("--repo-root", default=None)

    message_package_parser = subparsers.add_parser(
        "message-repair-package",
        help="Generate a rebase replay package containing approved commit message overrides.",
    )
    message_package_parser.add_argument("--work-id", required=True)
    message_package_parser.add_argument("--candidate-id", action="append", default=[])
    message_package_parser.add_argument("--analysis-path", default="")
    message_package_parser.add_argument("--output", default="")
    message_package_parser.add_argument("--target-branch", default="")
    message_package_parser.add_argument("--source-ref", default="")
    message_package_parser.add_argument("--remote", default="origin")
    message_package_parser.add_argument("--expected-remote-sha", default="")
    message_package_parser.add_argument("--allow-push", action="store_true")
    message_package_parser.add_argument("--apply-mode", choices=["direct", "git-3way", "auto-3way"], default="auto-3way")
    message_package_parser.add_argument("--repo-root", default=None)

    rebase_replay_parser = subparsers.add_parser(
        "rebase-replay-apply",
        help="Execute one approved small-commit rebase package with the built-in non-interactive replay runtime.",
    )
    rebase_replay_parser.add_argument("--work-id", required=True)
    rebase_replay_parser.add_argument("--package-path", default="")
    rebase_replay_parser.add_argument("--analysis-path", default="")
    rebase_replay_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    rebase_replay_parser.add_argument("--remote", default="")
    rebase_replay_parser.add_argument("--apply-mode", choices=["direct", "git-3way", "auto-3way"], default="")
    rebase_replay_parser.add_argument("--push", action="store_true")
    rebase_replay_parser.add_argument("--reuse-worktree", action="store_true")
    rebase_replay_parser.add_argument("--dry-run", action="store_true")
    rebase_replay_parser.add_argument("--repo-root", default=None)

    publish_verified_parser = subparsers.add_parser(
        "publish-verified-replay",
        help="Push an already verified replay tip with force-with-lease without regenerating the package.",
    )
    publish_verified_parser.add_argument("--work-id", required=True)
    publish_verified_parser.add_argument("--analysis-path", default="")
    publish_verified_parser.add_argument("--target-branch", default="")
    publish_verified_parser.add_argument("--remote", default="origin")
    publish_verified_parser.add_argument("--expected-remote-sha", required=True)
    publish_verified_parser.add_argument("--new-tip", default="")
    publish_verified_parser.add_argument("--execution-index", type=int, default=-1)
    publish_verified_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    publish_verified_parser.add_argument("--dry-run", action="store_true")
    publish_verified_parser.add_argument("--repo-root", default=None)

    sync_parser = subparsers.add_parser(
        "github-sync-plan", help="Create an approval-gated GitHub CLI/API sync plan from analysis JSON."
    )
    sync_parser.add_argument("--work-id", required=True)
    sync_parser.add_argument("--analysis-path", default="")
    sync_parser.add_argument("--output", default="")
    sync_parser.add_argument("--repo-root", default=None)

    sync_review_parser = subparsers.add_parser(
        "github-sync-review-plan",
        help="Create an OK/NG review checklist for GitHub Issue/PR/comment repair actions.",
    )
    sync_review_parser.add_argument("--work-id", required=True)
    sync_review_parser.add_argument("--analysis-path", default="")
    sync_review_parser.add_argument("--output", default="")
    sync_review_parser.add_argument("--repo-root", default=None)

    sync_review_intake_parser = subparsers.add_parser(
        "github-sync-review-intake",
        help="Ingest a GitHub Issue/PR/comment repair OK/NG checklist into analysis JSON.",
    )
    sync_review_intake_parser.add_argument("--work-id", required=True)
    sync_review_intake_parser.add_argument("--analysis-path", default="")
    sync_review_intake_parser.add_argument("--plan-path", default="")
    sync_review_intake_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    sync_review_intake_parser.add_argument("--allow-partial", action="store_true")
    sync_review_intake_parser.add_argument("--repo-root", default=None)

    sync_apply_parser = subparsers.add_parser(
        "github-sync-apply",
        help="Execute one approved GitHub sync action after Human Check.",
    )
    sync_apply_parser.add_argument("--work-id", required=True)
    sync_apply_parser.add_argument("--action-id", required=True)
    sync_apply_parser.add_argument("--analysis-path", default="")
    sync_apply_parser.add_argument("--human-check", choices=["pending", "approved"], default="pending")
    sync_apply_parser.add_argument("--dry-run", action="store_true")
    sync_apply_parser.add_argument("--repo-root", default=None)

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


def default_work_scope(target_branch: str) -> str:
    branch = target_branch.strip()
    return slugify(branch) if branch else "original"


def default_work_id(
    repository: str,
    scan_mode: list[str],
    default_owner: str = "",
    target_branch: str = "",
) -> str:
    mode = "full" if "full" in scan_mode else scan_mode[0]
    return f"github/{default_work_scope(target_branch)}/{mode}"


def rag_source_report_name(topic: str) -> str:
    timestamp = local_timestamp().replace("_", "")
    random_id = "".join(secrets.choice(RAG_SOURCE_ID_ALPHABET) for _ in range(6))
    return f"{timestamp}_{random_id}_{slugify(topic)}.md"


def github_operation_gate(
    *,
    work_id: str,
    repository: str,
    repair_mode: str,
    rag_output: bool,
) -> dict[str, Any]:
    mutation_allowed = repair_mode == "apply"
    reasons = []
    if mutation_allowed:
        reasons.append("repair-mode apply may execute one approved mutation package after Human Check.")
    if rag_output:
        reasons.append("RAG publication requires human approval before publication.")
    return {
        "schema_version": "1.0",
        "artifact_type": "github-operation-gate",
        "workflow": "github-knowledge-maintenance",
        "work_id": work_id,
        "created_at": utc_now_iso(),
        "repository": repository,
        "read_only_allowed": True,
        "mutation_allowed": mutation_allowed,
        "clone_allowed": False,
        "human_check_required": bool(reasons),
        "human_check_reasons": reasons,
        "responsibility_boundary": github_git_responsibility_boundary(),
        "git_cli_preflight": git_cli_preflight(),
        "rules": [
            "Read-only GitHub CLI/API collection may proceed.",
            "GitHub API/gh is for hosted metadata and documentation sync; it must not be used as if it can rebase.",
            "Git CLI local is required for commit graph rewrite, before/after SHA mapping, and tree verification; authentication is not required for local-only operations.",
            "Git CLI remote is required to fetch, ls-remote, or push the verified graph to GitHub; authentication is required.",
            "Runtime automation must not depend on interactive editor driven rebase.",
            "A single Human Check approval package is sufficient when it includes target branch, exact commands, rollback, and verification.",
            "Clone requires separate human approval when API evidence is insufficient.",
        ],
    }


def github_tool_selection(
    *,
    work_id: str,
    repair_mode: str,
) -> dict[str, Any]:
    tools = [
        {
            "name": "gh",
            "mode": "read-only",
            "purpose": "Collect GitHub Issue, PR, label, comment, release, and metadata evidence.",
            "required": True,
            "source": "github-knowledge-maintenance",
            "human_check_required": False,
        },
        {
            "name": "github-api",
            "mode": "read-only",
            "purpose": "Collect GitHub metadata when gh output needs API-backed detail.",
            "required": False,
            "source": "github-knowledge-maintenance",
            "human_check_required": False,
        },
        {
            "name": "git",
            "mode": "local-history-read",
            "purpose": "Read local commit graph and file history that GitHub API cannot rewrite.",
            "required": True,
            "source": "github-knowledge-maintenance",
            "human_check_required": False,
            "authentication_required": False,
            "install_required": not git_cli_preflight()["available"],
            "install_command": git_cli_preflight()["install_command"],
        },
    ]
    if repair_mode == "apply":
        tools.append(
            {
                "name": "gh",
                "mode": "mutation",
                "purpose": "Apply human-approved GitHub documentation sync actions.",
                "required": False,
                "source": "github-knowledge-maintenance",
                "human_check_required": True,
            }
        )
        tools.append(
            {
                "name": "git",
                "mode": "local-history-mutation",
                "purpose": "Create and verify an approved non-interactive commit graph rewrite.",
                "required": True,
                "source": "github-knowledge-maintenance",
                "human_check_required": True,
                "authentication_required": False,
                "install_required": not git_cli_preflight()["available"],
                "install_command": git_cli_preflight()["install_command"],
            }
        )
        tools.append(
            {
                "name": "git",
                "mode": "remote-history-mutation",
                "purpose": "Reflect a verified local commit graph to the approved GitHub branch with fetch/ls-remote/push.",
                "required": True,
                "source": "github-knowledge-maintenance",
                "human_check_required": True,
                "authentication_required": True,
                "install_required": not git_cli_preflight()["available"],
                "install_command": git_cli_preflight()["install_command"],
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "tool-selection",
        "architecture": "context-first",
        "selected_at": utc_now_iso(),
        "selected_by": "dispatcher",
        "selection_mode": "manual",
        "work_id": work_id,
        "workflow": "github-knowledge-maintenance",
        "status": "selected",
        "tools": tools,
        "responsibility_boundary": github_git_responsibility_boundary(),
        "human_check_required": any(item["human_check_required"] for item in tools),
        "human_check_reasons": [
            f"Tool `{item['name']}` is selected for mutation mode."
            for item in tools
            if item["human_check_required"]
        ],
        "source": {
            "registry": REGISTRY_DB_PATH.as_posix(),
            "schema": TOOL_SELECTION_SCHEMA,
        },
        "gate_restart": github_knowledge_gate_restart(
            "github-knowledge-tool-selection-gate",
            status="ready",
            restart_reason="github-knowledge-tool-selection",
        ),
    }


def register_github_knowledge_contexts(repo_root: Path, work_dir: Path, work_id: str) -> None:
    context_dir = context_dir_for_work_dir(work_dir)
    registrations = [
        ("agent-context", context_dir / "agent-context.json", True, AGENT_CONTEXT_SCHEMA),
        ("artifact-index", context_dir / "artifact-index.json", True, ARTIFACT_INDEX_SCHEMA),
        ("handoff-package", context_dir / "handoff-package.json", False, HANDOFF_PACKAGE_SCHEMA),
        ("tool-selection", context_dir / "tool-selection.json", True, TOOL_SELECTION_SCHEMA),
        ("github-operation-gate", context_dir / "github-operation-gate.json", True, GITHUB_OPERATION_GATE_SCHEMA),
        ("github-knowledge-analysis", context_dir / "github-knowledge-analysis.json", False, GITHUB_KNOWLEDGE_ANALYSIS_SCHEMA),
        ("qa-records", context_dir / "qa-records.json", False, QA_RECORD_SCHEMA),
        ("finding-records", context_dir / "finding-records.json", False, FINDING_RECORD_SCHEMA),
        ("decision-records", context_dir / "decision-records.json", False, DECISION_RECORD_SCHEMA),
        ("test-evidence", context_dir / "test-evidence.json", False, TEST_EVIDENCE_SCHEMA),
    ]
    for context_type, path, required, schema in registrations:
        if not path.exists():
            continue
        register_context(
            repo_root,
            work_dir,
            work_id=work_id,
            context_type=context_type,
            path=path,
            required=required,
            generated_by="github-knowledge-maintenance",
            owner="workflow" if context_type not in {"tool-selection"} else "dispatcher",
            schema=schema,
        )


def init_work(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    repository = normalize_repository_value(args.repository)
    repo_name = repository_name(repository, default_github_owner(settings))
    work_id = args.work_id or default_work_id(
        repository,
        args.scan_mode,
        default_github_owner(settings),
        args.target_branch,
    )
    work_dir = work_dir_for_id(repo_root, work_id)
    if work_dir.exists() and not args.reuse_existing:
        raise FileExistsError(
            f"Work directory already exists: {work_dir}. Confirm reuse, then rerun with --reuse-existing."
        )

    work_dir = ensure_work_tree(repo_root, work_id)
    context_dir = context_dir_for_work_dir(work_dir)
    now = utc_now_iso()
    intent_summary = args.intent_summary or (
        f"{repository} のGitHub knowledge assetsを、Git historyを消さずsource codeを変更せずに保守する。"
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
                "Git historyを消したり、過去の証跡を隠したりしない。",
                "target repositoryのcommit source、source code、README本文、configuration contentを変更しない。",
                "既存commit messageを書き換える場合は、人間がitem単位でhigh-risk pathを明示承認した場合に限る。",
                "GitHub CLI/APIの証跡が不足し、人間が承認した場合を除き、repositoryをcloneしない。",
            ],
            "success_criteria": [
                "GitHub metadata collection planが明示されている。",
                "Knowledge assetsとnarrative gapsがJSONに記録されている。",
                "人間レビュー可能なrepair proposalsが準備されている。",
                "Commit repair proposalsに、GitHub commit-list viewだけで意味が分かるsemantic subjectが含まれている。",
                "PR title repair proposalsに、GitHub PR-list viewだけで意味が分かるsemantic titleが含まれている。",
                "承認済みGitHub documentation sync actionsがdraft proposalsと分離されている。",
                "要求された場合、Knowledge DB candidatesとRAG candidatesが生成されている。",
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
            "Git historyは歴史的証跡であり、消してはいけない。",
            "既存commit-message/body rewriteは、item単位の明示的な人間承認、before/after SHA mapping、rollback plan、必要時のreview済みforce-push commandがある場合のみ許可する。",
            "Commit message repairでは、GitHub commit-list subjectをbodyとは別に評価する。",
            "このworkflowではcommit sourceとsource filesを変更しない。",
            "GitHub mutationには明示的な人間承認が必要。",
            "Repair mode 'proposal' では gh edit/comment commandを実行しない。",
            "Repair mode 'apply' でも、各mutation前にitem単位の人間承認が必要。",
            "Cloneには明示的な人間承認と記録済み理由が必要。",
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
                "gh issue/pr/api commandでGitHub metadataを収集する。",
                "knowledge assets、narrative gaps、semantic subject gaps、PR title gaps、repair proposalsをJSONへ記録する。",
            ],
            "stop_conditions": [
                "人間承認が記録されるまでGitHubまたはGit mutation前で停止する。",
                "既存commit-message rewriteは、before/after SHA mappingとrollback planがreviewされるまで停止する。",
                "提案semantic subjectがGitHub commit-list viewでまだ曖昧な場合、commit-message rewrite前で停止する。",
                "人間承認と理由が記録されるまでclone前で停止する。",
            ],
        },
    )
    write_json(
        context_dir / "tool-selection.json",
        github_tool_selection(work_id=work_id, repair_mode=args.repair_mode),
    )
    write_json(
        context_dir / "github-operation-gate.json",
        github_operation_gate(
            work_id=work_id,
            repository=repository,
            repair_mode=args.repair_mode,
            rag_output=bool(args.rag_output),
        ),
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
            "summary": "GitHub repository knowledge maintenanceのworkflow context。",
            "unresolved_items": [],
        },
    )
    write_json(context_dir / "artifact-index.json", index)
    register_github_knowledge_contexts(repo_root, work_dir, work_id)
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
    context = read_json(context_file(work_dir, "agent-context.json"), default={}) or {}
    assumptions = context.get("assumptions", [])
    assumption_map = {}
    for item in assumptions:
        if isinstance(item, str) and "=" in item:
            key, value = item.split("=", 1)
            assumption_map[key] = value
    return {
        "schema_version": "1.0",
        "workflow": "github-knowledge-maintenance",
        "work_id": assumption_map.get("work_id", work_dir.name),
        "repository": context.get("project", {}).get("repository", ""),
        "target_branch": assumption_map.get("target_branch", ""),
        "scan_mode": [mode for mode in assumption_map.get("scan_mode", "recent").split(",") if mode],
        "repair_mode": assumption_map.get("repair_mode", "proposal"),
        "rag_output": assumption_map.get("rag_output", "False").lower() == "true",
        "generated_at": utc_now_iso(),
        "summary": "TBD: GitHub repository knowledge maintenanceの調査結果を要約する。",
        "collection_plan": [
            {
                "id": "COLLECT-000",
                "source_type": "api",
                "command": "gh --version; if missing, request human approval then run: winget install --id GitHub.cli",
                "purpose": "Issue、PR、comment、label、branch、tag、release metadataを収集する前にGitHub CLIが利用可能であることを確認する。",
                "status": "planned",
            },
            {
                "id": "COLLECT-001",
                "source_type": "issue",
                "command": "gh issue list --repo <owner/repo> --state all --limit 100",
                "purpose": "Issueのintentとmaintenance contextを収集する。",
                "status": "planned",
            },
            {
                "id": "COLLECT-002",
                "source_type": "pull-request",
                "command": "gh pr list --repo <owner/repo> --state all --limit 100",
                "purpose": "PRのimplementation narrativeとreview contextを収集する。",
                "status": "planned",
            },
        ],
        "metadata_sources": [],
        "knowledge_assets": [],
        "narrative_gaps": [],
        "repair_proposals": [],
        "history_rewrite_candidates": [],
        "message_repair_candidates": [],
        "github_sync_review_plans": [],
        "github_sync_review_intakes": [],
        "github_sync_actions": [],
        "knowledge_db_candidates": [],
        "rag_candidates": [],
        "open_questions": [],
        "guardrails": [
            "Git historyを消したり、歴史的証跡を隠したりしない。",
            "commit sourceまたはtarget repositoryのsource filesを変更しない。",
            "既存commit-message/body rewriteには、item単位の明示的な人間承認、before/after SHA mapping、rollback plan、必要時のreview済みforce-push commandが必要。",
            "GitHub commit-list subjectが曖昧なままの場合、bodyのみのcommit repairを承認しない。",
            "Commit repair proposalsには `type(scope): responsibility/result` 形式のsemantic subjectを含める。",
            "PR title repair proposalsには、bodyを開かなくてもGitHub PR-list viewで意味が分かるsemantic titleを含める。",
            "source codeを変更しない。",
            "人間承認なしに gh edit/comment/api mutation commandを実行しない。",
            "GitHub CLI/API収集を優先し、cloneは明示承認がある場合のみ行う。",
        ],
    }


def analysis_path_for(work_dir: Path, raw_path: str) -> Path:
    return Path(raw_path).resolve() if raw_path else context_file(work_dir, "github-knowledge-analysis.json")


def register_artifact(repo_root: Path, work_dir: Path, artifact_id: str, title: str, path: Path, artifact_type: str) -> None:
    context = read_json(context_file(work_dir, "agent-context.json"), default={}) or {}
    project_name = context.get("project", {}).get("name", work_dir.name)
    work_id = default_analysis(work_dir).get("work_id", work_dir.name)
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
    write_json(context_file(work_dir, "artifact-index.json"), index)
    if path.name == "github-knowledge-analysis.json":
        register_context(
            repo_root,
            work_dir,
            work_id=str(work_id),
            context_type="github-knowledge-analysis",
            path=path,
            required=True,
            generated_by="github-knowledge-maintenance",
            owner="workflow",
            schema=GITHUB_KNOWLEDGE_ANALYSIS_SCHEMA,
        )


def create_analysis_template(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = work_dir_for_id(repo_root, args.work_id)
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


MOJIBAKE_MARKERS = ("\u7e67", "\u7e3a", "\u8b41", "\u9015", "\u8373", "\u90b1", "\ufffd")
INTEGRITY_MARKDOWN_PATTERNS = (
    "github-knowledge-repair-plan-*.md",
    "github-history-rebase-plan-*.md",
    "github-history-message-repair-plan-*.md",
    "github-documentation-sync-review-plan-*.md",
    "github-documentation-sync-plan-*.md",
    "github-knowledge-rag-candidate-*.md",
    "github-history-rebase-replay-execution-*.md",
)


def inspect_utf8_text_artifact(repo_root: Path, path: Path, *, artifact_kind: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": relative_to_repo(repo_root, path),
        "artifact_kind": artifact_kind,
        "exists": path.exists(),
        "utf8_decode": "not-checked",
        "json_parse": "not-applicable",
        "bom": False,
        "mojibake_markers": [],
        "content_signals": [],
        "findings": [],
    }
    if not path.exists():
        record["findings"].append("missing")
        return record
    raw = path.read_bytes()
    record["bom"] = raw.startswith(b"\xef\xbb\xbf")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        record["utf8_decode"] = "fail"
        record["findings"].append(f"utf8-decode-failed: {exc}")
        return record

    record["utf8_decode"] = "pass"
    markers = [marker for marker in MOJIBAKE_MARKERS if marker in text]
    if markers:
        record["mojibake_markers"] = markers
        record["findings"].append("mojibake-marker-present")
    if artifact_kind == "analysis-json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            record["json_parse"] = "fail"
            record["findings"].append(f"json-parse-failed: {exc}")
        else:
            record["json_parse"] = "pass"
            if isinstance(payload, dict):
                candidates = payload.get("history_rewrite_candidates", [])
                count = len(candidates) if isinstance(candidates, list) else "invalid"
                record["content_signals"].append(f"history_rewrite_candidates:{count}")
            else:
                record["findings"].append("analysis-json-not-object")
    elif artifact_kind == "rebase-plan":
        if "候補別 OK / NG チェックリスト" in text:
            record["content_signals"].append("ok-ng-checklist-present")
        else:
            record["findings"].append("ok-ng-checklist-missing")
    return record


def github_knowledge_artifact_paths(work_dir: Path, analysis_path: Path) -> list[tuple[str, Path]]:
    process_dir = process_report_dir_for_work_dir(work_dir)
    artifacts: list[tuple[str, Path]] = [("analysis-json", analysis_path)]
    if process_dir.exists():
        for pattern in INTEGRITY_MARKDOWN_PATTERNS:
            kind = "rebase-plan" if pattern == "github-history-rebase-plan-*.md" else "markdown-report"
            for path in sorted(process_dir.glob(pattern)):
                artifacts.append((kind, path))
    return artifacts


def build_artifact_integrity_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# GitHub Knowledge Artifact Integrity",
        "",
        "## Summary",
        "",
        f"- Status: `{report['status']}`",
        f"- Work ID: `{report['work_id']}`",
        f"- Checked artifacts: {len(report['artifacts'])}",
        f"- Finding count: {len(report['findings'])}",
        "",
        "## Rule",
        "",
        "- Do not judge mojibake from console rendering alone.",
        "- Verify saved file bytes with strict UTF-8 decode before reporting corruption.",
        "- Do not hand-edit `github-knowledge-analysis.json`; use the official `github-knowledge` runtime commands.",
        "",
        "## Artifacts",
        "",
        "| Path | Kind | UTF-8 | JSON | BOM | Signals | Findings |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for artifact in report["artifacts"]:
        signals = "<br>".join(artifact.get("content_signals", [])) or "-"
        findings = "<br>".join(artifact.get("findings", [])) or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{artifact['path']}`",
                    str(artifact["artifact_kind"]),
                    str(artifact["utf8_decode"]),
                    str(artifact["json_parse"]),
                    str(artifact["bom"]).lower(),
                    signals,
                    findings,
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def create_artifact_integrity_report(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = work_dir_for_id(repo_root, args.work_id)
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    analysis_path = analysis_path_for(work_dir, args.analysis_path)
    artifacts = [
        inspect_utf8_text_artifact(repo_root, path, artifact_kind=kind)
        for kind, path in github_knowledge_artifact_paths(work_dir, analysis_path)
    ]
    findings = [
        f"{artifact['path']}: {finding}"
        for artifact in artifacts
        for finding in artifact.get("findings", [])
    ]
    status = "pass" if not findings else "fail"
    report = {
        "artifact_type": "github-knowledge-artifact-integrity",
        "workflow": "github-knowledge-maintenance",
        "work_id": args.work_id,
        "status": status,
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "artifacts": artifacts,
        "findings": findings,
        "generated_at": utc_now_iso(),
        "gate_restart": github_knowledge_gate_restart(
            "github-knowledge-artifact-integrity-gate",
            status=status,
            restart_reason="artifact-integrity-findings" if findings else "normal-artifact-integrity-gate",
            repair_available=bool(findings),
            repair_command=(
                "aiwfctl github-knowledge artifact-integrity --work-id "
                f"{args.work_id} --fail-on-finding"
                if findings
                else ""
            ),
        ),
    }
    output_path = (
        Path(args.output).resolve()
        if args.output
        else process_report_dir_for_work_dir(work_dir) / f"github-knowledge-artifact-integrity-{local_timestamp()}.md"
    )
    json_path = output_path.with_suffix(".json")
    write_json(json_path, report)
    report["report_json"] = relative_to_repo(repo_root, json_path)
    write_markdown(output_path, build_artifact_integrity_markdown(report))
    report["report_path"] = relative_to_repo(repo_root, output_path)
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-KNOWLEDGE-ARTIFACT-INTEGRITY",
        "GitHub Knowledge Artifact Integrity",
        output_path,
        "report",
    )
    if args.fail_on_finding and findings:
        raise RuntimeError("GitHub knowledge artifact integrity failed: " + "; ".join(findings))
    return report


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- なし"
    return "\n".join(f"- {item}" for item in items)


FIELD_LABELS = {
    "file_paths": "target files",
    "suspect_commits": "suspect commits",
    "expected_commit": "expected commit",
    "repair_goal": "repair goal",
    "independent_responsibility": "independent responsibility",
    "evidence_refs": "evidence refs",
    "completion_criteria": "completion criteria",
    "recommended_action": "recommended Git action",
    "approval_status": "approval status",
    "before_after_sha_mapping": "before/after SHA mapping",
    "rollback_plan": "rollback plan",
    "draft_commands": "draft commands",
    "verification_commands": "verification commands",
    "asset_ref": "知識資産",
    "gap_type": "不足種別",
    "severity": "重要度",
    "evidence": "根拠",
    "why_it_matters": "なぜ重要か",
    "target": "対象",
    "proposal_type": "提案種別",
    "reason": "理由",
    "before_summary": "現状",
    "after_summary": "対応後",
    "approval_required": "承認要否",
    "draft_body": "提案本文",
    "asset_type": "知識種別",
    "source_ref": "参照元",
    "intent": "意図",
    "reuse_value": "再利用価値",
    "candidate_type": "候補種別",
    "knowledge_value": "知識価値",
    "limits": "制約",
    "question": "確認事項",
    "blocks": "ブロック有無",
    "file_paths": "対象ファイル",
    "suspect_commits": "疑わしいコミット",
    "expected_commit": "本来まとめる候補コミット",
    "repair_goal": "修復方針",
    "independent_responsibility": "独立責務",
    "evidence_refs": "証跡参照",
    "recommended_action": "推奨Git操作",
    "completion_criteria": "完了条件",
    "approval_status": "承認状態",
    "before_after_sha_mapping": "修正前後SHA対応",
    "rollback_plan": "ロールバック計画",
    "draft_commands": "ドラフトコマンド",
    "verification_commands": "検証コマンド",
    "approved_at": "承認日時",
    "approved_by": "承認者",
    "approval_type": "承認種別",
    "repository": "リポジトリ",
    "target_branch": "対象branch",
    "scope": "承認範囲",
    "limitations": "制約",
}


def markdown_value(value: Any) -> str:
    if isinstance(value, bool):
        return "はい" if value else "いいえ"
    return str(value)


def field_list(items: list[dict[str, Any]], fields: list[str]) -> str:
    if not items:
        return "- なし"
    lines: list[str] = []
    for item in items:
        title = item.get("title") or item.get("id") or "Untitled"
        lines.append(f"### {title}")
        lines.append("")
        for field in fields:
            label = FIELD_LABELS.get(field, field)
            value = item.get(field, "")
            if isinstance(value, list):
                value_text = markdown_list([markdown_value(entry) for entry in value])
                lines.extend([f"{label}:", "", value_text, ""])
            else:
                lines.append(f"- {label}: {markdown_value(value)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def git_output(repo_path: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=True,
    )
    return result.stdout


def parse_commit_log(raw_log: str) -> list[dict[str, Any]]:
    commits: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in raw_log.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "\x1f" in line:
            commit_hash, subject = line.split("\x1f", 1)
            current = {"hash": commit_hash, "subject": subject, "files": []}
            commits.append(current)
            continue
        if current is not None:
            current["files"].append(line)
    return commits


def collect_commit_summaries(repo_path: Path, base: str, head: str, max_commits: int) -> list[dict[str, Any]]:
    revision = f"{base}..{head}" if base else head
    command = [
        "log",
        "--name-only",
        "--format=%H%x1f%s",
        f"--max-count={max(1, max_commits)}",
        revision,
    ]
    try:
        raw_log = git_output(repo_path, command)
    except subprocess.CalledProcessError:
        if not base:
            raise
        command[-1] = head
        raw_log = git_output(repo_path, command)
    return parse_commit_log(raw_log)


def commit_subject_is_weak(subject: str) -> bool:
    normalized = subject.strip().lower()
    if not normalized:
        return True
    weak_terms = ["update", "fix", "wip", "tmp", "temp", "misc", "cleanup", "対応", "修正", "更新"]
    if normalized in weak_terms:
        return True
    if any(normalized.startswith(f"{term}:") for term in weak_terms):
        return True
    if "(" not in normalized.split(":", 1)[0] and ":" not in normalized:
        return True
    return False


def contains_mojibake(text: str) -> bool:
    return any(marker in text for marker in MOJIBAKE_MARKERS)


def normalize_git_path(path: str) -> str:
    return path.strip().strip('"').replace("\\", "/")


def path_domains(files: list[str]) -> set[str]:
    domains: set[str] = set()
    for raw_path in files:
        path = normalize_git_path(raw_path)
        parts = [part for part in path.split("/") if part]
        if not parts:
            continue
        root = parts[0]
        suffix = Path(path).suffix.lower()
        domains.add(root)
        if root in {".github", "docs", "skills", "templates", "runtime", "rag", "work"}:
            domains.add(root)
        if len(parts) >= 2:
            domains.add(f"{root}/{parts[1]}")
        if suffix in {".md", ".rst"}:
            domains.add("docs-like")
        if suffix in {".py", ".ps1", ".cmd", ".sh"}:
            domains.add("runtime-code")
        if path.endswith((".schema.json", ".jsonl")):
            domains.add("structured-data")
        if "test" in path.lower() or "/tests/" in path.lower():
            domains.add("tests")
        if "brand" in parts or "logo" in parts or suffix in {".svg", ".png", ".jpg", ".jpeg"}:
            domains.add("brand-asset")
        if path in {".gitignore", "pytest.ini", "pyproject.toml", "uv.lock"}:
            domains.add("repo-config")
        if "registries" in parts or suffix in {".duckdb", ".db"}:
            domains.add("registry-data")
    return domains


def path_affinity_score(left_files: list[str], right_files: list[str]) -> int:
    left_normalized = {normalize_git_path(path) for path in left_files if path}
    right_normalized = {normalize_git_path(path) for path in right_files if path}
    left_roots = {path.split("/", 1)[0] for path in left_normalized if path}
    right_roots = {path.split("/", 1)[0] for path in right_normalized if path}
    left_dirs = {str(Path(path).parent).replace("\\", "/") for path in left_normalized if "/" in path or "\\" in path}
    right_dirs = {str(Path(path).parent).replace("\\", "/") for path in right_normalized if "/" in path or "\\" in path}
    left_suffixes = {Path(path).suffix for path in left_normalized if Path(path).suffix}
    right_suffixes = {Path(path).suffix for path in right_normalized if Path(path).suffix}
    return (
        len(left_normalized & right_normalized) * 6
        + len(left_dirs & right_dirs) * 4
        + len(path_domains(list(left_normalized)) & path_domains(list(right_normalized))) * 3
        + len(left_roots & right_roots) * 2
        + len(left_suffixes & right_suffixes)
    )


def nearest_related_commit(commits: list[dict[str, Any]], index: int, candidate_files: list[str]) -> tuple[dict[str, Any], int] | None:
    best: tuple[int, int, int, int, dict[str, Any]] | None = None
    for other_index, commit in enumerate(commits):
        if other_index == index:
            continue
        score = path_affinity_score(candidate_files, commit.get("files", []) or [])
        if score <= 0:
            continue
        distance = abs(other_index - index)
        semantic_bonus = 2 if not commit_subject_is_weak(str(commit.get("subject", ""))) else 0
        current = (score, semantic_bonus, -distance, -other_index, commit)
        if best is None or current > best:
            best = current
    return (best[4], best[0]) if best else None


def nearest_semantic_commit(
    commits: list[dict[str, Any]], index: int, candidate_files: list[str]
) -> dict[str, Any] | None:
    related = nearest_related_commit(commits, index, candidate_files)
    if related is None:
        return None
    commit, _score = related
    return None if commit_subject_is_weak(str(commit.get("subject", ""))) else commit


def short_commit(commit: dict[str, Any]) -> str:
    commit_hash = str(commit.get("hash", ""))
    subject = str(commit.get("subject", ""))
    return f"{commit_hash[:7]} {subject}".strip()


def build_detected_history_candidate(
    commit: dict[str, Any],
    expected_commit: dict[str, Any] | None,
    index: int,
    *,
    related_score: int = 0,
) -> dict[str, Any]:
    commit_hash = str(commit.get("hash", ""))
    expected = short_commit(expected_commit) if expected_commit else ""
    candidate_id = f"HISTORY-DETECT-{index + 1:03d}"
    expected_is_weak = bool(expected_commit and commit_subject_is_weak(str(expected_commit.get("subject", ""))))
    if expected and not expected_is_weak:
        repair_goal = "absorb-into-existing-commit"
        recommended_action = "non-interactive-git-cli-rewrite"
        after_summary = f"`{expected}` へ吸収可能かHuman Reviewで確認する。"
    else:
        repair_goal = "manual-review-required"
        recommended_action = "manual-review-required"
        if expected:
            after_summary = f"`{expected}` は資材上の関連候補だがsubjectが薄いため、吸収、分割、message補修、no-rewriteのどれにするかHuman Reviewで判断する。"
        else:
            after_summary = "安全な吸収先を自動特定できないため、コミット資材の内容をHuman Reviewで確認する。"
    draft_commands = [f"git branch backup/{candidate_id.lower()} HEAD"]
    if commit_hash:
        draft_commands.extend(
            [
                f"git switch -c rewrite/{candidate_id.lower()} {commit_hash[:12]}^",
                f"# replay approved commits with git cherry-pick --no-commit and git commit -F <message-file>",
                "git diff --quiet <old-head>..<new-head>",
            ]
        )
    return {
        "id": candidate_id,
        "file_paths": commit.get("files", []) or [],
        "suspect_commits": [short_commit(commit)],
        "expected_commit": expected,
        "repair_goal": repair_goal,
        "independent_responsibility": "",
        "evidence_refs": [f"git show --stat {commit_hash}"] if commit_hash else [],
        "content_review_evidence": {
            "related_commit_score": related_score,
            "candidate_domains": sorted(path_domains(commit.get("files", []) or [])),
            "related_commit_subject_is_weak": expected_is_weak,
            "decision_basis": "path, directory, extension, domain, and nearby commit affinity; subject is not sufficient by itself",
        },
        "completion_criteria": [
            "対象ファイルが正しいsemantic commitへ吸収される、独立責務として維持される、message補修へ送られる、または候補が却下される。",
            "漏れコミットを正当化するためだけに新しいIssue、PR story、commit messageを後付けしない。",
            "最終的なgit logと対象ファイル履歴が承認済み計画と一致する。",
        ],
        "recommended_action": recommended_action,
        "tool_responsibility": {
            "github_api": "remote metadata/ref verification only; cannot rewrite commit graph",
            "git_cli_local": "local non-interactive commit graph rewrite and verification; authentication is not required",
            "git_cli_remote": "fetch/ls-remote/push to GitHub after local verification; authentication is required",
        },
        "reason": "1-3ファイルの小さなコミットで、subjectが薄い、またはコミット資材上の関連性確認が必要な履歴文脈が検出された。",
        "before_summary": short_commit(commit),
        "after_summary": after_summary,
        "approval_status": "pending",
        "before_after_sha_mapping": [],
        "rollback_plan": f"git reset --hard {commit_hash}" if commit_hash else "",
        "draft_commands": draft_commands,
        "verification_commands": [
            "git log --format=\"%H %s\" --max-count=20",
            "git diff --stat",
        ],
    }


def detect_history_rewrite_candidates(
    *,
    repo_path: Path,
    base: str,
    head: str,
    max_commits: int,
    max_files: int,
) -> list[dict[str, Any]]:
    commits = collect_commit_summaries(repo_path, base, head, max_commits)
    candidates: list[dict[str, Any]] = []
    for commit_index, commit in enumerate(commits):
        files = commit.get("files", []) or []
        if not 1 <= len(files) <= max_files:
            continue
        related = nearest_related_commit(commits, commit_index, files)
        expected_commit = related[0] if related else None
        related_score = related[1] if related else 0
        if not commit_subject_is_weak(str(commit.get("subject", ""))) and expected_commit is None:
            continue
        candidates.append(
            build_detected_history_candidate(
                commit,
                expected_commit,
                len(candidates),
                related_score=related_score,
            )
        )
    return candidates


def history_rewrite_candidates(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = analysis.get("history_rewrite_candidates", []) or []
    return [candidate for candidate in candidates if isinstance(candidate, dict)]


def message_repair_candidates(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = analysis.get("message_repair_candidates", []) or []
    return [candidate for candidate in candidates if isinstance(candidate, dict)]


def find_message_repair_candidate(analysis: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for candidate in message_repair_candidates(analysis):
        if str(candidate.get("id", "")) == candidate_id:
            return candidate
    raise KeyError(f"Unknown commit message repair candidate: {candidate_id}")


def maybe_find_history_rewrite_candidate(analysis: dict[str, Any], candidate_id: str) -> dict[str, Any] | None:
    for candidate in history_rewrite_candidates(analysis):
        if str(candidate.get("id", "")) == candidate_id:
            return candidate
    return None


def maybe_find_message_repair_candidate(analysis: dict[str, Any], candidate_id: str) -> dict[str, Any] | None:
    for candidate in message_repair_candidates(analysis):
        if str(candidate.get("id", "")) == candidate_id:
            return candidate
    return None


EXECUTABLE_REBASE_REPAIR_GOALS = {
    "absorb-into-existing-commit",
    "drop-empty-or-noise-commit",
    "split-into-independent-commit",
}

REBASE_REPAIR_GOALS = {
    *EXECUTABLE_REBASE_REPAIR_GOALS,
    "keep-with-evidence",
    "manual-review-required",
    "no-rewrite",
}


def validate_history_rewrite_candidates(candidates: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for candidate in candidates:
        candidate_id = str(candidate.get("id", "HISTORY-XXX"))
        file_paths = candidate.get("file_paths", []) or []
        if not isinstance(file_paths, list) or not 1 <= len(file_paths) <= 3:
            errors.append(f"{candidate_id}: file_paths must contain 1 to 3 files.")
        repair_goal = str(candidate.get("repair_goal", ""))
        if repair_goal and repair_goal not in REBASE_REPAIR_GOALS:
            errors.append(f"{candidate_id}: repair_goal is not supported.")
        approval_status = str(candidate.get("approval_status", "pending"))
        if approval_status not in {"pending", "approved", "rejected"}:
            errors.append(f"{candidate_id}: approval_status must be pending, approved, or rejected.")
        if approval_status == "approved":
            if not repair_goal:
                errors.append(f"{candidate_id}: approved rebase repair requires repair_goal.")
            if repair_goal == "absorb-into-existing-commit" and not candidate.get("expected_commit"):
                errors.append(f"{candidate_id}: absorb repair requires expected_commit.")
            if repair_goal == "keep-with-evidence" and not candidate.get("independent_responsibility"):
                errors.append(f"{candidate_id}: keep repair requires independent_responsibility.")
            if repair_goal == "keep-with-evidence" and not candidate.get("evidence_refs"):
                errors.append(f"{candidate_id}: keep repair requires evidence_refs.")
            if not candidate.get("completion_criteria"):
                errors.append(f"{candidate_id}: approved rebase repair requires completion_criteria.")
            if candidate.get("execution_status") in {"verified", "pushed"} and not candidate.get("before_after_sha_mapping"):
                errors.append(f"{candidate_id}: verified rebase repair requires before_after_sha_mapping.")
            if not candidate.get("rollback_plan"):
                errors.append(f"{candidate_id}: approved rebase repair requires rollback_plan.")
            if not candidate.get("draft_commands") and not candidate.get("replay_package_ref"):
                errors.append(f"{candidate_id}: approved rebase repair requires draft_commands or replay_package_ref.")
            for command in candidate.get("draft_commands", []) or []:
                command_text = str(command)
                if "<" in command_text or ">" in command_text or command_text.lstrip().startswith("#"):
                    errors.append(f"{candidate_id}: approved rebase repair requires concrete draft_commands.")
            if not candidate.get("verification_commands"):
                errors.append(f"{candidate_id}: approved rebase repair requires verification_commands.")
    return errors


def history_rewrite_candidate_is_resolved(candidate: dict[str, Any]) -> bool:
    approval_status = str(candidate.get("approval_status", "pending"))
    repair_goal = str(candidate.get("repair_goal", ""))
    execution_status = str(candidate.get("execution_status", "pending"))
    if approval_status == "rejected":
        return True
    if approval_status == "pending":
        return False
    if repair_goal == "no-rewrite":
        return bool(candidate.get("reason"))
    if repair_goal == "keep-with-evidence":
        return bool(candidate.get("independent_responsibility") and candidate.get("evidence_refs"))
    if repair_goal in {"absorb-into-existing-commit", "drop-empty-or-noise-commit", "split-into-independent-commit"}:
        return execution_status in {"verified", "pushed"}
    return False


def unresolved_history_rewrite_candidates(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in history_rewrite_candidates(analysis)
        if not history_rewrite_candidate_is_resolved(candidate)
    ]


def message_repair_candidate_is_resolved(candidate: dict[str, Any]) -> bool:
    approval_status = str(candidate.get("approval_status", "pending"))
    execution_status = str(candidate.get("execution_status", "pending"))
    if approval_status == "rejected":
        return True
    if approval_status == "pending":
        return False
    if approval_status == "approved":
        return execution_status in {"verified", "pushed"}
    return False


def unresolved_message_repair_candidates(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        candidate
        for candidate in message_repair_candidates(analysis)
        if not message_repair_candidate_is_resolved(candidate)
    ]


def load_analysis(repo_root: Path, work_id: str, raw_path: str) -> tuple[Path, Path, dict[str, Any]]:
    work_dir = work_dir_for_id(repo_root, work_id)
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    path = analysis_path_for(work_dir, raw_path)
    if not path.exists():
        raise FileNotFoundError(f"GitHub knowledge analysis does not exist: {path}")
    analysis = read_json(path)
    if not isinstance(analysis, dict):
        raise ValueError(f"GitHub knowledge analysis must be a JSON object: {path}")
    return work_dir, path, analysis


def latest_rebase_review_plan(work_dir: Path) -> Path:
    report_dir = process_report_dir_for_work_dir(work_dir)
    paths = list(report_dir.glob("github-history-rebase-plan-*.md"))
    if not paths:
        raise FileNotFoundError(f"Rebase plan report does not exist under: {report_dir}")
    return max(paths, key=lambda path: (path.stat().st_mtime, path.name))


def latest_message_repair_plan(work_dir: Path) -> Path:
    report_dir = process_report_dir_for_work_dir(work_dir)
    paths = list(report_dir.glob("github-history-message-repair-plan-*.md"))
    if not paths:
        raise FileNotFoundError(f"Commit message repair plan report does not exist under: {report_dir}")
    return max(paths, key=lambda path: (path.stat().st_mtime, path.name))


def latest_sync_review_plan(work_dir: Path) -> Path:
    report_dir = process_report_dir_for_work_dir(work_dir)
    paths = list(report_dir.glob("github-documentation-sync-review-plan-*.md"))
    if not paths:
        raise FileNotFoundError(f"GitHub sync review plan report does not exist under: {report_dir}")
    return max(paths, key=lambda path: (path.stat().st_mtime, path.name))


def markdown_checkbox_is_checked(value: str) -> bool:
    return bool(re.search(r"\[\s*[xX]\s*\]", value))


def parse_rebase_review_checklist(plan_path: Path) -> dict[str, str]:
    decisions: dict[str, str] = {}
    errors: list[str] = []
    for line in plan_path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped.startswith("| HISTORY-"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        candidate_id = cells[0]
        if candidate_id in decisions:
            errors.append(f"{candidate_id}: duplicate checklist row.")
            continue
        ok_checked = markdown_checkbox_is_checked(cells[1])
        ng_checked = markdown_checkbox_is_checked(cells[2])
        if ok_checked == ng_checked:
            errors.append(f"{candidate_id}: exactly one of OK or NG must be checked.")
            continue
        decisions[candidate_id] = "OK" if ok_checked else "NG"
    if not decisions and not errors:
        raise ValueError(f"No HISTORY-* OK/NG checklist rows were found in: {plan_path}")
    if errors:
        raise ValueError("Invalid rebase review checklist: " + " ".join(errors))
    return decisions


def parse_message_review_checklist(plan_path: Path) -> dict[str, str]:
    decisions: dict[str, str] = {}
    errors: list[str] = []
    for line in plan_path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped.startswith("| MESSAGE-REPAIR-"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        candidate_id = cells[0]
        if candidate_id in decisions:
            errors.append(f"{candidate_id}: duplicate checklist row.")
            continue
        ok_checked = markdown_checkbox_is_checked(cells[1])
        ng_checked = markdown_checkbox_is_checked(cells[2])
        if ok_checked == ng_checked:
            errors.append(f"{candidate_id}: exactly one of OK or NG must be checked.")
            continue
        decisions[candidate_id] = "OK" if ok_checked else "NG"
    if not decisions and not errors:
        raise ValueError(f"No MESSAGE-REPAIR-* OK/NG checklist rows were found in: {plan_path}")
    if errors:
        raise ValueError("Invalid commit message repair checklist: " + " ".join(errors))
    return decisions


def parse_sync_review_checklist(plan_path: Path) -> dict[str, str]:
    decisions: dict[str, str] = {}
    errors: list[str] = []
    for line in plan_path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0].lower() in {"action_id", "---"} or cells[0] == "-":
            continue
        if not ("[" in cells[1] and "[" in cells[2]):
            continue
        action_id = cells[0]
        if action_id in decisions:
            errors.append(f"{action_id}: duplicate checklist row.")
            continue
        ok_checked = markdown_checkbox_is_checked(cells[1])
        ng_checked = markdown_checkbox_is_checked(cells[2])
        if ok_checked == ng_checked:
            errors.append(f"{action_id}: exactly one of OK or NG must be checked.")
            continue
        decisions[action_id] = "OK" if ok_checked else "NG"
    if not decisions and not errors:
        raise ValueError(f"No GitHub sync action OK/NG checklist rows were found in: {plan_path}")
    if errors:
        raise ValueError("Invalid GitHub sync review checklist: " + " ".join(errors))
    return decisions


def approved_repair_goal_for_candidate(candidate: dict[str, Any], ok_repair_goal: str) -> str:
    if ok_repair_goal != "auto":
        return ok_repair_goal
    current_goal = str(candidate.get("repair_goal", "")).strip()
    if current_goal in EXECUTABLE_REBASE_REPAIR_GOALS:
        return current_goal
    if candidate.get("expected_commit"):
        return "absorb-into-existing-commit"
    raise ValueError(
        f"{candidate.get('id', 'HISTORY-XXX')}: OK review requires --ok-repair-goal "
        "because auto cannot derive a concrete executable repair_goal."
    )


def recommended_action_for_repair_goal(repair_goal: str) -> str:
    if repair_goal == "split-into-independent-commit":
        return "split-commit"
    if repair_goal == "no-rewrite":
        return "no-rewrite"
    if repair_goal in EXECUTABLE_REBASE_REPAIR_GOALS:
        return "non-interactive-git-cli-rewrite"
    return "manual-review-required"


def apply_rebase_review_decision(
    *,
    repo_root: Path,
    work_dir: Path,
    candidate: dict[str, Any],
    decision: str,
    ok_repair_goal: str,
    reviewed_at: str,
    plan_ref: str,
) -> dict[str, Any]:
    candidate_id = str(candidate.get("id", "HISTORY-XXX"))
    if decision == "NG":
        candidate["approval_status"] = "rejected"
        candidate["repair_goal"] = "no-rewrite"
        candidate["recommended_action"] = "no-rewrite"
        candidate["human_review_decision"] = "NG"
        candidate["human_reviewed_at"] = reviewed_at
        candidate["human_review_source"] = plan_ref
        candidate.setdefault("rejection_reason", "Human Review checklist marked NG.")
        return {
            "candidate_id": candidate_id,
            "decision": decision,
            "approval_status": "rejected",
            "repair_goal": "no-rewrite",
        }

    repair_goal = approved_repair_goal_for_candidate(candidate, ok_repair_goal)
    candidate["approval_status"] = "approved"
    candidate["repair_goal"] = repair_goal
    candidate["recommended_action"] = recommended_action_for_repair_goal(repair_goal)
    candidate["human_review_decision"] = "OK"
    candidate["human_reviewed_at"] = reviewed_at
    candidate["human_review_source"] = plan_ref
    if repair_goal in EXECUTABLE_REBASE_REPAIR_GOALS:
        candidate["draft_commands"] = []
        candidate["replay_package_ref"] = relative_to_repo(repo_root, default_rebase_replay_package_path(work_dir))
    return {
        "candidate_id": candidate_id,
        "decision": decision,
        "approval_status": "approved",
        "repair_goal": repair_goal,
    }


def create_rebase_review_intake(args: argparse.Namespace) -> dict[str, Any]:
    if args.human_check != "approved":
        raise PermissionError("rebase-review-intake requires --human-check approved.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    if args.plan_path:
        plan_path = Path(args.plan_path).resolve()
        ensure_child_path(process_report_dir_for_work_dir(work_dir), plan_path, "rebase review plan")
    else:
        plan_path = latest_rebase_review_plan(work_dir)
    decisions = parse_rebase_review_checklist(plan_path)
    all_candidates = history_rewrite_candidates(analysis)
    candidate_ids = {str(candidate.get("id", "")) for candidate in all_candidates}
    missing = sorted(candidate_id for candidate_id in candidate_ids if candidate_id and candidate_id not in decisions)
    unknown = sorted(candidate_id for candidate_id in decisions if candidate_id not in candidate_ids)
    if unknown:
        raise ValueError("Checklist contains unknown history rewrite candidates: " + ", ".join(unknown))
    if missing and not args.allow_partial:
        raise ValueError(
            "Checklist is incomplete. Missing decisions for: "
            + ", ".join(missing)
            + ". Use --allow-partial to intake only checked rows."
        )

    reviewed_at = utc_now_iso()
    plan_ref = relative_to_repo(repo_root, plan_path)
    updates = [
        apply_rebase_review_decision(
            repo_root=repo_root,
            work_dir=work_dir,
            candidate=candidate,
            decision=decisions[str(candidate.get("id"))],
            ok_repair_goal=str(args.ok_repair_goal or "auto"),
            reviewed_at=reviewed_at,
            plan_ref=plan_ref,
        )
        for candidate in all_candidates
        if str(candidate.get("id")) in decisions
    ]
    errors = validate_history_rewrite_candidates(
        [
            candidate
            for candidate in all_candidates
            if str(candidate.get("id")) in decisions and candidate.get("approval_status") == "approved"
        ]
    )
    if errors:
        raise ValueError("Rebase review intake produced invalid approved candidates: " + " ".join(errors))

    analysis.setdefault("rebase_review_intakes", []).append(
        {
            "reviewed_at": reviewed_at,
            "plan_path": plan_ref,
            "ok_repair_goal": str(args.ok_repair_goal or "auto"),
            "allow_partial": bool(args.allow_partial),
            "candidate_ids": [update["candidate_id"] for update in updates],
            "approved_count": sum(1 for update in updates if update["approval_status"] == "approved"),
            "rejected_count": sum(1 for update in updates if update["approval_status"] == "rejected"),
        }
    )
    write_json(analysis_path, analysis)
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-KNOWLEDGE-ANALYSIS",
        "GitHub Knowledge Analysis",
        analysis_path,
        "report",
    )
    return {
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "plan_path": plan_ref,
        "candidate_count": len(updates),
        "approved_count": sum(1 for update in updates if update["approval_status"] == "approved"),
        "rejected_count": sum(1 for update in updates if update["approval_status"] == "rejected"),
        "decisions": updates,
    }


def commit_subject_and_body(repo_path: Path, commit: str) -> tuple[str, str]:
    message = replay_commit_metadata(repo_path, commit)["message"].rstrip()
    if not message:
        return "", ""
    lines = message.splitlines()
    subject = lines[0].strip()
    body = "\n".join(lines[1:]).strip()
    return subject, body


def paths_for_commit(repo_path: Path, commit: str) -> list[str]:
    return sorted({new_path for _status, _old_path, new_path in changed_paths_for_commit(repo_path, commit)})


def infer_commit_type_scope(paths: list[str], subject: str) -> tuple[str, str]:
    lowered = [path.replace("\\", "/").lower() for path in paths]
    subject_lower = subject.lower()
    if lowered and all(path.endswith((".md", ".rst", ".txt")) or path.startswith("docs/") for path in lowered):
        return "docs", "docs"
    if any("/tests/" in f"/{path}" or path.startswith("tests/") or "pytest" in path for path in lowered):
        return "test", "runtime"
    if any(path.startswith("runtime/") for path in lowered):
        return ("fix" if any(word in subject_lower for word in ["fix", "修正", "是正", "guard"]) else "feat", "runtime")
    if any(path.startswith("skills/") for path in lowered):
        return "docs", "workflow"
    if any(path.startswith(".github/") for path in lowered):
        return "chore", "github"
    if any(path in {".gitignore", ".editorconfig", "pytest.ini"} or path.startswith("templates/") for path in lowered):
        return "chore", "config"
    if any(path.startswith("work/requirements/") for path in lowered):
        return "docs", "requirements"
    return ("fix" if any(word in subject_lower for word in ["fix", "修正", "是正"]) else "chore", "repo")


def summarize_commit_responsibility(paths: list[str], subject: str) -> str:
    clean_subject = re.sub(r"^(update|fix|docs|chore|feat|test)(\([^)]*\))?:\s*", "", subject, flags=re.IGNORECASE).strip()
    if clean_subject and not contains_mojibake(clean_subject) and clean_subject.lower() not in {"update", "fix", "修正", "対応", "変更"}:
        return clean_subject[:80]
    domains = sorted({path.replace("\\", "/").split("/", 1)[0] for path in paths if path})
    if domains:
        return f"{', '.join(domains[:3])} の責務を明確化"
    return "履歴上の責務を明確化"


def proposed_commit_message_for_repair(commit: str, subject: str, paths: list[str]) -> tuple[str, str]:
    commit_type, scope = infer_commit_type_scope(paths, subject)
    responsibility = summarize_commit_responsibility(paths, subject)
    proposed_subject = f"{commit_type}({scope}): {responsibility}"
    path_summary = ", ".join(paths[:8]) if paths else "(no changed paths)"
    body = "\n".join(
        [
            "Intent: GitHub commit listで変更責務を読み取れるようにする。",
            f"Scope: {path_summary}",
            "Decision: rebase整備後のtreeを変えず、commit messageだけをsemantic subject/bodyへ補修する。",
            "Impact: GitHub履歴、RAG、後続AI workflowの検索・判断材料を改善する。",
            f"Source-Commit: {commit}",
        ]
    )
    return proposed_subject, proposed_subject + "\n\n" + body + "\n"


def detect_message_repair_candidates(
    *,
    repo_path: Path,
    source_ref: str,
    max_commits: int,
) -> list[dict[str, Any]]:
    commits = commit_sequence(repo_path, source_ref)[-max_commits:]
    candidates: list[dict[str, Any]] = []
    for commit in commits:
        subject, body = commit_subject_and_body(repo_path, commit)
        if not commit_subject_is_weak(subject) and body and not contains_mojibake(subject):
            continue
        paths = paths_for_commit(repo_path, commit)
        proposed_subject, proposed_message = proposed_commit_message_for_repair(commit, subject, paths)
        candidates.append(
            {
                "id": f"MESSAGE-REPAIR-{len(candidates) + 1:03d}",
                "commit": commit,
                "current_subject": subject,
                "proposed_subject": proposed_subject,
                "proposed_commit_message": proposed_message,
                "file_paths": paths,
                "reason": "Commit subject/body is weak for GitHub commit-list and future RAG retrieval.",
                "approval_status": "pending",
                "execution_status": "pending",
                "verification_commands": [
                    "git log --format=\"%H %s\" --max-count=20",
                    f"git diff --quiet {source_ref}..HEAD",
                ],
            }
        )
    return candidates


def message_repair_checklist(candidates: list[dict[str, Any]]) -> str:
    lines = [
        "## 候補別 OK / NG チェックリスト",
        "",
        "このチェックリストは commit message/body repair のHuman Review用です。対象候補の `OK` または `NG` に1つだけチェックしてください。",
        "",
        "| 候補ID | OK欄 | NG欄 | commit | 現在のsubject | 提案subject | 対象ファイル |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        paths = ", ".join(candidate.get("file_paths", [])[:4])
        lines.append(
            "| {id} | [ ] OK | [ ] NG | {commit} | {current} | {proposed} | {paths} |".format(
                id=candidate.get("id", ""),
                commit=str(candidate.get("commit", ""))[:12],
                current=str(candidate.get("current_subject", "")).replace("|", "\\|"),
                proposed=str(candidate.get("proposed_subject", "")).replace("|", "\\|"),
                paths=paths.replace("|", "\\|"),
            )
        )
    return "\n".join(lines)


def build_message_repair_plan(analysis: dict[str, Any], candidates: list[dict[str, Any]], *, source_ref: str) -> str:
    return "\n".join(
        [
            "# Git Commit Message Repair Plan",
            "",
            "この計画はrebase整備後に、GitHub commit listで意味が通るsubject/bodyへ補修するためのHuman Review資料です。",
            "source treeは変更せず、既存のtree-preserving replay runtimeでmessage_overridesだけを適用します。",
            "",
            "## Target",
            "",
            f"- Repository: `{analysis.get('repository', '')}`",
            f"- Branch: `{analysis.get('target_branch', '')}`",
            f"- Source ref: `{source_ref}`",
            f"- Candidate count: `{len(candidates)}`",
            "",
            message_repair_checklist(candidates),
            "",
            "## Verification",
            "",
            "- before/after SHA mappingを出力する",
            "- final treeがsource refと一致することを確認する",
            "- `git log --format=\"%H %s\" --max-count=20` を実行する",
            "- remote反映は `force-with-lease` で expected remote SHA と一致する場合だけ行う",
        ]
    )


def create_message_repair_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    repo_path = Path(args.git_repo).resolve() if args.git_repo else repo_root
    source_ref = str(args.source_ref or "").strip() or f"origin/{analysis.get('target_branch', '')}"
    candidates = detect_message_repair_candidates(
        repo_path=repo_path,
        source_ref=source_ref,
        max_commits=int(args.max_commits or 200),
    )
    analysis["message_repair_candidates"] = candidates
    output_path = (
        Path(args.output).resolve()
        if args.output
        else process_report_dir_for_work_dir(work_dir) / f"github-history-message-repair-plan-{local_timestamp()}.md"
    )
    write_markdown(output_path, build_message_repair_plan(analysis, candidates, source_ref=source_ref))
    analysis.setdefault("message_repair_plans", []).append(
        {
            "generated_at": utc_now_iso(),
            "plan_path": relative_to_repo(repo_root, output_path),
            "source_ref": source_ref,
            "candidate_count": len(candidates),
        }
    )
    write_json(analysis_path, analysis)
    register_artifact(repo_root, work_dir, "GITHUB-HISTORY-MESSAGE-REPAIR-PLAN", "Git Commit Message Repair Plan", output_path, "report")
    return {
        "message_repair_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "candidate_count": len(candidates),
        "source_ref": source_ref,
    }


def apply_message_review_decision(
    *,
    candidate: dict[str, Any],
    decision: str,
    reviewed_at: str,
    plan_ref: str,
) -> dict[str, Any]:
    candidate_id = str(candidate.get("id", "MESSAGE-REPAIR-XXX"))
    candidate["human_review_decision"] = decision
    candidate["human_reviewed_at"] = reviewed_at
    candidate["human_review_source"] = plan_ref
    if decision == "NG":
        candidate["approval_status"] = "rejected"
        candidate["execution_status"] = "pending"
        return {"candidate_id": candidate_id, "approval_status": "rejected", "decision": decision}
    if not candidate.get("proposed_commit_message"):
        raise ValueError(f"{candidate_id}: OK review requires proposed_commit_message.")
    candidate["approval_status"] = "approved"
    candidate["execution_status"] = "pending"
    return {"candidate_id": candidate_id, "approval_status": "approved", "decision": decision}


def create_message_review_intake(args: argparse.Namespace) -> dict[str, Any]:
    if args.human_check != "approved":
        raise PermissionError("message-review-intake requires --human-check approved.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    if args.plan_path:
        plan_path = Path(args.plan_path).resolve()
        ensure_child_path(process_report_dir_for_work_dir(work_dir), plan_path, "message repair plan")
    else:
        plan_path = latest_message_repair_plan(work_dir)
    decisions = parse_message_review_checklist(plan_path)
    candidates = message_repair_candidates(analysis)
    candidate_ids = {str(candidate.get("id", "")) for candidate in candidates}
    unknown = sorted(candidate_id for candidate_id in decisions if candidate_id not in candidate_ids)
    missing = sorted(candidate_id for candidate_id in candidate_ids if candidate_id and candidate_id not in decisions)
    if unknown:
        raise ValueError("Checklist contains unknown commit message repair candidates: " + ", ".join(unknown))
    if missing and not args.allow_partial:
        raise ValueError(
            "Checklist is incomplete. Missing decisions for: "
            + ", ".join(missing)
            + ". Use --allow-partial to intake only checked rows."
        )
    reviewed_at = utc_now_iso()
    plan_ref = relative_to_repo(repo_root, plan_path)
    updates = [
        apply_message_review_decision(
            candidate=candidate,
            decision=decisions[str(candidate.get("id"))],
            reviewed_at=reviewed_at,
            plan_ref=plan_ref,
        )
        for candidate in candidates
        if str(candidate.get("id")) in decisions
    ]
    analysis.setdefault("message_review_intakes", []).append(
        {
            "reviewed_at": reviewed_at,
            "plan_path": plan_ref,
            "allow_partial": bool(args.allow_partial),
            "candidate_ids": [update["candidate_id"] for update in updates],
            "approved_count": sum(1 for update in updates if update["approval_status"] == "approved"),
            "rejected_count": sum(1 for update in updates if update["approval_status"] == "rejected"),
        }
    )
    write_json(analysis_path, analysis)
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-ANALYSIS", "GitHub Knowledge Analysis", analysis_path, "report")
    return {
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "plan_path": plan_ref,
        "candidate_count": len(updates),
        "approved_count": sum(1 for update in updates if update["approval_status"] == "approved"),
        "rejected_count": sum(1 for update in updates if update["approval_status"] == "rejected"),
        "decisions": updates,
    }


def create_detect_rebase_candidates(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    git_repo = Path(args.git_repo).resolve() if args.git_repo else repo_root
    base = "" if getattr(args, "all_history", False) else args.base
    detected = detect_history_rewrite_candidates(
        repo_path=git_repo,
        base=base,
        head=args.head,
        max_commits=args.max_commits,
        max_files=args.max_files,
    )
    existing = history_rewrite_candidates(analysis) if args.append else []
    analysis["history_rewrite_candidates"] = existing + detected
    write_json(analysis_path, analysis)
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-KNOWLEDGE-ANALYSIS",
        "GitHub Knowledge Analysis",
        analysis_path,
        "report",
    )
    return {
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "git_repo": str(git_repo),
        "base": base,
        "head": args.head,
        "all_history": bool(getattr(args, "all_history", False)),
        "candidate_count": len(detected),
        "total_candidate_count": len(analysis["history_rewrite_candidates"]),
    }


def find_history_rewrite_candidate(analysis: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for candidate in history_rewrite_candidates(analysis):
        if candidate.get("id") == candidate_id:
            return candidate
    raise ValueError(f"History rewrite candidate not found: {candidate_id}")


def is_interactive_git_command(command: str) -> bool:
    normalized = " ".join(command.strip().lower().split())
    return " rebase -i " in f" {normalized} " or " rebase --interactive " in f" {normalized} "


def parse_git_cli_command(command: str) -> list[str]:
    stripped = command.strip()
    if not stripped.startswith("git "):
        raise ValueError(f"Only git commands can be executed by rebase-apply: {command}")
    if any(token in stripped for token in ["\n", "\r", "&&", "||", "|", ";"]):
        raise ValueError("Git CLI command must be a single command without shell chaining.")
    if "<" in stripped or ">" in stripped:
        raise ValueError("Git CLI command must be concrete before execution; placeholders are not allowed.")
    if is_interactive_git_command(stripped):
        raise ValueError(
            "Interactive rebase is not supported by runtime automation. "
            "Use non-interactive Git CLI rewrite commands such as cherry-pick/commit-tree/update-ref."
        )
    parts = shlex.split(stripped, posix=True)
    if not parts or parts[0] != "git":
        raise ValueError(f"Only git commands can be executed by rebase-apply: {command}")
    return parts


def run_rebase_command(repo_path: Path, command: str, *, allow_interactive: bool, dry_run: bool) -> dict[str, Any]:
    parts = parse_git_cli_command(command)
    stripped = " ".join(shlex.quote(part) for part in parts)
    if allow_interactive and is_interactive_git_command(command):
        raise ValueError("Interactive rebase remains unsupported by github-knowledge-maintenance runtime.")
    if dry_run:
        return {"command": stripped, "skipped": True, "returncode": 0, "stdout": "", "stderr": ""}
    result = subprocess.run(
        parts,
        cwd=repo_path,
        shell=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return {
        "command": stripped,
        "skipped": False,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def create_rebase_apply(args: argparse.Namespace) -> dict[str, Any]:
    if args.human_check != "approved":
        raise PermissionError("rebase-apply requires --human-check approved.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    require_github_operation_gate(repo_root, work_dir, require_mutation_gate=True)
    candidate = find_history_rewrite_candidate(analysis, args.candidate_id)
    if candidate.get("approval_status") != "approved":
        raise PermissionError(f"{args.candidate_id} is not approved.")
    validation_errors = validate_history_rewrite_candidates([candidate])
    if validation_errors:
        raise ValueError("Approved rebase candidate is not executable: " + " ".join(validation_errors))
    if candidate.get("repair_goal") == "no-rewrite":
        raise ValueError(f"{args.candidate_id} has repair_goal no-rewrite.")
    git_repo = Path(args.git_repo).resolve() if args.git_repo else repo_root
    commands = [str(command) for command in candidate.get("draft_commands", [])]
    results = [
        run_rebase_command(git_repo, command, allow_interactive=False, dry_run=args.dry_run)
        for command in commands
    ]
    failed = [result for result in results if result["returncode"] != 0]
    if failed:
        candidate["execution_status"] = "failed"
        candidate["executed_at"] = utc_now_iso()
        candidate["execution_result"] = failed[0]
        write_json(analysis_path, analysis)
        raise RuntimeError("rebase-apply command failed: " + failed[0]["command"])
    verification_commands = [str(command) for command in candidate.get("verification_commands", [])]
    verification_results = [
        run_rebase_command(git_repo, command, allow_interactive=False, dry_run=args.dry_run)
        for command in verification_commands
    ]
    failed_verification = [result for result in verification_results if result["returncode"] != 0]
    if failed_verification:
        candidate["execution_status"] = "verification-failed"
        candidate["executed_at"] = utc_now_iso()
        candidate["execution_result"] = {
            "commands": results,
            "verification": verification_results,
        }
        write_json(analysis_path, analysis)
        raise RuntimeError("rebase-apply verification failed: " + failed_verification[0]["command"])
    candidate["execution_status"] = "dry-run" if args.dry_run else "verified"
    candidate["executed_at"] = utc_now_iso()
    candidate["execution_result"] = {
        "commands": results,
        "verification": verification_results,
        "verification_required": False,
    }
    write_json(analysis_path, analysis)
    return {
        "candidate_id": args.candidate_id,
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "git_repo": str(git_repo),
        "dry_run": bool(args.dry_run),
        "executed_count": 0 if args.dry_run else len(results),
        "planned_count": len(results),
        "verification_count": len(verification_results),
        "results": results,
        "verification_results": verification_results,
        "gate_restart": github_knowledge_gate_restart(
            "github-knowledge-rebase-apply-gate",
            status="dry-run" if args.dry_run else "verified",
            restart_reason="normal-rebase-apply-gate",
        ),
    }


EMPTY_GIT_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


def safe_branch_segment(value: str) -> str:
    segment = slugify(value.replace("/", "-").replace("\\", "-"))
    return segment or "target"


def ensure_child_path(parent: Path, child: Path, label: str) -> Path:
    parent_resolved = parent.resolve()
    child_resolved = child.resolve()
    if child_resolved != parent_resolved and parent_resolved not in child_resolved.parents:
        raise ValueError(f"{label} must stay under {parent_resolved}: {child_resolved}")
    return child_resolved


def default_rebase_replay_package_path(work_dir: Path) -> Path:
    return context_file(work_dir, "rebase-replay-package.json")


def default_message_repair_package_path(work_dir: Path) -> Path:
    return context_file(work_dir, "message-repair-package.json")


def load_rebase_replay_package(work_dir: Path, raw_path: str) -> tuple[Path, dict[str, Any]]:
    path = Path(raw_path).resolve() if raw_path else default_rebase_replay_package_path(work_dir)
    if not path.exists():
        raise FileNotFoundError(f"Rebase replay package does not exist: {path}")
    package = read_json(path)
    if not isinstance(package, dict):
        raise ValueError(f"Rebase replay package must be a JSON object: {path}")
    return path, package


COMMIT_REF_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def commit_ref_from_candidate_value(value: Any, *, label: str) -> str:
    token = str(value or "").strip().split(maxsplit=1)[0] if str(value or "").strip() else ""
    if not COMMIT_REF_RE.fullmatch(token):
        raise ValueError(f"{label} must start with a 7-40 character Git SHA: {value}")
    return token


def candidate_message_override(candidate: dict[str, Any]) -> str:
    for key in ["message_override", "proposed_commit_message", "proposed_message"]:
        value = candidate.get(key)
        if isinstance(value, dict):
            message = str(value.get("message", "")).strip()
        else:
            message = str(value or "").strip()
        if message:
            return message.rstrip() + "\n"
    return ""


def selected_rebase_replay_candidates(analysis: dict[str, Any], candidate_ids: list[str]) -> list[dict[str, Any]]:
    all_candidates = history_rewrite_candidates(analysis)
    if candidate_ids:
        selected = [find_history_rewrite_candidate(analysis, candidate_id) for candidate_id in candidate_ids]
    else:
        selected = [
            candidate
            for candidate in all_candidates
            if candidate.get("approval_status") == "approved"
            and candidate.get("repair_goal")
            in {"absorb-into-existing-commit", "drop-empty-or-noise-commit", "split-into-independent-commit"}
            and candidate.get("execution_status") not in {"verified", "pushed"}
        ]
    if not selected:
        raise ValueError("No approved executable history rewrite candidates were selected.")
    return selected


def selected_message_repair_candidates(analysis: dict[str, Any], candidate_ids: list[str]) -> list[dict[str, Any]]:
    all_candidates = message_repair_candidates(analysis)
    if candidate_ids:
        selected = [find_message_repair_candidate(analysis, candidate_id) for candidate_id in candidate_ids]
    else:
        selected = [
            candidate
            for candidate in all_candidates
            if candidate.get("approval_status") == "approved"
            and candidate.get("execution_status") not in {"verified", "pushed"}
        ]
    if not selected:
        raise ValueError("No approved executable commit message repair candidates were selected.")
    return selected


def build_rebase_replay_package_from_candidates(
    analysis: dict[str, Any],
    candidates: list[dict[str, Any]],
    *,
    target_branch: str,
    source_ref: str,
    remote: str,
    expected_remote_sha: str,
    allow_push: bool,
    apply_mode: str,
) -> dict[str, Any]:
    target_branch = target_branch or str(analysis.get("target_branch", "")).strip()
    if not target_branch:
        raise ValueError("rebase-replay-package requires --target-branch or analysis.target_branch.")
    source_ref = source_ref or target_branch
    package: dict[str, Any] = {
        "schema_version": "1.0",
        "target_branch": target_branch,
        "source_ref": source_ref,
        "remote": remote or "origin",
        "apply_mode": apply_mode,
        "expected_remote_sha": expected_remote_sha,
        "candidate_ids": [],
        "output_branch": "",
        "allow_push": bool(allow_push),
        "replay_strategy": "tree-preserving",
        "absorb": [],
        "drop": [],
        "remove_after_apply": [],
        "message_overrides": [],
        "verification_commands": [],
    }
    seen_verification: set[str] = set()
    for candidate in candidates:
        candidate_id = str(candidate.get("id", "HISTORY-XXX"))
        if candidate.get("approval_status") != "approved":
            raise PermissionError(f"{candidate_id} is not approved.")
        repair_goal = str(candidate.get("repair_goal", ""))
        suspect_refs = [
            commit_ref_from_candidate_value(value, label=f"{candidate_id}.suspect_commits")
            for value in candidate.get("suspect_commits", []) or []
        ]
        if not suspect_refs:
            raise ValueError(f"{candidate_id} requires suspect_commits.")
        package["candidate_ids"].append(candidate_id)
        if repair_goal == "absorb-into-existing-commit":
            target = commit_ref_from_candidate_value(candidate.get("expected_commit"), label=f"{candidate_id}.expected_commit")
            package["absorb"].append({"target": target, "sources": suspect_refs})
            message = candidate_message_override(candidate)
            if message:
                package["message_overrides"].append({"commit": target, "message": message})
        elif repair_goal == "drop-empty-or-noise-commit":
            package["drop"].extend(suspect_refs)
        elif repair_goal == "split-into-independent-commit":
            message = candidate_message_override(candidate)
            if not message:
                raise ValueError(f"{candidate_id} split repair requires message_override or proposed_commit_message.")
            for commit in suspect_refs:
                package["message_overrides"].append({"commit": commit, "message": message})
        else:
            raise ValueError(f"{candidate_id} is not an executable replay repair goal.")
        for command in candidate.get("verification_commands", []) or []:
            command_text = str(command).strip()
            if command_text and command_text not in seen_verification:
                package["verification_commands"].append(command_text)
                seen_verification.add(command_text)
    if not package["verification_commands"]:
        package["verification_commands"].append(f"git diff --quiet {source_ref}..HEAD")
    validate_rebase_replay_package(normalize_rebase_replay_package(package), analysis, push=bool(allow_push))
    return package


def build_message_repair_package_from_candidates(
    analysis: dict[str, Any],
    candidates: list[dict[str, Any]],
    *,
    target_branch: str,
    source_ref: str,
    remote: str,
    expected_remote_sha: str,
    allow_push: bool,
    apply_mode: str,
) -> dict[str, Any]:
    target_branch = target_branch or str(analysis.get("target_branch", "")).strip()
    if not target_branch:
        raise ValueError("message-repair-package requires --target-branch or analysis.target_branch.")
    source_ref = source_ref or f"origin/{target_branch}"
    package: dict[str, Any] = {
        "schema_version": "1.0",
        "target_branch": target_branch,
        "source_ref": source_ref,
        "remote": remote or "origin",
        "apply_mode": apply_mode,
        "expected_remote_sha": expected_remote_sha,
        "candidate_ids": [],
        "output_branch": "",
        "allow_push": bool(allow_push),
        "replay_strategy": "tree-preserving",
        "absorb": [],
        "drop": [],
        "remove_after_apply": [],
        "message_overrides": [],
        "verification_commands": [],
    }
    seen_verification: set[str] = set()
    for candidate in candidates:
        candidate_id = str(candidate.get("id", "MESSAGE-REPAIR-XXX"))
        if candidate.get("approval_status") != "approved":
            raise PermissionError(f"{candidate_id} is not approved.")
        commit = commit_ref_from_candidate_value(candidate.get("commit"), label=f"{candidate_id}.commit")
        message = str(candidate.get("proposed_commit_message", "")).rstrip()
        if not message:
            raise ValueError(f"{candidate_id} requires proposed_commit_message.")
        package["candidate_ids"].append(candidate_id)
        package["message_overrides"].append({"commit": commit, "message": message + "\n"})
        for command in candidate.get("verification_commands", []) or []:
            command_text = str(command).strip()
            if command_text and command_text not in seen_verification:
                package["verification_commands"].append(command_text)
                seen_verification.add(command_text)
    if not package["verification_commands"]:
        package["verification_commands"].append(f"git diff --quiet {source_ref}..HEAD")
    validate_rebase_replay_package(normalize_rebase_replay_package(package), analysis, push=bool(allow_push))
    return package


def create_rebase_replay_package(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    candidates = selected_rebase_replay_candidates(analysis, [str(item) for item in args.candidate_id or []])
    output_path = Path(args.output).resolve() if args.output else default_rebase_replay_package_path(work_dir)
    ensure_child_path(context_dir_for_work_dir(work_dir), output_path, "rebase replay package")
    package = build_rebase_replay_package_from_candidates(
        analysis,
        candidates,
        target_branch=str(args.target_branch or "").strip(),
        source_ref=str(args.source_ref or "").strip(),
        remote=str(args.remote or "origin").strip() or "origin",
        expected_remote_sha=str(args.expected_remote_sha or "").strip(),
        allow_push=bool(args.allow_push),
        apply_mode=str(args.apply_mode or "direct").strip() or "direct",
    )
    write_json(output_path, package)
    package_ref = relative_to_repo(repo_root, output_path)
    for candidate in candidates:
        candidate["replay_package_ref"] = package_ref
    analysis.setdefault("rebase_replay_packages", []).append(
        {
            "generated_at": utc_now_iso(),
            "package_path": package_ref,
            "candidate_ids": package["candidate_ids"],
            "target_branch": package["target_branch"],
            "source_ref": package["source_ref"],
            "apply_mode": package["apply_mode"],
            "replay_strategy": package.get("replay_strategy", "tree-preserving"),
            "allow_push": package["allow_push"],
        }
    )
    write_json(analysis_path, analysis)
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-HISTORY-REBASE-REPLAY-PACKAGE",
        "GitHub History Rebase Replay Package",
        output_path,
        "other",
    )
    return {
        "rebase_replay_package": package_ref,
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "candidate_count": len(package["candidate_ids"]),
        "candidate_ids": package["candidate_ids"],
        "target_branch": package["target_branch"],
        "source_ref": package["source_ref"],
        "apply_mode": package["apply_mode"],
        "allow_push": package["allow_push"],
    }


def create_message_repair_package(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    candidates = selected_message_repair_candidates(analysis, [str(item) for item in args.candidate_id or []])
    output_path = Path(args.output).resolve() if args.output else default_message_repair_package_path(work_dir)
    ensure_child_path(context_dir_for_work_dir(work_dir), output_path, "commit message repair package")
    package = build_message_repair_package_from_candidates(
        analysis,
        candidates,
        target_branch=str(args.target_branch or "").strip(),
        source_ref=str(args.source_ref or "").strip(),
        remote=str(args.remote or "origin").strip() or "origin",
        expected_remote_sha=str(args.expected_remote_sha or "").strip(),
        allow_push=bool(args.allow_push),
        apply_mode=str(args.apply_mode or "auto-3way").strip() or "auto-3way",
    )
    write_json(output_path, package)
    package_ref = relative_to_repo(repo_root, output_path)
    for candidate in candidates:
        candidate["replay_package_ref"] = package_ref
    analysis.setdefault("message_repair_packages", []).append(
        {
            "generated_at": utc_now_iso(),
            "package_path": package_ref,
            "candidate_ids": package["candidate_ids"],
            "target_branch": package["target_branch"],
            "source_ref": package["source_ref"],
            "apply_mode": package["apply_mode"],
            "allow_push": package["allow_push"],
        }
    )
    write_json(analysis_path, analysis)
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-HISTORY-MESSAGE-REPAIR-PACKAGE",
        "Git Commit Message Repair Package",
        output_path,
        "other",
    )
    return {
        "message_repair_package": package_ref,
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "candidate_count": len(package["candidate_ids"]),
        "candidate_ids": package["candidate_ids"],
        "target_branch": package["target_branch"],
        "source_ref": package["source_ref"],
        "apply_mode": package["apply_mode"],
        "allow_push": package["allow_push"],
    }


def package_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def package_commit_map(value: Any, *, key_name: str = "commit") -> dict[str, list[str]]:
    if isinstance(value, dict):
        return {str(key): [str(item) for item in package_list(items)] for key, items in value.items()}
    result: dict[str, list[str]] = {}
    for item in package_list(value):
        if not isinstance(item, dict):
            continue
        key = str(item.get(key_name, item.get("target", ""))).strip()
        if not key:
            continue
        raw_values = item.get("sources", item.get("paths", []))
        result[key] = [str(raw) for raw in package_list(raw_values)]
    return result


def package_message_overrides(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {str(key): str(message) for key, message in value.items()}
    result: dict[str, str] = {}
    for item in package_list(value):
        if not isinstance(item, dict):
            continue
        commit = str(item.get("commit", "")).strip()
        message = str(item.get("message", "")).rstrip()
        if commit and message:
            result[commit] = message + "\n"
    return result


def resolve_commit_ref(repo_path: Path, ref: str, *, label: str) -> str:
    value = str(ref or "").strip()
    if not value:
        return ""
    try:
        return git_text(repo_path, ["rev-parse", "--verify", f"{value}^{{commit}}"]).strip()
    except RuntimeError as exc:
        raise ValueError(f"{label} must resolve to a Git commit: {value}") from exc


def resolve_commit_map(repo_path: Path, value: dict[str, list[str]], *, label: str) -> dict[str, list[str]]:
    resolved: dict[str, list[str]] = {}
    for target, sources in value.items():
        full_target = resolve_commit_ref(repo_path, target, label=f"{label}.target")
        resolved[full_target] = [
            resolve_commit_ref(repo_path, source, label=f"{label}.source")
            for source in sources
        ]
    return resolved


def resolve_commit_set(repo_path: Path, value: set[str], *, label: str) -> set[str]:
    return {
        resolve_commit_ref(repo_path, item, label=label)
        for item in value
    }


def resolve_message_overrides(repo_path: Path, value: dict[str, str]) -> dict[str, str]:
    return {
        resolve_commit_ref(repo_path, commit, label="message_overrides.commit"): message
        for commit, message in value.items()
    }


def normalize_rebase_replay_package(package: dict[str, Any], repo_path: Path | None = None) -> dict[str, Any]:
    target_branch = str(package.get("target_branch", "")).strip()
    source_ref = str(package.get("source_ref", "")).strip() or f"origin/{target_branch}"
    apply_mode = str(package.get("apply_mode", "direct")).strip() or "direct"
    if not target_branch:
        raise ValueError("Rebase replay package requires target_branch.")
    if not source_ref:
        raise ValueError("Rebase replay package requires source_ref.")
    candidate_ids = [str(item) for item in package_list(package.get("candidate_ids")) if str(item).strip()]
    normalized = {
        "target_branch": target_branch,
        "source_ref": source_ref,
        "remote": str(package.get("remote", "origin")).strip() or "origin",
        "apply_mode": apply_mode,
        "replay_strategy": str(package.get("replay_strategy", "tree-preserving")).strip() or "tree-preserving",
        "expected_remote_sha": str(package.get("expected_remote_sha", "")).strip(),
        "candidate_ids": candidate_ids,
        "output_branch": str(package.get("output_branch", "")).strip(),
        "absorb": package_commit_map(package.get("absorb")),
        "drop": {str(item) for item in package_list(package.get("drop"))},
        "remove_after_apply": package_commit_map(package.get("remove_after_apply")),
        "message_overrides": package_message_overrides(package.get("message_overrides")),
        "verification_commands": [str(item) for item in package_list(package.get("verification_commands"))],
        "allow_push": bool(package.get("allow_push", False)),
    }
    if repo_path is None:
        return normalized
    normalized["absorb"] = resolve_commit_map(repo_path, normalized["absorb"], label="absorb")
    normalized["drop"] = resolve_commit_set(repo_path, normalized["drop"], label="drop")
    normalized["remove_after_apply"] = resolve_commit_map(
        repo_path,
        normalized["remove_after_apply"],
        label="remove_after_apply",
    )
    normalized["message_overrides"] = resolve_message_overrides(repo_path, normalized["message_overrides"])
    return normalized


def validate_rebase_replay_package(package: dict[str, Any], analysis: dict[str, Any], *, push: bool) -> None:
    if package["apply_mode"] not in {"direct", "git-3way", "auto-3way"}:
        raise ValueError("Rebase replay package apply_mode must be direct, git-3way, or auto-3way.")
    if package["candidate_ids"]:
        for candidate_id in package["candidate_ids"]:
            history_candidate = maybe_find_history_rewrite_candidate(analysis, candidate_id)
            message_candidate = maybe_find_message_repair_candidate(analysis, candidate_id)
            if history_candidate is None and message_candidate is None:
                raise KeyError(f"Unknown rebase replay candidate: {candidate_id}")
            candidate = history_candidate or message_candidate or {}
            if candidate.get("approval_status") != "approved":
                raise PermissionError(f"{candidate_id} is not approved.")
            if history_candidate is not None:
                if candidate.get("repair_goal") not in {
                    "absorb-into-existing-commit",
                    "drop-empty-or-noise-commit",
                    "split-into-independent-commit",
                }:
                    raise ValueError(f"{candidate_id} is not an executable replay repair goal.")
            elif not candidate.get("proposed_commit_message"):
                raise ValueError(f"{candidate_id} is not an executable commit message repair candidate.")
    if push:
        if not package["allow_push"]:
            raise PermissionError("Rebase replay package does not allow push.")
        if not package["expected_remote_sha"]:
            raise ValueError("Push requires expected_remote_sha for force-with-lease.")
    replay_inputs = set(package["absorb"].keys()) | package["drop"] | set(package["remove_after_apply"].keys())
    for sources in package["absorb"].values():
        replay_inputs.update(sources)
    if not replay_inputs and not package["message_overrides"]:
        raise ValueError("Rebase replay package has no replay actions.")


def validate_rebase_replay_actions(package: dict[str, Any], original_commits: list[str]) -> None:
    commit_set = set(original_commits)
    absorbed_sources = {source for sources in package["absorb"].values() for source in sources}
    skipped_commits = absorbed_sources | package["drop"]
    action_refs = set(package["absorb"].keys()) | skipped_commits | set(package["remove_after_apply"].keys())
    missing_refs = sorted(action_refs - commit_set)
    if missing_refs:
        raise RuntimeError("Replay package references commits outside source history: " + ", ".join(missing_refs))
    conflicting_targets = sorted(set(package["absorb"].keys()) & skipped_commits)
    if conflicting_targets:
        raise RuntimeError("Absorb target is also scheduled to be skipped: " + ", ".join(conflicting_targets))


def connected_absorb_components(absorb: dict[str, list[str]]) -> list[set[str]]:
    adjacency: dict[str, set[str]] = {}
    for target, sources in absorb.items():
        adjacency.setdefault(target, set())
        for source in sources:
            adjacency.setdefault(source, set())
            adjacency[target].add(source)
            adjacency[source].add(target)

    components: list[set[str]] = []
    seen: set[str] = set()
    for node in adjacency:
        if node in seen:
            continue
        stack = [node]
        component: set[str] = set()
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            component.add(current)
            stack.extend(sorted(adjacency[current] - seen))
        components.append(component)
    return components


def select_absorb_anchor(
    component: set[str],
    outgoing: dict[str, set[str]],
    order: dict[str, int],
) -> tuple[str, str]:
    sinks = sorted(
        [commit for commit in component if not outgoing.get(commit)],
        key=lambda commit: order.get(commit, 10**9),
    )
    if sinks:
        return sinks[0], "component sink target"
    return (
        min(component, key=lambda commit: order.get(commit, 10**9)),
        "cycle resolved to earliest responsibility anchor",
    )


def resolve_absorb_anchor_graph(
    package: dict[str, Any],
    original_commits: list[str],
) -> dict[str, Any]:
    if not package["absorb"]:
        return package

    order = {commit: index for index, commit in enumerate(original_commits)}
    outgoing: dict[str, set[str]] = {}
    originally_absorbed = {source for sources in package["absorb"].values() for source in sources}
    for target, sources in package["absorb"].items():
        for source in sources:
            outgoing.setdefault(source, set()).add(target)

    resolved_absorb: dict[str, set[str]] = {}
    resolutions: list[dict[str, Any]] = []
    for component in connected_absorb_components(package["absorb"]):
        anchor, reason = select_absorb_anchor(component, outgoing, order)
        component_sources = sorted(
            (component & originally_absorbed) - {anchor},
            key=lambda commit: order.get(commit, 10**9),
        )
        if component_sources:
            resolved_absorb.setdefault(anchor, set()).update(component_sources)
        original_edges = [
            {"source": source, "target": target}
            for target, sources in package["absorb"].items()
            for source in sources
            if source in component or target in component
        ]
        if set(component_sources) != {
            source
            for target, sources in package["absorb"].items()
            for source in sources
            if source in component or target in component
        } or len({edge["target"] for edge in original_edges}) > 1:
            resolutions.append(
                {
                    "anchor": anchor,
                    "sources": component_sources,
                    "reason": reason,
                    "original_edges": original_edges,
                }
            )

    package = dict(package)
    package["absorb"] = {
        target: sorted(sources, key=lambda commit: order.get(commit, 10**9))
        for target, sources in sorted(resolved_absorb.items(), key=lambda item: order.get(item[0], 10**9))
    }
    if resolutions:
        package["semantic_anchor_resolution"] = resolutions
    return package


def git_text(repo_path: Path, args: list[str], *, input_text: str | None = None, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        input=input_text,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result.stdout


def git_bytes(repo_path: Path, args: list[str], *, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
    return result.stdout


def commit_sequence(repo_path: Path, source_ref: str) -> list[str]:
    output = git_text(repo_path, ["rev-list", "--reverse", source_ref])
    return [line.strip() for line in output.splitlines() if line.strip()]


def commit_parent(repo_path: Path, commit: str) -> str:
    parts = git_text(repo_path, ["rev-list", "--parents", "-n", "1", commit]).strip().split()
    return parts[1] if len(parts) > 1 else EMPTY_GIT_TREE


def commit_patch(repo_path: Path, commit: str) -> bytes:
    parent = commit_parent(repo_path, commit)
    if parent == EMPTY_GIT_TREE:
        return git_bytes(repo_path, ["diff-tree", "--root", "--binary", "--full-index", "-p", commit])
    return git_bytes(repo_path, ["diff-tree", "--binary", "--full-index", "-p", parent, commit])


def treeish_path_entry(repo_path: Path, treeish: str, path: str) -> dict[str, str] | None:
    output = git_bytes(repo_path, ["ls-tree", "-z", treeish, "--", path])
    if not output:
        return None
    header = output.split(b"\t", 1)[0].decode("utf-8", errors="replace")
    fields = header.split()
    if len(fields) < 3:
        return None
    return {"mode": fields[0], "sha": fields[2]}


def changed_paths_for_commit(repo_path: Path, commit: str) -> list[tuple[str, str, str]]:
    parent = commit_parent(repo_path, commit)
    if parent == EMPTY_GIT_TREE:
        args = ["diff-tree", "--root", "--no-commit-id", "--name-status", "-r", "-M", "-z", commit]
    else:
        args = ["diff-tree", "--no-commit-id", "--name-status", "-r", "-M", "-z", parent, commit]
    raw = git_bytes(repo_path, args)
    parts = [part for part in raw.split(b"\0") if part]
    changes: list[tuple[str, str, str]] = []
    index = 0
    while index < len(parts):
        status = parts[index].decode("utf-8", errors="replace")
        index += 1
        if status.startswith(("R", "C")):
            if index + 1 >= len(parts):
                break
            old_path = parts[index].decode("utf-8", errors="replace")
            new_path = parts[index + 1].decode("utf-8", errors="replace")
            index += 2
            changes.append((status, old_path, new_path))
            continue
        if index >= len(parts):
            break
        path = parts[index].decode("utf-8", errors="replace")
        index += 1
        changes.append((status, path, path))
    return changes


def commit_path_states(repo_path: Path, commit: str) -> dict[str, dict[str, dict[str, str] | None]]:
    parent = commit_parent(repo_path, commit)
    parent_treeish = parent if parent != EMPTY_GIT_TREE else EMPTY_GIT_TREE
    pre: dict[str, dict[str, str] | None] = {}
    post: dict[str, dict[str, str] | None] = {}
    for status, old_path, new_path in changed_paths_for_commit(repo_path, commit):
        if status.startswith("R"):
            pre[old_path] = treeish_path_entry(repo_path, parent_treeish, old_path)
            post[old_path] = None
            pre[new_path] = treeish_path_entry(repo_path, parent_treeish, new_path)
            post[new_path] = treeish_path_entry(repo_path, commit, new_path)
        elif status.startswith("C"):
            pre[new_path] = treeish_path_entry(repo_path, parent_treeish, new_path)
            post[new_path] = treeish_path_entry(repo_path, commit, new_path)
        else:
            pre[old_path] = treeish_path_entry(repo_path, parent_treeish, old_path)
            post[old_path] = treeish_path_entry(repo_path, commit, old_path)
    return {"pre": pre, "post": post}


def absorb_tree_adjustments(
    repo_path: Path,
    package: dict[str, Any],
    original_commits: list[str],
) -> dict[str, list[dict[str, Any]]]:
    order = {commit: index for index, commit in enumerate(original_commits)}
    adjustments: dict[str, list[dict[str, Any]]] = {commit: [] for commit in original_commits}
    state_cache: dict[str, dict[str, dict[str, dict[str, str] | None]]] = {}
    for target, sources in package["absorb"].items():
        target_index = order[target]
        for source in sources:
            source_index = order[source]
            state_cache.setdefault(source, commit_path_states(repo_path, source))
            if target_index < source_index:
                affected_range = range(target_index, source_index)
                state_name = "post"
            elif source_index < target_index:
                affected_range = range(source_index + 1, target_index)
                state_name = "pre"
            else:
                continue
            for index in affected_range:
                commit = original_commits[index]
                adjustments[commit].append(
                    {
                        "source": source,
                        "target": target,
                        "state": state_name,
                        "entries": state_cache[source][state_name],
                    }
                )
    return adjustments


def write_adjusted_tree(
    repo_path: Path,
    base_commit: str,
    adjustments: list[dict[str, Any]],
) -> str:
    with tempfile.NamedTemporaryFile(dir=repo_path, delete=False) as handle:
        index_path = Path(handle.name)
    env = os.environ.copy()
    env["GIT_INDEX_FILE"] = str(index_path)
    try:
        git_text(repo_path, ["read-tree", f"{base_commit}^{{tree}}"], env=env)
        for adjustment in adjustments:
            for path, entry in adjustment["entries"].items():
                if entry is None:
                    git_text(repo_path, ["update-index", "--force-remove", "--", path], env=env)
                else:
                    git_text(
                        repo_path,
                        ["update-index", "--add", "--cacheinfo", entry["mode"], entry["sha"], path],
                        env=env,
                    )
        return git_text(repo_path, ["write-tree"], env=env).strip()
    finally:
        index_path.unlink(missing_ok=True)


def apply_patch_direct(repo_path: Path, patch: bytes) -> None:
    args = ["apply", "--index", "--binary", "--whitespace=nowarn"]
    git_bytes(repo_path, [args[0], "--check", *args[1:]], input_bytes=patch)
    git_bytes(repo_path, args, input_bytes=patch)


def apply_patch_git_3way(repo_path: Path, patch: bytes) -> None:
    git_bytes(repo_path, ["apply", "--3way", "--index", "--binary", "--whitespace=nowarn"], input_bytes=patch)


def apply_commit_patch(repo_path: Path, commit: str, apply_mode: str) -> str:
    patch = commit_patch(repo_path, commit)
    if not patch.strip():
        return "empty"
    if apply_mode == "direct":
        apply_patch_direct(repo_path, patch)
        return "direct"
    if apply_mode == "git-3way":
        apply_patch_git_3way(repo_path, patch)
        return "git-3way"
    if apply_mode == "auto-3way":
        try:
            apply_patch_direct(repo_path, patch)
            return "direct"
        except RuntimeError as direct_error:
            try:
                apply_patch_git_3way(repo_path, patch)
            except RuntimeError as three_way_error:
                raise RuntimeError(
                    "git apply auto-3way failed. "
                    f"direct apply error: {direct_error}; git 3-way apply error: {three_way_error}"
                ) from three_way_error
            return "git-3way"
    raise ValueError("apply_mode must be direct, git-3way, or auto-3way.")


def remove_replay_paths(repo_path: Path, paths: list[str]) -> None:
    for path in paths:
        git_text(repo_path, ["rm", "-f", "--ignore-unmatch", "--", path])


def staged_changes_exist(repo_path: Path) -> bool:
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_path, check=False)
    return result.returncode != 0


def replay_commit_metadata(repo_path: Path, commit: str) -> dict[str, str]:
    raw = git_text(repo_path, ["show", "-s", "--format=%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI%x00%B", commit])
    parts = raw.split("\x00", 6)
    return {
        "author_name": parts[0],
        "author_email": parts[1],
        "author_date": parts[2],
        "committer_name": parts[3],
        "committer_email": parts[4],
        "committer_date": parts[5],
        "message": parts[6].rstrip() + "\n",
    }


def write_replayed_commit(
    repo_path: Path,
    commit: str,
    message_overrides: dict[str, str],
    *,
    allow_empty: bool = False,
) -> str | None:
    if not staged_changes_exist(repo_path) and not allow_empty:
        return None
    metadata = replay_commit_metadata(repo_path, commit)
    message = message_overrides.get(commit, metadata["message"]).rstrip() + "\n"
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": metadata["author_name"],
            "GIT_AUTHOR_EMAIL": metadata["author_email"],
            "GIT_AUTHOR_DATE": metadata["author_date"],
            "GIT_COMMITTER_NAME": metadata["committer_name"],
            "GIT_COMMITTER_EMAIL": metadata["committer_email"],
            "GIT_COMMITTER_DATE": metadata["committer_date"],
        }
    )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=repo_path, delete=False) as handle:
        handle.write(message)
        message_path = Path(handle.name)
    try:
        command = ["commit", "-F", str(message_path)]
        if allow_empty:
            command.append("--allow-empty")
        git_text(repo_path, command, env=env)
    finally:
        message_path.unlink(missing_ok=True)
    return git_text(repo_path, ["rev-parse", "HEAD"]).strip()


def write_replayed_tree_commit(
    repo_path: Path,
    commit: str,
    tree: str,
    parent_commit: str,
    message_overrides: dict[str, str],
) -> str:
    metadata = replay_commit_metadata(repo_path, commit)
    message = message_overrides.get(commit, metadata["message"]).rstrip() + "\n"
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": metadata["author_name"],
            "GIT_AUTHOR_EMAIL": metadata["author_email"],
            "GIT_AUTHOR_DATE": metadata["author_date"],
            "GIT_COMMITTER_NAME": metadata["committer_name"],
            "GIT_COMMITTER_EMAIL": metadata["committer_email"],
            "GIT_COMMITTER_DATE": metadata["committer_date"],
        }
    )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=repo_path, delete=False) as handle:
        handle.write(message)
        message_path = Path(handle.name)
    try:
        command = ["commit-tree", tree]
        if parent_commit:
            command.extend(["-p", parent_commit])
        command.extend(["-F", str(message_path)])
        return git_text(repo_path, command, env=env).strip()
    finally:
        message_path.unlink(missing_ok=True)


def run_approved_verification_command(repo_path: Path, command: str) -> dict[str, Any]:
    stripped = command.strip()
    if not stripped:
        raise ValueError("Verification command must not be empty.")
    if any(token in stripped for token in ["\n", "\r", "&&", "||", "|", ";"]):
        raise ValueError("Verification command must be a single command without shell chaining.")
    parts = parse_git_cli_command(stripped)
    result = subprocess.run(
        parts,
        cwd=repo_path,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return {
        "command": stripped,
        "returncode": result.returncode,
        "stdout": result.stdout[:4000],
        "stderr": result.stderr[:4000],
    }


def replay_worktree_path(work_dir: Path, target_branch: str) -> Path:
    return git_worktree_dir_for_work_dir(work_dir) / safe_branch_segment(target_branch)


def prepare_replay_worktree(
    repo_root: Path,
    work_dir: Path,
    package: dict[str, Any],
    *,
    reuse_worktree: bool,
) -> Path:
    worktree_root = git_worktree_dir_for_work_dir(work_dir)
    worktree_path = ensure_child_path(worktree_root, replay_worktree_path(work_dir, package["target_branch"]), "replay worktree")
    if worktree_path.exists() and not reuse_worktree:
        raise FileExistsError(f"Replay worktree already exists: {worktree_path}")
    if worktree_path.exists():
        git_text(repo_root, ["worktree", "remove", "--force", str(worktree_path)])
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    git_text(repo_root, ["worktree", "add", "--detach", str(worktree_path), package["source_ref"]])
    git_text(worktree_path, ["config", "core.autocrlf", "false"])
    return worktree_path


def build_rebase_replay_report(
    *,
    package: dict[str, Any],
    package_path: Path,
    worktree_path: Path,
    mapping_path: Path,
    remote_before: str,
    remote_after: str,
    before_count: int,
    after_count: int,
    tree_equal: bool,
    pushed: bool,
    apply_results: list[dict[str, str]],
    verification_results: list[dict[str, Any]],
) -> str:
    apply_lines = [
        f"- `{item['commit']}` `{item['role']}` -> `{item['mode']}`" for item in apply_results
    ] or ["- none"]
    verification_lines = [
        f"- `{item['command']}` -> `{item['returncode']}`" for item in verification_results
    ] or ["- none"]
    anchor_resolution_lines = [
        f"- Anchor `{item['anchor']}` absorbs {len(item.get('sources', []))} commit(s): {item.get('reason', '')}"
        for item in package.get("semantic_anchor_resolution", [])
    ] or ["- none"]
    return "\n".join(
        [
            "# Git history rebase replay execution",
            "",
            "## Target",
            "",
            f"- Branch: `{package['target_branch']}`",
            f"- Source ref: `{package['source_ref']}`",
            f"- Apply mode: `{package['apply_mode']}`",
            f"- Replay strategy: `{package.get('replay_strategy', 'tree-preserving')}`",
            f"- Package: `{package_path}`",
            f"- Worktree: `{worktree_path}`",
            f"- SHA map: `{mapping_path}`",
            f"- Remote before: `{remote_before}`",
            f"- Remote after: `{remote_after}`",
            f"- Pushed: `{str(pushed).lower()}`",
            "",
            "## Result",
            "",
            f"- Before commit count: `{before_count}`",
            f"- After commit count: `{after_count}`",
            f"- Final tree equals source ref: `{str(tree_equal).lower()}`",
            "",
            "## Patch apply",
            "",
            *apply_lines,
            "",
            "## Semantic Anchor Resolution",
            "",
            *anchor_resolution_lines,
            "",
            "## Verification",
            "",
            *verification_lines,
            "",
            "## Runtime rule",
            "",
            f"The rewrite was executed by the built-in non-interactive replay runtime. No generated Python helper script under `{context_path_pattern()}` is required.",
        ]
    )


def execute_rebase_replay_package(
    repo_root: Path,
    work_dir: Path,
    package: dict[str, Any],
    package_path: Path,
    *,
    push: bool,
    remote_override: str,
    reuse_worktree: bool,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        worktree_path = replay_worktree_path(work_dir, package["target_branch"])
        return {
            "dry_run": True,
            "worktree_path": relative_to_repo(repo_root, worktree_path),
            "package_path": relative_to_repo(repo_root, package_path),
            "apply_mode": package["apply_mode"],
            "push_planned": bool(push),
        }

    remote = remote_override or package["remote"]
    remote_before = ""
    if push:
        output = git_text(repo_root, ["ls-remote", "--heads", remote, package["target_branch"]])
        remote_before = output.split()[0] if output.strip() else ""
        if remote_before != package["expected_remote_sha"]:
            raise RuntimeError(
                f"Remote {package['target_branch']} moved: expected {package['expected_remote_sha']}, got {remote_before}"
            )

    worktree_path = prepare_replay_worktree(repo_root, work_dir, package, reuse_worktree=reuse_worktree)
    original_commits = commit_sequence(worktree_path, package["source_ref"])
    package = resolve_absorb_anchor_graph(package, original_commits)
    validate_rebase_replay_actions(package, original_commits)
    source_tip = git_text(worktree_path, ["rev-parse", package["source_ref"]]).strip()
    build_branch = f"github-knowledge-replay/{safe_branch_segment(work_dir.name)}/{safe_branch_segment(package['target_branch'])}"

    absorbed_sources = {source for sources in package["absorb"].values() for source in sources}
    skipped_commits = absorbed_sources | package["drop"]
    adjustments_by_commit = absorb_tree_adjustments(worktree_path, package, original_commits)
    mapping: list[tuple[str, str]] = []
    apply_results: list[dict[str, str]] = []
    new_parent = ""
    for index, commit in enumerate(original_commits):
        if commit in skipped_commits:
            mapping.append((commit, "DROPPED"))
            continue
        adjustments = list(adjustments_by_commit.get(commit, []))
        remove_paths = package["remove_after_apply"].get(commit, [])
        if remove_paths:
            adjustments.append(
                {
                    "source": commit,
                    "target": commit,
                    "state": "remove-after-apply",
                    "entries": {path: None for path in remove_paths},
                }
            )
        tree = write_adjusted_tree(worktree_path, commit, adjustments)
        new_commit = write_replayed_tree_commit(
            worktree_path,
            commit,
            tree,
            new_parent,
            package["message_overrides"],
        )
        new_parent = new_commit
        apply_results.append(
            {
                "commit": commit,
                "role": "base",
                "mode": "tree-replay",
            }
        )
        for adjustment in adjustments:
            apply_results.append(
                {
                    "commit": adjustment["source"],
                    "role": f"absorb-{adjustment['state']}-state-into:{adjustment['target']}",
                    "mode": "tree-overlay",
                }
            )
        mapping.append((commit, new_commit))
    dropped_commits = {before for before, after in mapping if after == "DROPPED"}
    missing_drops = sorted(skipped_commits - dropped_commits)
    if missing_drops:
        raise RuntimeError("Replay did not drop all approved source commits: " + ", ".join(missing_drops))

    if not new_parent:
        raise RuntimeError("Replay produced no commits.")
    new_tip = new_parent
    subprocess.run(["git", "branch", "-D", build_branch], cwd=worktree_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    git_text(worktree_path, ["update-ref", f"refs/heads/{build_branch}", new_tip])
    git_text(worktree_path, ["switch", "--force", build_branch])
    git_text(worktree_path, ["reset", "--hard", new_tip])
    before_count = len(original_commits)
    after_count = int(git_text(worktree_path, ["rev-list", "--count", "HEAD"]).strip())
    tree_equal = subprocess.run(["git", "diff", "--quiet", f"{package['source_ref']}..HEAD"], cwd=worktree_path).returncode == 0
    if not tree_equal:
        raise RuntimeError("Replay result tree does not match source ref.")

    output_branch = package["output_branch"] or build_branch
    if output_branch != build_branch:
        subprocess.run(["git", "branch", "-D", output_branch], cwd=worktree_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        git_text(worktree_path, ["branch", "-m", output_branch])

    timestamp = local_timestamp()
    mapping_path = context_file(work_dir, f"github-history-rebase-replay-sha-map-{timestamp}.tsv")
    mapping_path.write_text(
        "before\tafter\n" + "\n".join(f"{before}\t{after}" for before, after in mapping) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    verification_results = [
        run_approved_verification_command(worktree_path, command)
        for command in package["verification_commands"]
    ]
    failed_verification = [item for item in verification_results if item["returncode"] != 0]
    if failed_verification:
        raise RuntimeError("Replay verification failed: " + failed_verification[0]["command"])

    pushed = False
    remote_after = remote_before
    push_result: dict[str, Any] | None = None
    if push:
        push_command = [
            "push",
            f"--force-with-lease={package['target_branch']}:{package['expected_remote_sha']}",
            remote,
            f"{new_tip}:refs/heads/{package['target_branch']}",
        ]
        push_output = git_text(worktree_path, push_command)
        pushed = True
        remote_after = git_text(repo_root, ["ls-remote", "--heads", remote, package["target_branch"]]).split()[0]
        push_result = {"command": "git " + " ".join(push_command), "stdout": push_output, "remote_after": remote_after}

    report_path = process_report_dir_for_work_dir(work_dir) / f"github-history-rebase-replay-execution-{timestamp}.md"
    write_markdown(
        report_path,
        build_rebase_replay_report(
            package=package,
            package_path=package_path,
            worktree_path=worktree_path,
            mapping_path=mapping_path,
            remote_before=remote_before,
            remote_after=remote_after,
            before_count=before_count,
            after_count=after_count,
            tree_equal=tree_equal,
            pushed=pushed,
            apply_results=apply_results,
            verification_results=verification_results,
        ),
    )
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-HISTORY-REBASE-REPLAY-EXECUTION",
        "GitHub History Rebase Replay Execution",
        report_path,
        "report",
    )
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-HISTORY-REBASE-REPLAY-SHA-MAP",
        "GitHub History Rebase Replay SHA Map",
        mapping_path,
        "other",
    )
    return {
        "dry_run": False,
        "source_tip": source_tip,
        "new_tip": new_tip,
        "before_count": before_count,
        "after_count": after_count,
        "tree_equal": tree_equal,
        "pushed": pushed,
        "remote_before": remote_before,
        "remote_after": remote_after,
        "worktree_path": relative_to_repo(repo_root, worktree_path),
        "report_path": relative_to_repo(repo_root, report_path),
        "mapping_path": relative_to_repo(repo_root, mapping_path),
        "apply_mode": package["apply_mode"],
        "apply_results": apply_results,
        "verification_results": verification_results,
        "push_result": push_result,
    }


def create_rebase_replay_apply(args: argparse.Namespace) -> dict[str, Any]:
    if args.human_check != "approved":
        raise PermissionError("rebase-replay-apply requires --human-check approved.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    require_github_operation_gate(repo_root, work_dir, require_mutation_gate=True)
    package_path, raw_package = load_rebase_replay_package(work_dir, args.package_path)
    package = normalize_rebase_replay_package(raw_package, None if args.dry_run else repo_root)
    if getattr(args, "apply_mode", ""):
        package["apply_mode"] = args.apply_mode
    validate_rebase_replay_package(package, analysis, push=bool(args.push))
    result = execute_rebase_replay_package(
        repo_root,
        work_dir,
        package,
        package_path,
        push=bool(args.push),
        remote_override=str(args.remote or ""),
        reuse_worktree=bool(args.reuse_worktree),
        dry_run=bool(args.dry_run),
    )
    result["target_branch"] = package["target_branch"]
    result["remote"] = str(args.remote or "") or package["remote"]
    result["expected_remote_sha"] = package["expected_remote_sha"]
    result["candidate_ids"] = package["candidate_ids"]
    if not args.dry_run:
        for candidate_id in package["candidate_ids"]:
            candidate = maybe_find_history_rewrite_candidate(analysis, candidate_id)
            if candidate is None:
                candidate = find_message_repair_candidate(analysis, candidate_id)
            candidate["execution_status"] = "pushed" if result["pushed"] else "verified"
            candidate["executed_at"] = utc_now_iso()
            candidate["replay_package_ref"] = relative_to_repo(repo_root, package_path)
            candidate["before_after_sha_mapping"] = [result["mapping_path"]]
            candidate["execution_result"] = {
                "runtime": "built-in-rebase-replay",
                "report_path": result["report_path"],
                "mapping_path": result["mapping_path"],
                "worktree_path": result["worktree_path"],
                "apply_mode": result["apply_mode"],
                "new_tip": result["new_tip"],
                "pushed": result["pushed"],
            }
        analysis.setdefault("rebase_replay_executions", []).append(result)
        write_json(analysis_path, analysis)
    result["analysis_path"] = relative_to_repo(repo_root, analysis_path)
    result["package_path"] = relative_to_repo(repo_root, package_path)
    result["gate_restart"] = github_knowledge_gate_restart(
        "github-knowledge-rebase-replay-gate",
        status="dry-run" if args.dry_run else "verified",
        restart_reason="normal-rebase-replay-gate",
    )
    return result


def verified_replay_executions(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        execution
        for execution in analysis.get("rebase_replay_executions", []) or []
        if isinstance(execution, dict)
        and not execution.get("dry_run")
        and bool(execution.get("tree_equal"))
        and not bool(execution.get("pushed"))
        and str(execution.get("new_tip", "")).strip()
    ]


def select_verified_replay_execution(
    analysis: dict[str, Any],
    *,
    execution_index: int,
    new_tip: str,
) -> dict[str, Any]:
    executions = verified_replay_executions(analysis)
    if new_tip:
        matches = [item for item in executions if str(item.get("new_tip", "")).strip() == new_tip]
        if not matches:
            raise ValueError(f"No verified unpublished replay execution found for new tip: {new_tip}")
        return matches[-1]
    if not executions:
        raise ValueError("No verified unpublished replay execution is available.")
    try:
        return executions[execution_index]
    except IndexError as exc:
        raise IndexError(f"Verified replay execution index is out of range: {execution_index}") from exc


def candidate_matches_execution_tip(candidate: dict[str, Any], new_tip: str) -> bool:
    execution_result = candidate.get("execution_result", {})
    return isinstance(execution_result, dict) and str(execution_result.get("new_tip", "")).strip() == new_tip


def build_publish_verified_replay_report(
    *,
    target_branch: str,
    remote: str,
    expected_remote_sha: str,
    new_tip: str,
    source_tip: str,
    remote_before: str,
    remote_after: str,
    push_command: list[str],
    pushed: bool,
    dry_run: bool,
) -> str:
    return "\n".join(
        [
            "# Git history verified replay publication",
            "",
            "## Target",
            "",
            f"- Branch: `{target_branch}`",
            f"- Remote: `{remote}`",
            f"- Expected remote SHA: `{expected_remote_sha}`",
            f"- Source tip: `{source_tip}`",
            f"- New tip: `{new_tip}`",
            f"- Remote before: `{remote_before}`",
            f"- Remote after: `{remote_after}`",
            f"- Pushed: `{str(pushed).lower()}`",
            f"- Dry run: `{str(dry_run).lower()}`",
            "",
            "## Command",
            "",
            f"- `git {' '.join(push_command)}`",
            "",
            "## Verification",
            "",
            "- The selected replay execution was already verified with `tree_equal: true`.",
            "- This command does not regenerate replay commits or packages.",
            "- Remote reflection is guarded by `force-with-lease` and the expected remote SHA.",
        ]
    )


def create_publish_verified_replay(args: argparse.Namespace) -> dict[str, Any]:
    if args.human_check != "approved":
        raise PermissionError("publish-verified-replay requires --human-check approved.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    require_github_operation_gate(repo_root, work_dir, require_mutation_gate=True)
    target_branch = str(args.target_branch or analysis.get("target_branch", "")).strip()
    if not target_branch:
        raise ValueError("publish-verified-replay requires --target-branch or analysis.target_branch.")
    expected_remote_sha = str(args.expected_remote_sha or "").strip()
    if not expected_remote_sha:
        raise ValueError("publish-verified-replay requires --expected-remote-sha.")
    remote = str(args.remote or "origin").strip() or "origin"
    requested_new_tip = str(args.new_tip or "").strip()
    execution = select_verified_replay_execution(
        analysis,
        execution_index=int(args.execution_index),
        new_tip=requested_new_tip,
    )
    new_tip = str(execution.get("new_tip", "")).strip()
    source_tip = str(execution.get("source_tip", "")).strip()
    git_text(repo_root, ["rev-parse", "--verify", f"{new_tip}^{{commit}}"])
    if source_tip:
        git_text(repo_root, ["rev-parse", "--verify", f"{source_tip}^{{commit}}"])
        if subprocess.run(["git", "diff", "--quiet", f"{source_tip}..{new_tip}"], cwd=repo_root).returncode != 0:
            raise RuntimeError("Verified replay tip no longer matches the source tree.")
    remote_output = git_text(repo_root, ["ls-remote", "--heads", remote, target_branch])
    remote_before = remote_output.split()[0] if remote_output.strip() else ""
    if remote_before != expected_remote_sha:
        raise RuntimeError(f"Remote {target_branch} moved: expected {expected_remote_sha}, got {remote_before}")
    push_command = [
        "push",
        f"--force-with-lease={target_branch}:{expected_remote_sha}",
        remote,
        f"{new_tip}:refs/heads/{target_branch}",
    ]
    if args.dry_run:
        remote_after = remote_before
        pushed = False
    else:
        push_output = git_text(repo_root, push_command)
        remote_after = git_text(repo_root, ["ls-remote", "--heads", remote, target_branch]).split()[0]
        if remote_after != new_tip:
            raise RuntimeError(f"Remote {target_branch} did not move to verified replay tip: {remote_after}")
        pushed = True
        execution["pushed"] = True
        execution["remote_before"] = remote_before
        execution["remote_after"] = remote_after
        execution["push_result"] = {
            "command": "git " + " ".join(push_command),
            "stdout": push_output,
            "remote_after": remote_after,
        }
        for candidate in (analysis.get("history_rewrite_candidates", []) or []):
            if candidate_matches_execution_tip(candidate, new_tip):
                candidate["execution_status"] = "pushed"
                candidate.setdefault("execution_result", {})["pushed"] = True
                candidate["execution_result"]["remote_after"] = remote_after
        for candidate in (analysis.get("message_repair_candidates", []) or []):
            if candidate_matches_execution_tip(candidate, new_tip):
                candidate["execution_status"] = "pushed"
                candidate.setdefault("execution_result", {})["pushed"] = True
                candidate["execution_result"]["remote_after"] = remote_after
    timestamp = local_timestamp()
    report_path = process_report_dir_for_work_dir(work_dir) / f"github-history-verified-replay-publish-{timestamp}.md"
    write_markdown(
        report_path,
        build_publish_verified_replay_report(
            target_branch=target_branch,
            remote=remote,
            expected_remote_sha=expected_remote_sha,
            new_tip=new_tip,
            source_tip=source_tip,
            remote_before=remote_before,
            remote_after=remote_after,
            push_command=push_command,
            pushed=pushed,
            dry_run=bool(args.dry_run),
        ),
    )
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-HISTORY-VERIFIED-REPLAY-PUBLISH",
        "GitHub History Verified Replay Publication",
        report_path,
        "report",
    )
    result = {
        "dry_run": bool(args.dry_run),
        "pushed": pushed,
        "target_branch": target_branch,
        "remote": remote,
        "expected_remote_sha": expected_remote_sha,
        "new_tip": new_tip,
        "source_tip": source_tip,
        "remote_before": remote_before,
        "remote_after": remote_after,
        "push_result": None if args.dry_run else execution.get("push_result"),
        "report_path": relative_to_repo(repo_root, report_path),
    }
    if not args.dry_run:
        analysis.setdefault("rebase_replay_publications", []).append(
            {
                "published_at": utc_now_iso(),
                "target_branch": target_branch,
                "remote": remote,
                "expected_remote_sha": expected_remote_sha,
                "new_tip": new_tip,
                "remote_before": remote_before,
                "remote_after": remote_after,
                "report_path": result["report_path"],
            }
        )
        write_json(analysis_path, analysis)
    result["analysis_path"] = relative_to_repo(repo_root, analysis_path)
    result["gate_restart"] = github_knowledge_gate_restart(
        "github-knowledge-verified-replay-publish-gate",
        status="dry-run" if args.dry_run else "pushed",
        restart_reason="normal-verified-replay-publish-gate",
    )
    return result


def require_github_operation_gate(
    repo_root: Path,
    work_dir: Path,
    *,
    require_mutation_gate: bool = False,
    require_rag_gate: bool = False,
) -> dict[str, Any]:
    manifest_path = manifest_path_for_work_dir(work_dir)
    manifest = load_manifest(work_dir)
    gate_entry = context_entry(manifest, "github-operation-gate")
    tool_entry = context_entry(manifest, "tool-selection")
    missing = []
    if gate_entry is None:
        missing.append("github-operation-gate")
    if require_mutation_gate and tool_entry is None:
        missing.append("tool-selection")
    if missing:
        raise RuntimeError(
            "Context First gate: github-knowledge-maintenance requires "
            + ", ".join(missing)
            + f" before this operation. Re-run init or repair the manifest: {manifest_path}"
        )

    gate_path = context_path(repo_root, gate_entry) if gate_entry else context_file(work_dir, "github-operation-gate.json")
    gate = read_json(gate_path, default={}) or {}
    tool_path = context_path(repo_root, tool_entry) if tool_entry else context_file(work_dir, "tool-selection.json")
    tool_selection = read_json(tool_path, default={}) or {}
    reasons = []
    if require_mutation_gate and not bool(gate.get("mutation_allowed")):
        reasons.append("github-operation-gate does not allow mutation.")
    if require_mutation_gate and not bool(tool_selection.get("human_check_required")):
        reasons.append("tool-selection must mark GitHub mutation as Human Check required.")
    if require_rag_gate and not bool(gate.get("human_check_required")):
        reasons.append("github-operation-gate must require Human Check for RAG publication.")
    if reasons:
        raise RuntimeError("Context First gate: " + " ".join(reasons))

    return {
        "status": "ready",
        "manifest_path": relative_to_repo(repo_root, manifest_path),
        "github_operation_gate": relative_to_repo(repo_root, gate_path),
        "tool_selection": relative_to_repo(repo_root, tool_path) if tool_entry else "",
        "require_mutation_gate": require_mutation_gate,
        "require_rag_gate": require_rag_gate,
        "gate_restart": github_knowledge_gate_restart(
            "github-knowledge-operation-gate",
            status="ready",
            restart_reason="normal-github-knowledge-operation-gate",
        ),
    }


def build_repair_plan(analysis: dict[str, Any]) -> str:
    proposals = analysis.get("repair_proposals", []) or []
    gaps = analysis.get("narrative_gaps", []) or []
    rewrite_candidates = history_rewrite_candidates(analysis)
    return "\n".join(
        [
            "# GitHub ナレッジ修復計画",
            "",
            "## 意図",
            "",
            analysis.get("summary", "Maintain GitHub repository knowledge assets."),
            "",
            "## ワークフロー段階",
            "",
            "1. `detect-rebase-candidates` が1-3ファイルのcommit漏れ候補を検出し、`pending` 候補として記録する。",
            "2. `rebase-plan` が実行計画を計算し、Human Review用レポートを作成する。",
            "3. 1つのHuman Check approval packageで対象候補、方針、rollback、verification、remote updateをまとめて承認または却下する。",
            "4. `rebase-apply --human-check approved` は承認済みパッケージを消費するCLI実行ガードであり、追加の承認依頼ではない。",
            "",
            "## リポジトリ",
            "",
            f"- リポジトリ: `{analysis.get('repository', '')}`",
            f"- 対象 branch: `{analysis.get('target_branch', '')}`",
            f"- 修復 mode: `{analysis.get('repair_mode', 'proposal')}`",
            "",
            "## ガードレール",
            "",
            markdown_list(analysis.get("guardrails", []) or []),
            "",
            "## ナラティブ不足",
            "",
            field_list(gaps, ["asset_ref", "gap_type", "severity", "evidence", "why_it_matters"]),
            "",
            "## 修復提案",
            "",
            field_list(proposals, ["target", "proposal_type", "reason", "before_summary", "after_summary", "draft_body", "approval_required"]),
            "",
            "## Semantic Commit / PR Title チェック",
            "",
            "commit message/body 補修では、GitHub の commit list に表示される subject を body と別に確認します。",
            "PR title 補修では、GitHub の PR list に表示される title を body と別に確認します。",
            "",
            "良い形式:",
            "",
            "```text",
            "type(scope): 変更の責務または成果",
            "```",
            "",
            "避ける subject:",
            "",
            "- repository 名だけを scope にした subject",
            "- PR title が `Develop` や branch 名だけで終わる title",
            "- file 名だけの subject",
            "- `対応`、`修正`、`更新` だけで終わる subject",
            "- body を読まないと何が変わったか分からない subject/title",
            "",
            "Human Review では、subject/title が GitHub list view だけで意味を持つか確認します。",
            "",
            "## 1-3 file commit漏れ / Rebase候補",
            "",
            field_list(
                rewrite_candidates,
                [
                    "file_paths",
                    "suspect_commits",
                    "expected_commit",
                    "repair_goal",
                    "independent_responsibility",
                    "evidence_refs",
                    "recommended_action",
                    "reason",
                    "completion_criteria",
                    "approval_status",
                    "before_after_sha_mapping",
                    "rollback_plan",
                ],
            ),
            "",
            "このsectionは提案のみです。`git rebase`、`git commit --amend`、force pushは実行しません。",
            "対象fileは1-3件に限定し、source差分の意味が1つのcommit責務に自然に収まる場合だけ候補化します。",
            "無駄なcommitに後付けIssueやmessageを付けるだけのrepairは完了扱いにしません。吸収、分割、drop、または独立責務の根拠付き維持を明示します。",
            "",
            "## Human Review チェックリスト",
            "",
            "- 各修復理由を確認する。",
            "- 対象の Issue、PR、comment、CAR、README、docs、ADR を確認する。",
            "- 修正前後の要約を確認する。",
            "- commit message/body 補修では semantic subject が `type(scope): responsibility/result` になっていることを確認する。",
            "- semantic subject が GitHub commit list だけで意味を持つことを確認する。",
            "- PR title 補修では current title、proposed title、exact `gh pr edit --title` command を確認する。",
            "- PR title が GitHub PR list だけで意味を持つことを確認する。",
            "- commit source や対象 repository の source file を変更しないことを確認する。",
            "- 既存 commit message/body を直接修正する場合は、明示承認、before/after SHA mapping、rollback plan を確認する。",
            "- 1-3ファイルのcommit漏れrebase整備では、対象file一覧、suspect commit、本来まとめるcommit、before/after SHA mapping、rollback plan、verification commandを確認する。",
            "- rewrite 後は `git log --format=\"%H %s\"` または GitHub API で subject 表示を確認する。",
            "- 実行前に正確な Git / GitHub CLI/API command を確認する。",
        ]
    )


def create_repair_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    output_path = (
        Path(args.output).resolve()
        if args.output
        else process_report_dir_for_work_dir(work_dir) / f"github-knowledge-repair-plan-{local_timestamp()}.md"
    )
    write_markdown(output_path, build_repair_plan(analysis))
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-REPAIR-PLAN", "GitHub Knowledge Repair Plan", output_path, "report")
    return {
        "repair_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "proposal_count": len(analysis.get("repair_proposals", []) or []),
    }


def build_rebase_plan(analysis: dict[str, Any]) -> str:
    candidates = history_rewrite_candidates(analysis)
    validation_errors = validate_history_rewrite_candidates(candidates)
    approval_records = analysis.get("human_approval_records", []) or []
    open_questions = analysis.get("open_questions", []) or []
    boundary = github_git_responsibility_boundary()
    return "\n".join(
        [
            "# Git Commit 履歴 Rebase レビュー計画",
            "",
            "## ワークフロー段階",
            "",
            "1. `detect-rebase-candidates` が1-3ファイルのcommit漏れ候補を検出し、`pending` 候補として記録する。",
            "2. `rebase-plan` が実行計画を計算し、Human Review用レポートを作成する。",
            "3. 1つのHuman Check approval packageで対象候補、方針、rollback、verification、remote updateをまとめて承認または却下する。",
            "4. `rebase-apply --human-check approved` は承認済みパッケージを消費するCLI実行ガードであり、追加の承認依頼ではない。",
            "",
            "この計画書は、1-3ファイルの不自然なコミット履歴やコミット漏れをrebaseで整えるためのHuman Review資料です。",
            "このworkflow helperはGit操作を実行しません。",
            "",
            "## GitHub API / Git CLI 責務境界",
            "",
            "- GitHub API / gh: Issue、PR、comment、label、release、remote branch ref確認など、GitHub上のmetadataとcollaboration stateを扱う。",
            "- Git CLI local: commit graph作成、rebase相当の履歴rewrite、before/after SHA mapping、tree diff検証を扱う。local-only操作なので認証は不要。",
            "- Git CLI remote: fetch、ls-remote、push、force-with-leaseで検証済みlocal graphをGitHub branchへ反映する。remote操作なので認証が必要。",
            "- GitHub APIではcommit graph rewriteやrebaseはできない。GitHub tokenの有無とlocal rebase editorの要否は別問題として扱う。",
            "- runtime自動化では `git rebase -i` のeditor hookに依存しない。非対話のGit CLI local commandで履歴を作り、local verification後にGit CLI remote commandで承認済みbranchへ反映する。",
            f"- Approved small-commit packages should be generated with `aiwfctl github-knowledge rebase-package` and executed with `aiwfctl github-knowledge rebase-apply`; use JSON data under `{context_path_pattern()}`, not generated Python helper scripts.",
            f"- Replay verification worktrees must live under `{git_worktree_path_pattern()}/`; the main checkout is only for reports and context artifacts.",
            f"- 承認回数: {boundary['approval_model']['human_check_count']} approval package。対象repository、対象branch、rewrite action、local verification、rollback、exact remote update commandを1つの承認単位にまとめる。",
            "- 運用ルール: approval packageが承認済みなら、後続のlocal rewrite、verification、approved remote updateで人間への再承認依頼を出さない。CLIの `--human-check approved` は承認済み事実をruntimeへ渡す実行ガードとして扱う。",
            "",
            "## リポジトリ",
            "",
            f"- リポジトリ: `{analysis.get('repository', '')}`",
            f"- 対象branch: `{analysis.get('target_branch', '')}`",
            f"- 修復mode: `{analysis.get('repair_mode', 'proposal')}`",
            "",
            "## レビュー凡例",
            "",
            "| フィールド / 値 | Human Review上の意味 | GitHub sync gate |",
            "| --- | --- | --- |",
            "| `approval_status: pending` | 未レビュー。 | 未完了。GitHub sync applyを実行しない。 |",
            "| `approval_status: approved` + `repair_goal: absorb-into-existing-commit` | rebase/amendが承認済み。 | rebase適用と検証が終わるまで未完了。 |",
            "| `approval_status: approved` + `repair_goal: split-into-independent-commit` | commit分割が承認済み。 | 分割適用と検証が終わるまで未完了。 |",
            "| `approval_status: approved` + `repair_goal: drop-empty-or-noise-commit` | 空またはノイズcommitのdropが承認済み。 | drop適用と検証が終わるまで未完了。 |",
            "| `repair_goal: manual-review-required` | subjectだけでは判断せず、commit資材の内容を見て吸収、分割、message補修、維持、却下を決める。 | 未完了。Human Reviewで具体的な方針へ変更する。 |",
            "| `repair_goal: keep-with-evidence` | 正当な独立変更として維持する。 | `independent_responsibility` と `evidence_refs` が記録された場合のみ完了。 |",
            "| `repair_goal: no-rewrite` | 履歴書き換え不要と判断する。 | 理由が記録された場合に完了。 |",
            "| `approval_status: rejected` | 候補を却下する。 | 完了。rebaseしない。 |",
            "",
            "検出された差分が正当でそのまま残すべき場合は `keep-with-evidence` を使い、`pending` のまま放置しません。",
            "`manual-review-required` は、コミット資材の内容確認が必要な状態です。吸収先未検出の自動結果を `no-rewrite` として扱いません。",
            "誤検出または意図的にrebase不要と人間が判断した場合だけ `no-rewrite` を使います。",
            "",
            "## Human Approval 記録",
            "",
            field_list(
                approval_records,
                ["approval_type", "repository", "target_branch", "scope", "approved_at", "approved_by", "limitations"],
            ),
            "",
            "## 候補別 OK / NG チェックリスト",
            "",
            "このチェックリストはHuman Review用です。候補IDを手入力せず、対象候補の `OK` または `NG` にチェックしてください。",
            "`OK` / `NG` は候補の採否を1つのapproval packageに含めるためのレビュー入力であり、候補ごとに別承認を求めるものではありません。",
            "AIは、repair_goal、rollback plan、local verification、exact remote update commandを同じapproval packageにまとめ、承認済み後は同一パッケージ内の作業で再承認を求めません。before/after SHA mapping は承認後のlocal rewrite検証で生成します。",
            "",
            rebase_review_checklist(candidates),
            "",
            "## 候補",
            "",
            field_list(
                candidates,
                [
                    "file_paths",
                    "suspect_commits",
                    "expected_commit",
                    "repair_goal",
                    "independent_responsibility",
                    "evidence_refs",
                    "recommended_action",
                    "reason",
                    "before_summary",
                    "after_summary",
                    "completion_criteria",
                    "approval_status",
                    "before_after_sha_mapping",
                    "rollback_plan",
                    "draft_commands",
                    "verification_commands",
                ],
            ),
            "",
            "## 検証",
            "",
            markdown_list(validation_errors),
            "",
            "## 未解決確認事項",
            "",
            field_list(open_questions, ["question", "reason", "blocks"]),
            "",
            "## 必須Human Approval",
            "",
            "- 対象fileが1-3件であること。",
            "- rebase対象commitと、巻き込まれるcommit範囲が明示されていること。",
            "- 変更責務が1つのsemantic commitとして自然であること。",
            "- 無駄なcommitをIssue名やmessageで飾って残すのではなく、吸収、分割、drop、または根拠付き維持のどれかを明示すること。",
            "- `keep-with-evidence` の場合は、独立した責務と既存証跡が説明できること。",
            "- approval packageにrollback plan、local verification command、exact remote update commandが含まれていること。",
            "- before/after SHA mappingはlocal rewrite後にruntimeが生成し、人間が追跡できる成果物として残すこと。",
            "- `git log --format=\"%H %s\"` などでrewrite後のsubject表示をruntimeが確認すること。",
            "- force pushが必要な場合も、同じapproval package内で対象remote/branchとコマンドを承認すること。",
            "- 一度承認されたapproval package内のlocal rewrite、verification、approved remote updateについて、人間への再承認依頼を出さないこと。",
            "",
            "## 停止ルール",
            "",
            "- `approval_status: pending` の候補は実行しない。",
            "- file_pathsが0件または4件以上の候補は、このsmall rebase整備では扱わない。",
            "- repair_goalがないapproved候補は実行しない。",
            "- 独立責務や既存証跡のないcommitを後付けIssue/messageだけで完了扱いにしない。",
            "- rollback plan、verification command、exact remote update commandがないapproved候補は実行しない。",
            "- source codeの内容変更が必要な場合は、このworkflowではなく通常のfeature/fix workflowへ戻す。",
        ]
    )


def rebase_review_checklist(candidates: list[dict[str, Any]]) -> str:
    if not candidates:
        return "- なし"

    def detail_value(candidate: dict[str, Any], key: str) -> str:
        value = candidate.get(key, "")
        if isinstance(value, list):
            return ", ".join(str(item) for item in value) if value else "なし"
        return str(value) if str(value).strip() else "なし"

    lines: list[str] = [
        "| 候補ID | OK欄 | NG欄 | 疑わしいコミット | 対象ファイル | 現在の推奨 | メモ |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        candidate_id = candidate.get("id", "HISTORY-XXX")
        commits = ", ".join(str(item) for item in candidate.get("suspect_commits", []) or [""])
        files = ", ".join(str(item) for item in candidate.get("file_paths", []) or [""])
        current_goal = candidate.get("repair_goal", "")
        lines.append(f"| {candidate_id} | [ ] OK | [ ] NG | {commits} | {files} | `{current_goal}` |  |")
    lines.extend(
        [
            "",
            "### 詳細事項",
            "",
            "この節は判断材料の確認用です。OK / NG のチェックは上の「候補別 OK / NG チェックリスト」にのみ記入してください。",
            "",
        ]
    )
    for candidate in candidates:
        candidate_id = candidate.get("id", "HISTORY-XXX")
        commits = ", ".join(str(item) for item in candidate.get("suspect_commits", []) or [""])
        files = ", ".join(str(item) for item in candidate.get("file_paths", []) or [""])
        current_goal = candidate.get("repair_goal", "")
        lines.extend(
            [
                f"### {candidate_id}",
                "",
                f"- 疑わしいコミット: {commits}",
                f"- 対象ファイル: {files}",
                f"- 想定吸収先 / 期待commit: {detail_value(candidate, 'expected_commit')}",
                f"- 現在の推奨: `{current_goal}`",
                f"- 推奨action: {detail_value(candidate, 'recommended_action')}",
                f"- 判断理由: {detail_value(candidate, 'reason')}",
                f"- 独立責務の説明: {detail_value(candidate, 'independent_responsibility')}",
                f"- 証跡refs: {detail_value(candidate, 'evidence_refs')}",
                f"- Before: {detail_value(candidate, 'before_summary')}",
                f"- After: {detail_value(candidate, 'after_summary')}",
                f"- 完了条件: {detail_value(candidate, 'completion_criteria')}",
                f"- Rollback plan: {detail_value(candidate, 'rollback_plan')}",
                f"- Verification commands: {detail_value(candidate, 'verification_commands')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def create_rebase_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    output_path = (
        Path(args.output).resolve()
        if args.output
        else process_report_dir_for_work_dir(work_dir) / f"github-history-rebase-plan-{local_timestamp()}.md"
    )
    candidates = history_rewrite_candidates(analysis)
    validation_errors = validate_history_rewrite_candidates(candidates)
    write_markdown(output_path, build_rebase_plan(analysis))
    register_artifact(
        repo_root,
        work_dir,
        "GITHUB-HISTORY-REBASE-PLAN",
        "GitHub History Rebase Review Plan",
        output_path,
        "report",
    )
    return {
        "rebase_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "candidate_count": len(candidates),
        "validation_errors": validation_errors,
    }


def build_sync_plan(analysis: dict[str, Any]) -> str:
    actions = analysis.get("github_sync_actions", []) or []
    lines = [
        "# GitHub Documentation Sync 計画",
        "",
        "この計画自体は承認ではありません。人間レビューで承認された command だけを実行します。",
        "",
        "## リポジトリ",
        "",
        f"- リポジトリ: `{analysis.get('repository', '')}`",
        f"- 対象 branch: `{analysis.get('target_branch', '')}`",
        "",
        "## GitHub 同期アクション案",
        "",
    ]
    if not actions:
        lines.append("- なし")
    for action in actions:
        lines.extend(
            [
                f"### {action.get('id', 'SYNC-XXX')}: {action.get('title', 'Untitled')}",
                "",
                f"- 対象種別: `{action.get('target_type', '')}`",
                f"- 対象 ID: `{action.get('target_id', '')}`",
                f"- 操作: `{action.get('operation', '')}`",
                f"- 承認状態: `{action.get('approval_status', 'pending')}`",
                "",
                "理由:",
                "",
                action.get("reason", ""),
                "",
                "コマンド案:",
                "",
                "```powershell",
                action.get("draft_command", "# Update github-knowledge-analysis.json with the exact gh command."),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## 停止ルール",
            "",
            "- `pending` の command は実行しない。",
            "- この GitHub documentation sync plan では commit message rewrite を実行しない。",
            "- 1-3ファイルのcommit漏れrebase整備は `rebase-plan` のHuman Review後に別途実行する。",
            "- `git rebase`、`git commit --amend`、force push は、別の commit-message rewrite review plan で明示承認された場合だけ扱う。",
            "- commit message rewrite を扱う場合は、semantic subject の GitHub commit-list 表示を別途検証する。",
            "- 対象または command がこの計画と異なる場合は、analysis JSON を更新して再レビューする。",
        ]
    )
    return "\n".join(lines)


def sync_action_checklist(actions: list[dict[str, Any]]) -> str:
    lines = [
        "| action_id | OK | NG | target_type | target_id | operation | title |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    if not actions:
        lines.append("| - | - | - | - | - | - | No GitHub sync actions |")
    for action in actions:
        lines.append(
            "| {id} | [ ] OK | [ ] NG | {target_type} | {target_id} | {operation} | {title} |".format(
                id=action.get("id", "SYNC-XXX"),
                target_type=action.get("target_type", ""),
                target_id=action.get("target_id", ""),
                operation=action.get("operation", ""),
                title=str(action.get("title", "")).replace("|", "/"),
            )
        )
    return "\n".join(lines)


def build_sync_review_plan(analysis: dict[str, Any]) -> str:
    actions = github_sync_actions(analysis)
    lines = [
        "# GitHub Sync Review Plan",
        "",
        "This plan is the single OK / NG checklist for Issue, Pull Request, and comment repair actions.",
        "It does not mutate GitHub. Approved rows are ingested by `github-sync-review-intake` before `github-sync-apply`.",
        "",
        "## Repository",
        "",
        f"- repository: `{analysis.get('repository', '')}`",
        f"- target_branch: `{analysis.get('target_branch', '')}`",
        "",
        "## Candidate OK / NG Checklist",
        "",
        sync_action_checklist(actions),
        "",
        "## Action Details",
        "",
    ]
    if not actions:
        lines.append("- No GitHub sync actions.")
    for action in actions:
        lines.extend(
            [
                f"### {action.get('id', 'SYNC-XXX')}: {action.get('title', 'Untitled')}",
                "",
                f"- target_type: `{action.get('target_type', '')}`",
                f"- target_id: `{action.get('target_id', '')}`",
                f"- operation: `{action.get('operation', '')}`",
                f"- approval_status: `{action.get('approval_status', 'pending')}`",
                "",
                "reason:",
                "",
                str(action.get("reason", "")),
                "",
                "draft command:",
                "",
                "```powershell",
                str(action.get("draft_command", "# Missing draft_command.")),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Stop Rules",
            "",
            "- Check exactly one OK or NG box per action.",
            "- OK requires a concrete single `gh` command that passes runtime validation.",
            "- NG records `approval_status: rejected` and prevents execution.",
            "- `github-sync-apply` executes only one approved action id at a time.",
        ]
    )
    return "\n".join(lines)


def github_sync_actions(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    actions = analysis.get("github_sync_actions", []) or []
    return [action for action in actions if isinstance(action, dict)]


def find_github_sync_action(analysis: dict[str, Any], action_id: str) -> dict[str, Any]:
    for action in github_sync_actions(analysis):
        if action.get("id") == action_id:
            return action
    raise ValueError(f"GitHub sync action not found: {action_id}")


def parse_github_sync_command(command: str) -> list[str]:
    stripped = command.strip()
    if not stripped:
        raise ValueError("GitHub sync action requires draft_command.")
    if any(token in stripped for token in ["\n", "\r", "&&", "||", "|", ">", "<", ";"]):
        raise ValueError("GitHub sync action command must be a single gh command without shell chaining.")
    try:
        parts = shlex.split(stripped, posix=True)
    except ValueError as exc:
        raise ValueError(f"GitHub sync action command could not be parsed: {exc}") from exc
    if not parts or parts[0] != "gh":
        raise ValueError("GitHub sync action command must start with gh.")
    return parts


def validate_github_sync_command(action: dict[str, Any], command_parts: list[str]) -> None:
    action_id = str(action.get("id", "SYNC-XXX"))
    target_type = str(action.get("target_type", ""))
    operation = str(action.get("operation", ""))
    if len(command_parts) < 3:
        raise ValueError(f"{action_id}: GitHub sync command is incomplete.")
    family = command_parts[1]
    verb = command_parts[2]
    allowed = {
        ("issue", "edit"),
        ("issue", "comment"),
        ("pr", "edit"),
        ("pr", "comment"),
    }
    if (family, verb) in allowed:
        expected_target = "issue" if family == "issue" else "pull-request"
        expected_comment_target = "issue-comment" if family == "issue" else "pr-comment"
        if target_type not in {expected_target, expected_comment_target}:
            raise ValueError(f"{action_id}: command target does not match target_type.")
        if operation != verb:
            raise ValueError(f"{action_id}: command verb does not match operation.")
        return
    if family == "api":
        endpoint = command_parts[2]
        if target_type != "api" or operation != "api":
            raise ValueError(f"{action_id}: gh api requires target_type api and operation api.")
        if not endpoint.lstrip("/").startswith("repos/"):
            raise ValueError(f"{action_id}: gh api endpoint must be scoped under repos/.")
        return
    raise ValueError(f"{action_id}: unsupported GitHub sync command.")


def run_github_sync_command(command_parts: list[str], *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"command": " ".join(command_parts), "skipped": True, "returncode": 0, "stdout": "", "stderr": ""}
    result = subprocess.run(
        command_parts,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    return {
        "command": " ".join(command_parts),
        "skipped": False,
        "returncode": result.returncode,
        "stdout": result.stdout[:4000],
        "stderr": result.stderr[:4000],
    }


def create_sync_review_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    context_gate = require_github_operation_gate(
        repo_root,
        work_dir,
        require_mutation_gate=str(analysis.get("repair_mode", "proposal")) == "apply",
    )
    output_path = (
        Path(args.output).resolve()
        if args.output
        else process_report_dir_for_work_dir(work_dir) / f"github-documentation-sync-review-plan-{local_timestamp()}.md"
    )
    write_markdown(output_path, build_sync_review_plan(analysis))
    plan_ref = relative_to_repo(repo_root, output_path)
    analysis.setdefault("github_sync_review_plans", []).append(
        {
            "path": plan_ref,
            "created_at": utc_now_iso(),
            "action_count": len(github_sync_actions(analysis)),
        }
    )
    write_json(analysis_path, analysis)
    register_artifact(repo_root, work_dir, "GITHUB-SYNC-REVIEW-PLAN", "GitHub Sync Review Plan", output_path, "report")
    return {
        "sync_review_plan": plan_ref,
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "action_count": len(github_sync_actions(analysis)),
        "context_gate": context_gate,
    }


def apply_sync_review_decision(
    *,
    action: dict[str, Any],
    decision: str,
    reviewed_at: str,
    plan_ref: str,
) -> dict[str, Any]:
    action_id = str(action.get("id", "SYNC-XXX"))
    if decision == "NG":
        action["approval_status"] = "rejected"
        action["execution_status"] = "pending"
        action["human_review_decision"] = "NG"
        action["human_reviewed_at"] = reviewed_at
        action["human_review_source"] = plan_ref
        action.setdefault("rejection_reason", "Human Review checklist marked NG.")
        return {
            "action_id": action_id,
            "decision": decision,
            "approval_status": "rejected",
        }

    command_parts = parse_github_sync_command(str(action.get("draft_command", "")))
    validate_github_sync_command(action, command_parts)
    action["approval_status"] = "approved"
    action["execution_status"] = "pending"
    action["human_review_decision"] = "OK"
    action["human_reviewed_at"] = reviewed_at
    action["human_review_source"] = plan_ref
    return {
        "action_id": action_id,
        "decision": decision,
        "approval_status": "approved",
    }


def create_sync_review_intake(args: argparse.Namespace) -> dict[str, Any]:
    if args.human_check != "approved":
        raise PermissionError("github-sync-review-intake requires --human-check approved.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    if args.plan_path:
        plan_path = Path(args.plan_path).resolve()
        ensure_child_path(process_report_dir_for_work_dir(work_dir), plan_path, "GitHub sync review plan")
    else:
        plan_path = latest_sync_review_plan(work_dir)
    decisions = parse_sync_review_checklist(plan_path)
    all_actions = github_sync_actions(analysis)
    action_ids = {str(action.get("id", "")) for action in all_actions}
    missing = sorted(action_id for action_id in action_ids if action_id and action_id not in decisions)
    unknown = sorted(action_id for action_id in decisions if action_id not in action_ids)
    if unknown:
        raise ValueError("Checklist contains unknown GitHub sync actions: " + ", ".join(unknown))
    if missing and not args.allow_partial:
        raise ValueError(
            "Checklist is incomplete. Missing decisions for: "
            + ", ".join(missing)
            + ". Use --allow-partial to intake only checked rows."
        )

    reviewed_at = utc_now_iso()
    plan_ref = relative_to_repo(repo_root, plan_path)
    updates = [
        apply_sync_review_decision(
            action=action,
            decision=decisions[str(action.get("id"))],
            reviewed_at=reviewed_at,
            plan_ref=plan_ref,
        )
        for action in all_actions
        if str(action.get("id")) in decisions
    ]
    analysis.setdefault("github_sync_review_intakes", []).append(
        {
            "plan_path": plan_ref,
            "reviewed_at": reviewed_at,
            "updates": updates,
        }
    )
    write_json(analysis_path, analysis)
    return {
        "plan_path": plan_ref,
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "updates": updates,
        "approved_count": sum(1 for update in updates if update.get("approval_status") == "approved"),
        "rejected_count": sum(1 for update in updates if update.get("approval_status") == "rejected"),
    }


def create_sync_apply(args: argparse.Namespace) -> dict[str, Any]:
    if args.human_check != "approved":
        raise PermissionError("github-sync-apply requires --human-check approved.")
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    context_gate = require_github_operation_gate(repo_root, work_dir, require_mutation_gate=True)
    unresolved_candidates = unresolved_history_rewrite_candidates(analysis)
    if unresolved_candidates:
        unresolved_ids = ", ".join(str(candidate.get("id", "HISTORY-XXX")) for candidate in unresolved_candidates)
        raise RuntimeError(
            "github-sync-apply is blocked until rebase candidates are resolved: " + unresolved_ids
        )
    unresolved_message_candidates = unresolved_message_repair_candidates(analysis)
    if unresolved_message_candidates:
        unresolved_ids = ", ".join(str(candidate.get("id", "MESSAGE-REPAIR-XXX")) for candidate in unresolved_message_candidates)
        raise RuntimeError(
            "github-sync-apply is blocked until message repair candidates are verified: " + unresolved_ids
        )
    action = find_github_sync_action(analysis, args.action_id)
    if action.get("approval_status") != "approved":
        raise PermissionError(f"{args.action_id} is not approved.")
    if action.get("human_review_decision") != "OK" or not action.get("human_review_source"):
        raise PermissionError(f"{args.action_id} must be approved through github-sync-review-intake.")
    command_parts = parse_github_sync_command(str(action.get("draft_command", "")))
    validate_github_sync_command(action, command_parts)
    result = run_github_sync_command(command_parts, dry_run=bool(args.dry_run))
    if result["returncode"] != 0:
        action["execution_status"] = "failed"
        action["executed_at"] = utc_now_iso()
        action["execution_result"] = result
        write_json(analysis_path, analysis)
        raise RuntimeError(f"github-sync-apply command failed: {result['command']}")
    action["execution_status"] = "dry-run" if args.dry_run else "applied"
    action["executed_at"] = utc_now_iso()
    action["execution_result"] = result
    write_json(analysis_path, analysis)
    return {
        "action_id": args.action_id,
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "dry_run": bool(args.dry_run),
        "executed": not bool(args.dry_run),
        "context_gate": context_gate,
        "result": result,
        "gate_restart": github_knowledge_gate_restart(
            "github-knowledge-sync-apply-gate",
            status="dry-run" if args.dry_run else "applied",
            restart_reason="normal-github-sync-apply-gate",
        ),
    }


def create_sync_plan(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    context_gate = require_github_operation_gate(
        repo_root,
        work_dir,
        require_mutation_gate=str(analysis.get("repair_mode", "proposal")) == "apply",
    )
    output_path = (
        Path(args.output).resolve()
        if args.output
        else process_report_dir_for_work_dir(work_dir) / f"github-documentation-sync-plan-{local_timestamp()}.md"
    )
    write_markdown(output_path, build_sync_plan(analysis))
    register_artifact(repo_root, work_dir, "GITHUB-DOCUMENTATION-SYNC-PLAN", "GitHub Documentation Sync Plan", output_path, "report")
    return {
        "sync_plan": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "action_count": len(analysis.get("github_sync_actions", []) or []),
        "context_gate": context_gate,
        "gate_restart": github_knowledge_gate_restart(
            "github-knowledge-sync-plan-gate",
            status="ready",
            restart_reason="normal-github-sync-plan-gate",
        ),
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
            "## 要約",
            "",
            analysis.get("summary", ""),
            "",
            "## 知識資産",
            "",
            field_list(analysis.get("knowledge_assets", []) or [], ["asset_type", "source_ref", "intent", "reuse_value"]),
            "",
            "## ナラティブ不足",
            "",
            field_list(analysis.get("narrative_gaps", []) or [], ["asset_ref", "gap_type", "severity", "why_it_matters"]),
            "",
            "## 修復提案",
            "",
            field_list(analysis.get("repair_proposals", []) or [], ["target", "proposal_type", "reason", "approval_required"]),
            "",
            "## RAG 候補",
            "",
            field_list(analysis.get("rag_candidates", []) or [], ["candidate_type", "source_ref", "knowledge_value", "limits"]),
            "",
            "## 未解決確認事項",
            "",
            field_list(analysis.get("open_questions", []) or [], ["question", "reason", "blocks"]),
        ]
    )


def create_rag_candidate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir, analysis_path, analysis = load_analysis(repo_root, args.work_id, args.analysis_path)
    if args.publish_rag and args.human_check != "approved":
        raise PermissionError("RAG publication requires --human-check approved.")
    context_gate = require_github_operation_gate(
        repo_root,
        work_dir,
        require_rag_gate=bool(args.publish_rag),
    )
    topic = args.topic or f"github-knowledge-{repository_name(analysis.get('repository', 'repository'))}"
    if args.output:
        output_path = Path(args.output).resolve()
    elif args.publish_rag:
        output_path = repo_root / SOURCE_GITHUB_KNOWLEDGE / rag_source_report_name(topic)
    else:
        output_path = process_report_dir_for_work_dir(work_dir) / f"github-knowledge-rag-candidate-{local_timestamp()}.md"
    write_markdown(output_path, build_rag_candidate(analysis, topic))
    register_artifact(repo_root, work_dir, "GITHUB-KNOWLEDGE-RAG-CANDIDATE", "GitHub Knowledge RAG Candidate", output_path, "report")
    return {
        "rag_candidate": relative_to_repo(repo_root, output_path),
        "analysis_path": relative_to_repo(repo_root, analysis_path),
        "published": bool(args.publish_rag),
        "context_gate": context_gate,
        "gate_restart": github_knowledge_gate_restart(
            "github-knowledge-rag-candidate-gate",
            status="ready",
            restart_reason="normal-rag-candidate-gate",
        ),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "init":
        return init_work(args)
    if args.command == "analysis-template":
        return create_analysis_template(args)
    if args.command == "artifact-integrity":
        return create_artifact_integrity_report(args)
    if args.command == "repair-plan":
        return create_repair_plan(args)
    if args.command == "detect-rebase-candidates":
        return create_detect_rebase_candidates(args)
    if args.command == "rebase-plan":
        return create_rebase_plan(args)
    if args.command == "rebase-review-intake":
        return create_rebase_review_intake(args)
    if args.command == "message-repair-plan":
        return create_message_repair_plan(args)
    if args.command == "message-review-intake":
        return create_message_review_intake(args)
    if args.command == "rebase-apply":
        return create_rebase_apply(args)
    if args.command == "rebase-replay-package":
        return create_rebase_replay_package(args)
    if args.command == "message-repair-package":
        return create_message_repair_package(args)
    if args.command == "rebase-replay-apply":
        return create_rebase_replay_apply(args)
    if args.command == "publish-verified-replay":
        return create_publish_verified_replay(args)
    if args.command == "github-sync-plan":
        return create_sync_plan(args)
    if args.command == "github-sync-review-plan":
        return create_sync_review_plan(args)
    if args.command == "github-sync-review-intake":
        return create_sync_review_intake(args)
    if args.command == "github-sync-apply":
        return create_sync_apply(args)
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
