from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.constants.runtime_values import SCHEMA_VERSION  # noqa: E402
from runtime.common import find_repo_root, load_env, local_timestamp, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.workspace import process_report_dir_for_work_dir, target_repository_dir_for_work_dir, work_dir_for_id  # noqa: E402
from runtime.scm.scm_utils import current_branch, current_commit, require_success, run_git  # noqa: E402


SEMANTIC_COMMIT_RE = re.compile(
    r"^(feat|fix|docs|style|refactor|test|chore|build|ci|perf|revert)(\([A-Za-z0-9_.-]+\))?!?: .+"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Commit workflow changes with semantic commit validation.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--all", action="store_true", help="Run git add -A before commit.")
    parser.add_argument("--allow-empty", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def commit_changes(args: argparse.Namespace) -> dict[str, Any]:
    if not SEMANTIC_COMMIT_RE.match(args.message):
        raise ValueError(
            "Commit message must follow semantic commit format, e.g. 'feat: add remote gateway'."
        )
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    work_dir = work_dir_for_id(repo_root, args.work_id)
    source_dir = Path(args.source_dir).resolve() if args.source_dir else target_repository_dir_for_work_dir(work_dir)
    if not source_dir.exists():
        raise FileNotFoundError(f"Source repository does not exist: {source_dir}")

    if not args.dry_run:
        if settings.get("GIT_USER_NAME"):
            require_success(run_git(["config", "user.name", settings["GIT_USER_NAME"]], source_dir), "git config user.name")
        if settings.get("GIT_USER_EMAIL"):
            require_success(run_git(["config", "user.email", settings["GIT_USER_EMAIL"]], source_dir), "git config user.email")

    if not args.dry_run and args.all:
        require_success(run_git(["add", "-A"], source_dir), "git add")

    status_result = run_git(["status", "--short"], source_dir)
    require_success(status_result, "git status")
    status_before = status_result.stdout.strip()
    if not status_before and not args.allow_empty:
        raise RuntimeError("No changes to commit. Use --allow-empty if this is intentional.")

    if not args.dry_run:
        commit_args = ["commit", "-m", args.message]
        if args.allow_empty:
            commit_args.insert(1, "--allow-empty")
        require_success(run_git(commit_args, source_dir), "git commit")

    commit_hash = "dry-run" if args.dry_run else current_commit(source_dir)
    record = {
        "schema_version": SCHEMA_VERSION,
        "work_id": args.work_id,
        "source_dir": relative_to_repo(repo_root, source_dir),
        "branch": current_branch(source_dir),
        "commit": commit_hash,
        "message": args.message,
        "status_before": status_before,
        "created_at": utc_now_iso(),
        "dry_run": bool(args.dry_run),
    }
    record_path = process_report_dir_for_work_dir(work_dir) / f"commit-record-{local_timestamp()}.json"
    write_json(record_path, record)
    return {**record, "record_path": relative_to_repo(repo_root, record_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = commit_changes(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
