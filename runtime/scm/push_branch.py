from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import env_value, find_repo_root, load_env, local_timestamp, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.workspace import TARGET_REPOSITORY_PATTERN, context_file, process_report_dir_for_work_dir, target_repository_dir_for_work_dir, work_dir_for_id  # noqa: E402
from runtime.scm.scm_utils import current_branch, github_token_git_env, require_success, run_git  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Push the current issue branch after human approval.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--remote", default=None)
    parser.add_argument("--branch", default=None)
    parser.add_argument("--set-upstream", action="store_true")
    parser.add_argument("--human-check", required=True, choices=["approved"])
    parser.add_argument("--dry-run", action="store_true")
    return parser


def push_branch(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    work_dir = work_dir_for_id(repo_root, args.work_id)
    source_dir = Path(args.source_dir).resolve() if args.source_dir else target_repository_dir_for_work_dir(work_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"Source repository does not exist: {source_dir}")
    if source_dir.resolve() == repo_root.resolve():
        raise ValueError(f"Refusing to push the workflow repository itself. Set --source-dir to {TARGET_REPOSITORY_PATTERN}.")

    scm_state_path = context_file(work_dir, "scm-state.json")
    scm_state = read_json(scm_state_path, default={}) or {}
    remote = args.remote or scm_state.get("remote") or "origin"
    branch = args.branch or scm_state.get("working_branch") or current_branch(source_dir)
    if not branch.startswith("feature/issue-"):
        raise ValueError(f"Refusing to push non-issue branch: {branch}")

    command = ["push"]
    if args.set_upstream:
        command.append("-u")
    command.extend([remote, branch])
    if not args.dry_run:
        token = env_value(settings, "GITHUB_TOKEN", "GH_TOKEN", "GITHUB_API_TOKEN", "GITHUB_API_KEY")
        with github_token_git_env(token) as git_env:
            require_success(run_git(command, source_dir, env=git_env), "git push")

    record = {
        "schema_version": "1.0",
        "work_id": args.work_id,
        "source_dir": relative_to_repo(repo_root, source_dir),
        "remote": remote,
        "branch": branch,
        "human_check": args.human_check,
        "pushed_at": utc_now_iso(),
        "dry_run": bool(args.dry_run),
    }
    record_path = process_report_dir_for_work_dir(work_dir) / f"push-record-{local_timestamp()}.json"
    write_json(record_path, record)
    state = {**scm_state, "pushed_branch": branch, "pushed_at": record["pushed_at"], "push_record": relative_to_repo(repo_root, record_path)}
    write_json(scm_state_path, state)
    return {**record, "record_path": relative_to_repo(repo_root, record_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = push_branch(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
