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
    load_env,
    local_timestamp,
    read_json,
    relative_to_repo,
    repository_to_github_slug,
    utc_now_iso,
    write_json,
)
from runtime.scm.commit_changes import SEMANTIC_COMMIT_RE  # noqa: E402
from runtime.scm.scm_utils import (  # noqa: E402
    current_branch,
    current_commit,
    github_token_git_env,
    is_git_repository,
    require_success,
    run_git,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize and push the first commit to a precreated GitHub repository.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    parser.add_argument("--initial-branch", default=None)
    parser.add_argument("--remote", default=None)
    parser.add_argument("--message", default="chore: bootstrap realtime iac repository")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--human-check", choices=["approved"], default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def ensure_git_repository(source_dir: Path, initial_branch: str, dry_run: bool) -> None:
    source_dir.mkdir(parents=True, exist_ok=True)
    if dry_run:
        return
    if not is_git_repository(source_dir):
        require_success(run_git(["init"], source_dir), "git init")
    require_success(run_git(["checkout", "-B", initial_branch], source_dir), "git checkout initial branch")


def set_remote(source_dir: Path, remote: str, repository_url: str, dry_run: bool) -> None:
    if dry_run:
        return
    existing = run_git(["remote", "get-url", remote], source_dir)
    if existing.returncode == 0:
        require_success(run_git(["remote", "set-url", remote, repository_url], source_dir), "git remote set-url")
    else:
        require_success(run_git(["remote", "add", remote, repository_url], source_dir), "git remote add")


def verify_remote_access(cwd: Path, repository_url: str, token: str, dry_run: bool) -> None:
    if dry_run:
        return
    with github_token_git_env(token) as git_env:
        require_success(run_git(["ls-remote", repository_url], cwd, env=git_env), "git ls-remote precreated repository")


def has_head(source_dir: Path) -> bool:
    return run_git(["rev-parse", "--verify", "HEAD"], source_dir).returncode == 0


def bootstrap_repository(args: argparse.Namespace) -> dict[str, Any]:
    if not SEMANTIC_COMMIT_RE.match(args.message):
        raise ValueError("Commit message must follow semantic commit format, e.g. 'chore: bootstrap realtime iac repository'.")
    if args.push and args.human_check != "approved":
        raise ValueError("Initial repository push requires --human-check approved.")

    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    scm_state = read_json(work_dir / "context" / "scm-state.json", default={}) or {}
    source_dir = Path(args.source_dir).resolve() if args.source_dir else work_dir / "source" / "repository"
    if source_dir.resolve() == repo_root.resolve():
        raise ValueError("Refusing to initialize or push the workflow repository itself.")

    default_owner = default_github_owner(settings)
    github_repo = (
        repository_to_github_slug(args.github_repo, default_owner)
        if args.github_repo
        else repository_to_github_slug(str(scm_state.get("github_repo") or scm_state.get("repository", "")), default_owner)
    )
    if not github_repo:
        raise ValueError("GitHub repository is required. Create it on GitHub first, then pass --github-repo owner/name.")
    repository_url = f"https://github.com/{github_repo}.git"
    initial_branch = args.initial_branch or scm_state.get("target_branch") or "main"
    remote = args.remote or scm_state.get("remote") or env_value(settings, "DEFAULT_GIT_REMOTE_NAME", "GIT_REMOTE_NAME") or "origin"

    token = env_value(settings, "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN", "GITHUB_API_KEY")
    verify_remote_access(repo_root, repository_url, token, args.dry_run)
    ensure_git_repository(source_dir, str(initial_branch), args.dry_run)
    if not args.dry_run:
        if settings.get("GIT_USER_NAME"):
            require_success(run_git(["config", "user.name", settings["GIT_USER_NAME"]], source_dir), "git config user.name")
        if settings.get("GIT_USER_EMAIL"):
            require_success(run_git(["config", "user.email", settings["GIT_USER_EMAIL"]], source_dir), "git config user.email")
        require_success(run_git(["add", "-A"], source_dir), "git add")
        status = run_git(["status", "--short"], source_dir)
        require_success(status, "git status")
        if status.stdout.strip():
            require_success(run_git(["commit", "-m", args.message], source_dir), "git commit")
        elif not has_head(source_dir):
            raise RuntimeError("No files to bootstrap. Generate IaC artifacts before initial repository push.")
    set_remote(source_dir, remote, repository_url, args.dry_run)
    if args.push and not args.dry_run:
        with github_token_git_env(token) as git_env:
            require_success(run_git(["push", "-u", remote, str(initial_branch)], source_dir, env=git_env), "git push initial branch")

    branch = str(initial_branch) if args.dry_run else current_branch(source_dir)
    commit = "dry-run" if args.dry_run else current_commit(source_dir)
    record = {
            "schema_version": "1.0",
            "work_id": args.work_id,
        "source_dir": relative_to_repo(repo_root, source_dir),
        "github_repo": github_repo,
        "repository": repository_url,
        "remote": remote,
        "initial_branch": initial_branch,
        "current_branch": branch,
        "current_commit": commit,
        "message": args.message,
        "pushed": bool(args.push and not args.dry_run),
        "human_check": args.human_check,
        "created_at": utc_now_iso(),
        "dry_run": bool(args.dry_run),
    }
    record_path = work_dir / "process-report" / f"bootstrap-repository-{local_timestamp()}.json"
    write_json(record_path, record)
    scm_state.update(
        {
            "repository_mode": "precreated-new",
            "repository": repository_url,
            "github_repo": github_repo,
            "source_dir": relative_to_repo(repo_root, source_dir),
            "remote": remote,
            "target_branch": initial_branch,
            "base_branch": initial_branch,
            "current_branch": branch,
            "current_commit": commit,
            "bootstrap_record": relative_to_repo(repo_root, record_path),
            "initial_push_complete": bool(args.push and not args.dry_run),
        }
    )
    write_json(work_dir / "context" / "scm-state.json", scm_state)
    return {**record, "record_path": relative_to_repo(repo_root, record_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = bootstrap_repository(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
