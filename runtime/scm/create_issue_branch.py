from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.constants.workspace import (  # noqa: E402
    context_file,
    target_repository_dir_for_work_dir,
    work_dir_for_id,
)
from runtime.common import (  # noqa: E402
    default_github_owner,
    env_value,
    find_repo_root,
    load_env,
    read_json,
    relative_to_repo,
    repository_to_clone_source,
    repository_to_github_slug,
    write_json,
    utc_now_iso,
)
from runtime.github.api import create_branch_ref, create_linked_branch, get_branch_sha  # noqa: E402
from runtime.scm.scm_utils import (  # noqa: E402
    current_branch,
    current_commit,
    github_token_git_env,
    local_branch_exists,
    require_success,
    run_git,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or switch to feature/issue-<number> branch.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--issue-number", required=True)
    parser.add_argument("--repository", default=None, help="GitHub URL, git URL, owner/name, or local repository path.")
    parser.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    parser.add_argument("--base-branch", default=None, help="Remote base branch used to create the issue branch.")
    parser.add_argument("--branch-prefix", default=None)
    parser.add_argument("--remote", default=None)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--local-only", action="store_true", help="Only create/switch the local branch. Does not create GitHub branch.")
    parser.add_argument("--link-to-issue", action="store_true", help="Create the remote branch as a GitHub linked branch for the issue.")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def clone_issue_branch(
    repository: str,
    branch_name: str,
    source_dir: Path,
    token: str,
    default_owner: str,
    dry_run: bool,
) -> None:
    source_dir.parent.mkdir(parents=True, exist_ok=True)
    clone_source = repository_to_clone_source(repository, default_owner)
    command = ["clone", "--branch", branch_name, "--single-branch", clone_source, str(source_dir)]
    if dry_run:
        return
    with github_token_git_env(token) as git_env:
        require_success(run_git(command, source_dir.parent, env=git_env), "git clone issue branch")


def checkout_existing_repository(source_dir: Path, remote: str, branch_name: str, dry_run: bool) -> None:
    if dry_run:
        return
    require_success(run_git(["fetch", remote, branch_name], source_dir), "git fetch issue branch")
    if local_branch_exists(source_dir, branch_name):
        require_success(run_git(["switch", branch_name], source_dir), "git switch issue branch")
    else:
        require_success(
            run_git(["switch", "--track", "-c", branch_name, f"{remote}/{branch_name}"], source_dir),
            "git checkout issue branch",
        )


def create_branch(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    default_owner = default_github_owner(settings)
    branch_prefix = args.branch_prefix or env_value(settings, "DEFAULT_FEATURE_BRANCH_PREFIX", "FEATURE_BRANCH_PREFIX") or "feature/issue"
    work_dir = work_dir_for_id(repo_root, args.work_id)
    source_dir = Path(args.source_dir).resolve() if args.source_dir else target_repository_dir_for_work_dir(work_dir)
    state = read_json(context_file(work_dir, "scm-state.json"), default={}) or {}
    agent_context = read_json(context_file(work_dir, "agent-context.json"), default={}) or {}

    branch_name = f"{branch_prefix}-{args.issue_number}"
    repository = args.repository or state.get("repository") or agent_context.get("project", {}).get("repository", "")
    github_repo = (
        repository_to_github_slug(args.github_repo, default_owner)
        if args.github_repo
        else repository_to_github_slug(str(repository), default_owner)
    )
    base_branch = (
        args.base_branch
        or state.get("target_branch")
        or state.get("base_branch")
        or state.get("current_branch")
        or env_value(settings, "DEFAULT_GIT_TARGET_BRANCH", "GIT_TARGET_BRANCH")
        or "main"
    )
    remote = args.remote or state.get("remote") or env_value(settings, "DEFAULT_GIT_REMOTE_NAME", "GIT_REMOTE_NAME") or "origin"
    token = env_value(settings, "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN", "GITHUB_API_KEY")

    remote_ref = ""
    base_sha = ""
    linked_branch: dict[str, Any] = {}
    if args.local_only:
        linked_branch = {
            "status": "skipped_local_only" if args.link_to_issue else "not_requested",
        }
        if not source_dir.exists():
            raise FileNotFoundError(f"Source repository does not exist: {source_dir}")
        if not args.dry_run:
            if local_branch_exists(source_dir, branch_name):
                require_success(run_git(["switch", branch_name], source_dir), "git switch issue branch")
            else:
                require_success(run_git(["switch", "-c", branch_name], source_dir), "git create issue branch")
    else:
        if not github_repo:
            raise ValueError("GitHub repository is required. Set --repository/--github-repo or initialize agent context.")
        if not repository:
            repository = f"https://github.com/{github_repo}.git"

        if args.dry_run:
            base_sha = "dry-run"
            remote_ref = f"refs/heads/{branch_name}"
            if args.link_to_issue:
                linked_branch = {
                    "status": "dry-run",
                    "linked_branch_name": branch_name,
                    "base_oid": base_sha,
                }
        else:
            if args.link_to_issue:
                linked_branch = create_linked_branch(settings, github_repo, args.issue_number, branch_name, str(base_branch))
                base_sha = str(linked_branch.get("base_oid") or "")
                remote_ref = f"refs/heads/{linked_branch.get('linked_branch_name') or branch_name}"
            else:
                base_sha = get_branch_sha(settings, github_repo, str(base_branch))
                remote_ref = create_branch_ref(settings, github_repo, branch_name, base_sha)

        if source_dir.exists():
            checkout_existing_repository(source_dir, remote, branch_name, args.dry_run)
        else:
            clone_issue_branch(str(repository), branch_name, source_dir, token, default_owner, args.dry_run)

    state.update(
        {
            "issue_number": args.issue_number,
            "repository": repository,
            "github_repo": github_repo,
            "remote": remote,
            "target_branch": base_branch,
            "base_branch": base_branch,
            "working_branch": branch_name,
            "current_branch": branch_name if args.dry_run else current_branch(source_dir),
            "current_commit": "dry-run" if args.dry_run else current_commit(source_dir),
            "remote_branch_ref": remote_ref,
            "remote_branch_base_sha": base_sha,
            "linked_branch_status": linked_branch.get("status") or ("created" if args.link_to_issue else "not_requested"),
            "linked_branch_id": linked_branch.get("linked_branch_id", ""),
            "linked_branch_name": linked_branch.get("linked_branch_name", ""),
            "linked_branch_issue_id": linked_branch.get("issue_id", ""),
            "linked_branch_repository_id": linked_branch.get("repository_id", ""),
            "branch_created_at": utc_now_iso(),
            "dry_run": bool(args.dry_run),
        }
    )
    write_json(context_file(work_dir, "scm-state.json"), state)
    return {
        "work_id": args.work_id,
        "source_dir": relative_to_repo(repo_root, source_dir),
        "issue_number": args.issue_number,
        "branch": branch_name,
        "github_repo": github_repo,
        "base_branch": base_branch,
        "remote_branch_ref": remote_ref,
        "linked_branch_status": linked_branch.get("status") or ("created" if args.link_to_issue else "not_requested"),
        "linked_branch_id": linked_branch.get("linked_branch_id", ""),
        "dry_run": bool(args.dry_run),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = create_branch(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
