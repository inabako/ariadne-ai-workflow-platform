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
    env_value,
    find_repo_root,
    load_artifact_index,
    load_env,
    read_json,
    relative_to_repo,
    repository_to_clone_source,
    upsert_artifact,
    utc_now_iso,
    write_json,
)
from runtime.constants.workspace import (  # noqa: E402
    context_dir_for_work_dir,
    process_report_dir_for_work_dir,
    source_dir_for_work_dir,
    work_dir_for_id,
    work_path_pattern,
)
from runtime.scm.scm_utils import current_branch, current_commit, github_token_git_env, is_git_repository, require_success, run_git  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Prepare a support repository under {work_path_pattern('source', work_id='<id>')}.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--name", required=True, help=f"Directory name under {work_path_pattern('source', work_id='<id>')}.")
    parser.add_argument("--repository", required=True, help="GitHub URL, git URL, owner/name, or repository name.")
    parser.add_argument("--branch", default=None)
    parser.add_argument("--remote", default=None)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--no-pull", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def clone_repository(repository: str, branch: str, source_dir: Path, token: str, dry_run: bool) -> None:
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    command = ["clone", "--branch", branch, "--single-branch", repository, str(source_dir)]
    if dry_run:
        return
    with github_token_git_env(token) as git_env:
        require_success(run_git(command, source_dir.parent, env=git_env), "git clone support repository")


def prepare_support_repository(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    work_dir = work_dir_for_id(repo_root, args.work_id)
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")

    branch = args.branch or env_value(settings, "DEFAULT_GIT_TARGET_BRANCH", "GIT_TARGET_BRANCH") or "main"
    remote = args.remote or env_value(settings, "DEFAULT_GIT_REMOTE_NAME", "GIT_REMOTE_NAME") or "origin"
    source_dir = Path(args.source_dir).resolve() if args.source_dir else source_dir_for_work_dir(work_dir) / args.name

    if source_dir.exists() and not is_git_repository(source_dir):
        raise RuntimeError(f"Support source directory exists but is not a git repository: {source_dir}")

    action = "exists"
    if not source_dir.exists():
        token = env_value(settings, "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN", "GITHUB_API_KEY")
        clone_source = repository_to_clone_source(args.repository, default_github_owner(settings))
        clone_repository(clone_source, branch, source_dir, token, args.dry_run)
        action = "cloned"
    elif not args.dry_run:
        require_success(run_git(["fetch", remote, branch], source_dir), "git fetch support repository")
        require_success(run_git(["checkout", branch], source_dir), "git checkout support repository")
        if not args.no_pull:
            require_success(run_git(["pull", "--ff-only", remote, branch], source_dir), "git pull support repository")
        action = "updated"

    result = {
        "schema_version": "1.0",
        "work_id": args.work_id,
        "name": args.name,
        "repository": args.repository,
        "source_dir": relative_to_repo(repo_root, source_dir),
        "remote": remote,
        "branch": branch if args.dry_run else current_branch(source_dir),
        "commit": "dry-run" if args.dry_run else current_commit(source_dir),
        "action": "dry-run" if args.dry_run else action,
        "prepared_at": utc_now_iso(),
        "dry_run": bool(args.dry_run),
    }

    context_dir = context_dir_for_work_dir(work_dir)
    support_state_path = context_dir / "support-repositories.json"
    support_state = read_json(support_state_path, default={"schema_version": "1.0", "repositories": []}) or {}
    repositories = support_state.setdefault("repositories", [])
    repositories[:] = [item for item in repositories if item.get("name") != args.name]
    repositories.append(result)
    write_json(support_state_path, support_state)

    report_path = process_report_dir_for_work_dir(work_dir) / f"support-repository-{args.name}.json"
    write_json(report_path, result)

    agent_context = read_json(context_dir / "agent-context.json", default={}) or {}
    project_name = agent_context.get("project", {}).get("name", args.work_id)
    workflow_name = agent_context.get("workflow", {}).get("name", "")
    artifact_index = load_artifact_index(work_dir, project_name, workflow_name)
    now = utc_now_iso()
    upsert_artifact(
        artifact_index,
        {
            "id": f"SUPPORT-REPOSITORY-{args.name.upper()}",
            "title": f"Support Repository: {args.name}",
            "path": relative_to_repo(repo_root, report_path),
            "type": "process-report",
            "status": "draft",
            "owner_agent": "runtime-scm",
            "created_at": now,
            "updated_at": now,
            "depends_on": ["RAG-LOAD"],
            "consumed_by": ["environment-preflight", "integration-test"],
            "summary": "Support repository prepared from RAG or workflow dependency discovery.",
            "unresolved_items": [],
        },
    )
    upsert_artifact(
        artifact_index,
        {
            "id": "SUPPORT-REPOSITORIES",
            "title": "Support Repositories",
            "path": relative_to_repo(repo_root, support_state_path),
            "type": "other",
            "status": "draft",
            "owner_agent": "runtime-scm",
            "created_at": now,
            "updated_at": now,
            "depends_on": ["RAG-LOAD"],
            "consumed_by": ["environment-preflight", "integration-test"],
            "summary": "Repository-local inventory of support components prepared for this work item.",
            "unresolved_items": [],
        },
    )
    write_json(context_dir / "artifact-index.json", artifact_index)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = prepare_support_repository(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
