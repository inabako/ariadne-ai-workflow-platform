from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import quote

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    default_github_owner,
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
from runtime.constants.workspace import (  # noqa: E402
    context_file,
    process_report_dir_for_work_dir,
    target_repository_dir_for_work_dir,
    work_dir_for_id,
)
from runtime.github.api import github_api_json  # noqa: E402


ISSUE_URL_RE = re.compile(r"/issues/(\d+)")
ISSUE_TITLE_PREFIXES = {
    "new-feature": "新規機能フロー",
    "improvement": "改善フロー",
    "initial-development": "初期開発",
    "iac": "IaC",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or draft a GitHub Issue for workflow changes.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--github-repo", default=None, help="GitHub repository in owner/name format.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--flow-label", choices=sorted(ISSUE_TITLE_PREFIXES), default=None)
    parser.add_argument("--title-prefix", default=None, help="Issue title prefix label without brackets, for example 改善フロー.")
    parser.add_argument("--body-file", default=None)
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--assignee", action="append", default=[])
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--create", action="store_true", help="Actually create the issue using GitHub REST API.")
    return parser


def infer_flow_label(work_dir: Path) -> str:
    context = read_json(context_file(work_dir, "agent-context.json"), default={}) or {}
    workflow_name = str(context.get("workflow", {}).get("name", "")).lower()
    if "ariadne-new-system" in workflow_name or "new-system" in workflow_name:
        return ISSUE_TITLE_PREFIXES["initial-development"]
    if "maintenance" in workflow_name or "feature" in workflow_name:
        return ISSUE_TITLE_PREFIXES["new-feature"]
    if "corrective" in workflow_name or "docs-sync" in workflow_name:
        return ISSUE_TITLE_PREFIXES["improvement"]
    return ""


def normalize_issue_title(title: str, flow_label: str = "", explicit_prefix: str = "") -> tuple[str, str]:
    prefix = explicit_prefix.strip() or ISSUE_TITLE_PREFIXES.get(flow_label, "")
    if not prefix:
        return title, ""
    bracketed = f"[{prefix}]"
    if title.strip().startswith(bracketed):
        return title, prefix
    return f"{bracketed} {title.strip()}", prefix


def collect_artifact_paths(work_dir: Path) -> list[str]:
    index = read_json(context_file(work_dir, "artifact-index.json"), default={}) or {}
    artifacts = index.get("artifacts", [])
    return [artifact.get("path", "") for artifact in artifacts if artifact.get("path")]


def resolve_source_dir(repo_root: Path, work_dir: Path, scm_state: dict[str, Any]) -> Path:
    source_dir = str(scm_state.get("source_dir", "")).strip()
    if source_dir:
        path = Path(source_dir)
        return path.resolve() if path.is_absolute() else (repo_root / path).resolve()
    return target_repository_dir_for_work_dir(work_dir).resolve()


def project_issue_template_path(repo_root: Path, work_dir: Path, scm_state: dict[str, Any]) -> Path | None:
    template_path = resolve_source_dir(repo_root, work_dir, scm_state) / ".github" / "ISSUE_TEMPLATE.md"
    return template_path if template_path.exists() else None


def corrective_action_report_path(artifact_paths: list[str]) -> str:
    for path in artifact_paths:
        if "corrective-action-report" in path.replace("\\", "/"):
            return path
    return ""


def fill_project_issue_template(template_text: str, scm_state: dict[str, Any], artifact_paths: list[str]) -> str:
    replacements = {
        "Report": corrective_action_report_path(artifact_paths),
        "Target branch": str(scm_state.get("target_branch", "") or scm_state.get("current_branch", "")),
        "Target commit": str(scm_state.get("current_commit", "")),
    }
    body = template_text
    for label, value in replacements.items():
        if value:
            body = re.sub(
                rf"(?m)^- {re.escape(label)}:\s*$",
                f"- {label}: `{value}`",
                body,
            )
    return body


def default_issue_body(repo_root: Path, work_dir: Path) -> str:
    context = read_json(context_file(work_dir, "agent-context.json"), default={}) or {}
    scm_state = read_json(context_file(work_dir, "scm-state.json"), default={}) or {}
    artifact_paths = collect_artifact_paths(work_dir)
    template_path = project_issue_template_path(repo_root, work_dir, scm_state)
    if template_path:
        return fill_project_issue_template(template_path.read_text(encoding="utf-8-sig"), scm_state, artifact_paths)

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


def issue_body_from_args(repo_root: Path, work_dir: Path, args: argparse.Namespace) -> tuple[str, str, str | None]:
    if args.body_file:
        return Path(args.body_file).read_text(encoding="utf-8-sig"), "body-file", str(Path(args.body_file).resolve())

    scm_state = read_json(context_file(work_dir, "scm-state.json"), default={}) or {}
    template_path = project_issue_template_path(repo_root, work_dir, scm_state)
    if template_path:
        return default_issue_body(repo_root, work_dir), "project-template", relative_to_repo(repo_root, template_path)

    return default_issue_body(repo_root, work_dir), "runtime-default", None


def create_issue_with_api(
    github_repo: str,
    title: str,
    body_text: str,
    labels: list[str],
    assignees: list[str],
    settings: dict[str, str],
) -> tuple[str, str | None]:
    owner, repo = github_repo.split("/", 1)
    payload = {
        "title": title,
        "body": body_text,
    }
    if labels:
        payload["labels"] = labels
    if assignees:
        payload["assignees"] = assignees

    data = github_api_json(
        settings,
        "POST",
        f"/repos/{quote(owner, safe='')}/{quote(repo, safe='')}/issues",
        payload,
    )

    issue_url = str(data.get("html_url", ""))
    issue_number = data.get("number")
    if not issue_url and issue_number:
        issue_url = f"https://github.com/{github_repo}/issues/{issue_number}"
    if not issue_url:
        raise RuntimeError("GitHub API issue create failed: response did not include issue URL.")
    if issue_number is None:
        match = ISSUE_URL_RE.search(issue_url)
        issue_number = match.group(1) if match else None
    return issue_url, str(issue_number) if issue_number is not None else None


def manage_issue(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    settings = load_env(repo_root)
    work_dir = work_dir_for_id(repo_root, args.work_id)
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    scm_state = read_json(context_file(work_dir, "scm-state.json"), default={}) or {}
    owner = default_github_owner(settings)
    scm_github_repo = repository_to_github_slug(str(scm_state.get("repository", "")), owner)
    explicit_github_repo = repository_to_github_slug(args.github_repo, owner) if args.github_repo else None
    github_repo = explicit_github_repo or scm_github_repo
    if not github_repo:
        raise ValueError("GitHub repository is required. Run runtime/scm/prepare_repository.py first or set --github-repo.")
    if "/" not in github_repo:
        raise ValueError("GitHub repository must be in owner/name format.")
    explicit_prefix = args.title_prefix or ""
    flow_label = args.flow_label or ""
    if not explicit_prefix and not flow_label:
        explicit_prefix = infer_flow_label(work_dir)
    issue_title, applied_title_prefix = normalize_issue_title(args.title, flow_label, explicit_prefix)
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

    body_text, body_source, template_path = issue_body_from_args(repo_root, work_dir, args)
    issue_id = f"github-issue-{local_timestamp()}"
    report_dir = process_report_dir_for_work_dir(work_dir)
    draft_md = report_dir / f"{issue_id}.md"
    draft_json = report_dir / f"{issue_id}.json"
    write_markdown_bom(draft_md, body_text)

    issue_url = None
    issue_number = None
    status = "draft"
    if args.create:
        issue_url, issue_number = create_issue_with_api(
            github_repo,
            issue_title,
            body_text,
            labels,
            assignees,
            settings,
        )
        status = "created"

    issue_record = {
        "schema_version": "1.0",
        "work_id": args.work_id,
        "github_repo": github_repo,
        "title": issue_title,
        "raw_title": args.title,
        "title_prefix": applied_title_prefix,
        "body_path": relative_to_repo(repo_root, draft_md),
        "body_source": body_source,
        "template_path": template_path,
        "labels": labels,
        "assignees": assignees,
        "status": status,
        "issue_url": issue_url,
        "issue_number": issue_number,
        "created_at": utc_now_iso(),
    }
    write_json(draft_json, issue_record)

    agent_context = read_json(context_file(work_dir, "agent-context.json"), default={}) or {}
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
    write_json(context_file(work_dir, "artifact-index.json"), index)
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
