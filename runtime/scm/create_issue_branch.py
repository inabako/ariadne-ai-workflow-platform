from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import env_value, find_repo_root, load_env, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.scm.scm_utils import current_branch, current_commit, local_branch_exists, require_success, run_git  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or switch to feature/issue-<number> branch.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--issue-number", required=True)
    parser.add_argument("--branch-prefix", default=None)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def create_branch(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    branch_prefix = args.branch_prefix or env_value(settings, "DEFAULT_FEATURE_BRANCH_PREFIX", "FEATURE_BRANCH_PREFIX") or "feature/issue"
    work_dir = repo_root / "work" / args.work_id
    source_dir = Path(args.source_dir).resolve() if args.source_dir else work_dir / "source" / "repository"
    if not source_dir.exists():
        raise FileNotFoundError(f"Source repository does not exist: {source_dir}")

    branch_name = f"{branch_prefix}-{args.issue_number}"
    if not args.dry_run:
        if local_branch_exists(source_dir, branch_name):
            require_success(run_git(["switch", branch_name], source_dir), "git switch issue branch")
        else:
            require_success(run_git(["switch", "-c", branch_name], source_dir), "git create issue branch")

    state = read_json(work_dir / "context" / "scm-state.json", default={}) or {}
    state.update(
        {
            "issue_number": args.issue_number,
            "working_branch": branch_name,
            "current_branch": branch_name if args.dry_run else current_branch(source_dir),
            "current_commit": "dry-run" if args.dry_run else current_commit(source_dir),
            "branch_created_at": utc_now_iso(),
            "dry_run": bool(args.dry_run),
        }
    )
    write_json(work_dir / "context" / "scm-state.json", state)
    return {
        "work_id": args.work_id,
        "source_dir": relative_to_repo(repo_root, source_dir),
        "issue_number": args.issue_number,
        "branch": branch_name,
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
