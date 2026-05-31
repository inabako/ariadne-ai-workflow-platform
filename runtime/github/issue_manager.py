from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    find_repo_root,
    env_value,
    load_artifact_index,
    load_env,
    local_timestamp,
    read_json,
    relative_to_repo,
    repository_to_github_slug,
    upsert_artifact,
    utc_now_iso,
    write_json,
    write_markdown_bom,
)


ISSUE_URL_RE = re.compile(r"/issues/(\d+)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or draft a GitHub Issue for workflow changes.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", default=None)
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--assignee", action="append", default=[])
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--create", action="store_true", help="Actually create the issue using GitHub CLI.")
    return parser


def collect_artifact_paths(work_dir: Path) -> list[str]:
    index = read_json(work_dir / "context" / "artifact-index.json", default={}) or {}
    artifacts = index.get("artifacts", [])
    return [artifact.get("path", "") for artifact in artifacts if artifact.get("path")]


def default_issue_body(repo_root: Path, work_dir: Path) -> str:
    context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    scm_state = read_json(work_dir / "context" / "scm-state.json", default={}) or {}
    artifact_paths = collect_artifact_paths(work_dir)

    lines = [
        "## Intent",
        "",
        context.get("intent", {}).get("summary", "TBD"),
        "",
        "## Repository State",
        "",
        f"- Source: `{scm_state.get('source_dir', 'TBD')}`",
        f"- Target branch: `{scm_state.get('target_branch', 'TBD')}`",
        f"- Current commit: `{scm_state.get('current_commit', 'TBD')}`",
        "",
        "## Scope",
        "",
        "- Compare requirement documents with the current repository state.",
        "- Define implementation scope and affected components.",
        "- Preserve safety, rollback, and observability requirements.",
        "",
        "## Artifacts",
        "",
    ]
    if artifact_paths:
        lines.extend(f"- `{path}`" for path in artifact_paths)
    else:
        lines.append("- No artifacts registered yet.")
    lines.extend(
        [
            "",
            "## Acceptance Criteria",
            "",
            "- Required design documents are updated.",
            "- Required tests and test evidence are created.",
            "- Safety-critical QA is resolved or explicitly blocked.",
            "- Changes are committed on `feature/issue-<issue-number>` with a semantic commit message.",
        ]
    )
    return "\n".join(lines)


def create_issue_with_gh(
    github_repo: str,
    title: str,
    body_file: Path,
    labels: list[str],
    assignees: list[str],
    env: dict[str, str],
) -> tuple[str, str | None]:
    command = ["gh", "issue", "create", "--repo", github_repo, "--title", title, "--body-file", str(body_file)]
    for label in labels:
        command.extend(["--label", label])
    for assignee in assignees:
        command.extend(["--assignee", assignee])
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        shell=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"gh issue create failed: {detail}")
    issue_url = result.stdout.strip()
    match = ISSUE_URL_RE.search(issue_url)
    return issue_url, match.group(1) if match else None


def manage_issue(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    work_dir = repo_root / "work" / args.work_id
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    scm_state = read_json(work_dir / "context" / "scm-state.json", default={}) or {}
    scm_github_repo = repository_to_github_slug(str(scm_state.get("repository", "")))
    github_repo = args.github_repo or scm_github_repo
    if not github_repo:
        raise ValueError("GitHub repository is required. Run runtime/scm/prepare_repository.py first or set --github-repo.")
    labels = args.label or [
        item.strip()
        for item in env_value(settings, "DEFAULT_GITHUB_ISSUE_LABELS", "GITHUB_DEFAULT_LABELS").split(",")
        if item.strip()
    ]
    assignees = args.assignee or [
        item.strip()
        for item in env_value(settings, "DEFAULT_GITHUB_ISSUE_ASSIGNEES", "GITHUB_DEFAULT_ASSIGNEES").split(",")
        if item.strip()
    ]

    body_text = Path(args.body_file).read_text(encoding="utf-8-sig") if args.body_file else default_issue_body(repo_root, work_dir)
    issue_id = f"github-issue-{local_timestamp()}"
    draft_md = work_dir / "process-report" / f"{issue_id}.md"
    draft_json = work_dir / "process-report" / f"{issue_id}.json"
    write_markdown_bom(draft_md, body_text)

    issue_url = None
    issue_number = None
    status = "draft"
    if args.create:
        process_env = os.environ.copy()
        if settings.get("GITHUB_TOKEN") and not process_env.get("GH_TOKEN"):
            process_env["GH_TOKEN"] = settings["GITHUB_TOKEN"]
        if settings.get("GH_HOST"):
            process_env["GH_HOST"] = settings["GH_HOST"]
        issue_url, issue_number = create_issue_with_gh(
            github_repo,
            args.title,
            draft_md,
            labels,
            assignees,
            process_env,
        )
        status = "created"

    issue_record = {
        "schema_version": "1.0",
        "work_id": args.work_id,
        "github_repo": github_repo,
        "title": args.title,
        "body_path": relative_to_repo(repo_root, draft_md),
        "labels": labels,
        "assignees": assignees,
        "status": status,
        "issue_url": issue_url,
        "issue_number": issue_number,
        "created_at": utc_now_iso(),
    }
    write_json(draft_json, issue_record)

    agent_context = read_json(work_dir / "context" / "agent-context.json", default={}) or {}
    project_name = agent_context.get("project", {}).get("name", args.work_id)
    workflow_name = agent_context.get("workflow", {}).get("name", "")
    index = load_artifact_index(work_dir, project_name, workflow_name)
    now = utc_now_iso()
    for artifact_id, title, path in [
        ("GITHUB-ISSUE-MD", draft_md.name, draft_md),
        ("GITHUB-ISSUE-JSON", draft_json.name, draft_json),
    ]:
        upsert_artifact(
            index,
            {
                "id": f"{artifact_id}-{issue_id}",
                "title": title,
                "path": relative_to_repo(repo_root, path),
                "type": "report",
                "status": "draft" if status == "draft" else "approved",
                "owner_agent": "runtime-github",
                "created_at": now,
                "updated_at": now,
                "depends_on": [],
                "consumed_by": ["runtime-scm"],
                "summary": "GitHub Issue draft or creation record.",
                "unresolved_items": [] if issue_number else ["Issue number is not available until created."],
            },
        )
    write_json(work_dir / "context" / "artifact-index.json", index)
    return issue_record


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = manage_issue(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
