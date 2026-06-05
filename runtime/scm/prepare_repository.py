from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    default_github_owner,
    find_repo_root,
    extract_repository_config_from_files,
    env_value,
    load_artifact_index,
    load_env,
    read_json,
    requirement_files_from_artifact_index,
    relative_to_repo,
    repository_to_clone_source,
    upsert_artifact,
    utc_now_iso,
    write_json,
)
from runtime.scm.scm_utils import current_branch, current_commit, github_token_git_env, is_git_repository, require_success, run_git  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare target repository and branch for workflow execution.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--repository", default=None, help="GitHub URL, git URL, owner/name, or local repository path.")
    parser.add_argument("--target-branch", default=None)
    parser.add_argument("--remote", default=None)
    parser.add_argument("--requirements", nargs="*", help="Requirement files used to resolve repository settings.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None, help="Default: work/<id>/source/repository")
    parser.add_argument("--no-pull", action="store_true", help="Fetch only; do not pull after checkout.")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def clone_repository(repository: str, target_branch: str, source_dir: Path, token: str, dry_run: bool) -> None:
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    command = ["clone", "--branch", target_branch, "--single-branch", repository, str(source_dir)]
    if dry_run:
        return
    with github_token_git_env(token) as git_env:
        require_success(run_git(command, source_dir.parent, env=git_env), "git clone")


def prepare_repository(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    default_owner = default_github_owner(settings)
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    requirement_files = [
        Path(path).resolve() for path in args.requirements
    ] if args.requirements else requirement_files_from_artifact_index(repo_root, work_dir)
    requirement_config = extract_repository_config_from_files(requirement_files)

    repository = args.repository or requirement_config.get("repository")
    target_branch = (
        args.target_branch
        or requirement_config.get("target_branch")
        or env_value(settings, "DEFAULT_GIT_TARGET_BRANCH", "GIT_TARGET_BRANCH")
        or "main"
    )
    remote = args.remote or requirement_config.get("remote") or env_value(settings, "DEFAULT_GIT_REMOTE_NAME", "GIT_REMOTE_NAME") or "origin"
    if not repository:
        raise ValueError(
            "Repository is required. Set --repository, requirement Repository Control, "
            "or reject the requirement during intake."
        )
    source_dir = Path(args.source_dir).resolve() if args.source_dir else work_dir / "source" / "repository"

    if source_dir.exists() and not is_git_repository(source_dir):
        raise RuntimeError(f"Source directory exists but is not a git repository: {source_dir}")
    if not source_dir.exists():
        token = env_value(settings, "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN", "GITHUB_API_KEY")
        clone_repository(repository_to_clone_source(repository, default_owner), target_branch, source_dir, token, args.dry_run)

    if not args.dry_run:
        require_success(run_git(["fetch", remote, target_branch], source_dir), "git fetch")
        require_success(run_git(["checkout", target_branch], source_dir), "git checkout target branch")
        if not args.no_pull:
            require_success(run_git(["pull", "--ff-only", remote, target_branch], source_dir), "git pull")

    branch = target_branch if args.dry_run else current_branch(source_dir)
    commit = "dry-run" if args.dry_run else current_commit(source_dir)
    state = {
        "schema_version": "1.0",
        "work_id": args.work_id,
        "repository": repository,
        "repository_source": "cli" if args.repository else "requirements",
        "requirement_files": [relative_to_repo(repo_root, path) for path in requirement_files],
        "source_dir": relative_to_repo(repo_root, source_dir),
        "remote": remote,
        "target_branch": target_branch,
        "current_branch": branch,
        "current_commit": commit,
        "prepared_at": utc_now_iso(),
        "dry_run": bool(args.dry_run),
    }

    context_dir = work_dir / "context"
    write_json(context_dir / "scm-state.json", state)

    agent_context = read_json(context_dir / "agent-context.json", default={}) or {}
    project_name = agent_context.get("project", {}).get("name", args.work_id)
    workflow_name = agent_context.get("workflow", {}).get("name", "")
    artifact_index = load_artifact_index(work_dir, project_name, workflow_name)
    now = utc_now_iso()
    upsert_artifact(
        artifact_index,
        {
            "id": "SCM-STATE",
            "title": "SCM State",
            "path": relative_to_repo(repo_root, context_dir / "scm-state.json"),
            "type": "other",
            "status": "draft",
            "owner_agent": "runtime-scm",
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["runtime-github", "runtime-retrieval"],
            "summary": "Target repository and branch preparation state.",
            "unresolved_items": [],
        },
    )
    write_json(context_dir / "artifact-index.json", artifact_index)
    return state


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = prepare_repository(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
