from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import quote

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    default_github_owner,
    find_repo_root,
    load_env,
    local_timestamp,
    read_json,
    relative_to_repo,
    repository_to_github_slug,
    utc_now_iso,
    write_json,
    write_markdown_bom,
)
from runtime.github.api import github_api_json  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or draft a GitHub Pull Request for an issue branch.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    parser.add_argument("--base", default="develop")
    parser.add_argument("--head", default=None)
    parser.add_argument("--title-file", default=None)
    parser.add_argument("--body-file", default=None)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--human-check", choices=["approved"], default=None)
    return parser


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def latest_issue_title(repo_root: Path, work_dir: Path) -> str:
    issue_records = sorted((work_dir / "process-report").glob("github-issue-*.json"))
    base_work_id = str((read_json(work_dir / "context" / "scm-state.json", default={}) or {}).get("base_work_id", ""))
    if base_work_id:
        issue_records.extend(sorted((repo_root / "work" / base_work_id / "process-report").glob("github-issue-*.json")))
    for path in reversed(issue_records):
        record = read_json(path, default={}) or {}
        title = str(record.get("title", "")).strip()
        if title:
            return title
    return ""


def default_pr_title(repo_root: Path, work_dir: Path) -> str:
    title_file = work_dir / "process-report" / "pull-request-title.md"
    if title_file.exists():
        return read_text(title_file)
    issue_title = latest_issue_title(repo_root, work_dir)
    if issue_title:
        return issue_title
    return f"{work_dir.name}: pull request"


def default_pr_body(work_dir: Path) -> str:
    body_file = work_dir / "process-report" / "pull-request-description.md"
    if body_file.exists():
        return read_text(body_file)
    return f"""# Pull Request

## Issue

`{work_dir.name}`

## Change Sequence

```mermaid
sequenceDiagram
  participant Issue as GitHub Issue
  participant Branch as feature/issue branch
  participant Tests as Tests / Evidence
  participant PR as Pull Request
  participant Develop as develop
  Issue->>Branch: create linked issue branch
  Branch->>Tests: implement and verify
  Tests->>Branch: commit evidence
  Branch->>PR: push branch and open PR
  PR->>Develop: review and merge
```
"""


def create_pull_request_with_api(
    settings: dict[str, str],
    github_repo: str,
    title: str,
    body: str,
    head: str,
    base: str,
) -> dict[str, Any]:
    owner, repo = github_repo.split("/", 1)
    return github_api_json(
        settings,
        "POST",
        f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/pulls",
        {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
        },
    )


def manage_pull_request(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")

    scm_state = read_json(work_dir / "context" / "scm-state.json", default={}) or {}
    owner = default_github_owner(settings)
    github_repo = repository_to_github_slug(args.github_repo, owner) if args.github_repo else str(scm_state.get("github_repo", ""))
    if not github_repo:
        github_repo = repository_to_github_slug(str(scm_state.get("repository", "")), owner)
    if not github_repo or "/" not in github_repo:
        raise ValueError("GitHub repository is required. Run repository preparation first or set --github-repo.")

    head = args.head or str(scm_state.get("pushed_branch") or scm_state.get("working_branch") or "")
    if not head:
        raise ValueError("PR head branch is required. Push the issue branch first or set --head.")

    title = read_text(Path(args.title_file)) if args.title_file else default_pr_title(repo_root, work_dir)
    body = read_text(Path(args.body_file)) if args.body_file else default_pr_body(work_dir)

    pr_url = ""
    pr_number = ""
    status = "draft"
    if args.create:
        if args.human_check != "approved":
            raise ValueError("--create requires --human-check approved.")
        data = create_pull_request_with_api(settings, github_repo, title, body, head, args.base)
        pr_url = str(data.get("html_url", ""))
        pr_number = str(data.get("number", ""))
        status = "created"

    record = {
        "schema_version": "1.0",
        "work_id": args.work_id,
        "github_repo": github_repo,
        "title": title,
        "base": args.base,
        "head": head,
        "body_file": relative_to_repo(repo_root, Path(args.body_file).resolve()) if args.body_file else relative_to_repo(repo_root, work_dir / "process-report" / "pull-request-description.md"),
        "status": status,
        "pull_request_url": pr_url,
        "pull_request_number": pr_number,
        "created_at": utc_now_iso(),
    }
    record_path = work_dir / "process-report" / f"pull-request-{local_timestamp()}.json"
    markdown_path = work_dir / "process-report" / f"pull-request-{local_timestamp()}.md"
    write_json(record_path, record)
    write_markdown_bom(
        markdown_path,
        f"""# Pull Request {'Created' if args.create else 'Draft'}

| Item | Value |
| --- | --- |
| Repository | `{github_repo}` |
| Title | {title} |
| Head | `{head}` |
| Base | `{args.base}` |
| Status | {status} |
| URL | {pr_url or 'not-created'} |
""",
    )

    state = {**scm_state, "pull_request_record": relative_to_repo(repo_root, record_path)}
    if pr_url:
        state.update({"pull_request_url": pr_url, "pull_request_number": pr_number})
    write_json(work_dir / "context" / "scm-state.json", state)
    return {**record, "record_path": relative_to_repo(repo_root, record_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = manage_pull_request(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
