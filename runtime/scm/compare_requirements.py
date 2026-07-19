from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import (  # noqa: E402
    find_repo_root,
    load_artifact_index,
    local_timestamp,
    read_json,
    relative_to_repo,
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
from runtime.scm.scm_utils import current_branch, current_commit, run_git  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a comparison report between requirements and repository state.")
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--requirements", nargs="*", help="Requirement files. Defaults to requirement artifacts.")
    return parser


def safe_git(args: list[str], cwd: Path) -> str:
    result = run_git(args, cwd)
    if result.returncode != 0:
        return (result.stderr or result.stdout).strip()
    return result.stdout.strip()


def first_lines(path: Path, max_lines: int = 40) -> str:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except Exception as exc:
        return f"Could not read requirement file: {exc}"
    return "\n".join(lines[:max_lines])


def compare_requirements(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = work_dir_for_id(repo_root, args.work_id)
    source_dir = Path(args.source_dir).resolve() if args.source_dir else target_repository_dir_for_work_dir(work_dir)
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")
    if not source_dir.exists():
        raise FileNotFoundError(f"Source repository does not exist: {source_dir}")

    artifact_index = read_json(context_file(work_dir, "artifact-index.json"), default={}) or {}
    requirement_paths = args.requirements or [
        artifact.get("path")
        for artifact in artifact_index.get("artifacts", [])
        if artifact.get("type") == "requirement"
    ]
    requirement_files = [
        (repo_root / path).resolve() if path and not Path(path).is_absolute() else Path(path).resolve()
        for path in requirement_paths
        if path
    ]

    branch = current_branch(source_dir)
    commit = current_commit(source_dir)
    status = safe_git(["status", "--short"], source_dir)
    recent_log = safe_git(["log", "--oneline", "-5"], source_dir)
    file_count = safe_git(["ls-files"], source_dir).splitlines()

    report_name = f"requirement-comparison-{local_timestamp()}"
    report_dir = process_report_dir_for_work_dir(work_dir)
    md_path = report_dir / f"{report_name}.md"
    json_path = report_dir / f"{report_name}.json"

    comparison = {
        "schema_version": "1.0",
        "work_id": args.work_id,
        "source_dir": relative_to_repo(repo_root, source_dir),
        "branch": branch,
        "commit": commit,
        "requirement_files": [relative_to_repo(repo_root, path) for path in requirement_files],
        "status_short": status,
        "recent_log": recent_log,
        "tracked_file_count": len(file_count),
        "created_at": utc_now_iso(),
    }
    write_json(json_path, comparison)

    lines = [
        "# Requirement Comparison Report",
        "",
        f"- Work ID: `{args.work_id}`",
        f"- Source: `{relative_to_repo(repo_root, source_dir)}`",
        f"- Branch: `{branch}`",
        f"- Commit: `{commit}`",
        f"- Created at: `{comparison['created_at']}`",
        "",
        "## Requirement Files",
        "",
    ]
    if requirement_files:
        for path in requirement_files:
            lines.append(f"- `{relative_to_repo(repo_root, path)}`")
    else:
        lines.append("- No requirement artifact was found.")
    lines.extend(
        [
            "",
            "## Repository State",
            "",
            "### Status",
            "",
            "```text",
            status or "clean",
            "```",
            "",
            "### Recent Commits",
            "",
            "```text",
            recent_log or "no commits",
            "```",
            "",
            "## Requirement Excerpts",
            "",
        ]
    )
    for path in requirement_files:
        lines.extend(
            [
                f"### {relative_to_repo(repo_root, path)}",
                "",
                "```markdown",
                first_lines(path),
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Comparison Notes",
            "",
            "- Confirm whether the current repository branch already satisfies any requirement items.",
            "- Identify files and components likely affected by the requested change.",
            "- Use this report as the input for GitHub Issue creation.",
        ]
    )
    write_markdown_bom(md_path, "\n".join(lines))

    agent_context = read_json(context_file(work_dir, "agent-context.json"), default={}) or {}
    project_name = agent_context.get("project", {}).get("name", args.work_id)
    workflow_name = agent_context.get("workflow", {}).get("name", "")
    index = load_artifact_index(work_dir, project_name, workflow_name)
    now = utc_now_iso()
    for artifact_id, title, path in [
        ("REQ-COMPARE-MD", md_path.name, md_path),
        ("REQ-COMPARE-JSON", json_path.name, json_path),
    ]:
        upsert_artifact(
            index,
            {
                "id": f"{artifact_id}-{report_name}",
                "title": title,
                "path": relative_to_repo(repo_root, path),
                "type": "report",
                "status": "draft",
                "owner_agent": "runtime-scm",
                "created_at": now,
                "updated_at": now,
                "depends_on": [relative_to_repo(repo_root, item) for item in requirement_files],
                "consumed_by": ["runtime-github"],
                "summary": "Comparison between requirement documents and repository state.",
                "unresolved_items": [],
            },
        )
    write_json(context_file(work_dir, "artifact-index.json"), index)
    return {
        "work_id": args.work_id,
        "markdown_report": relative_to_repo(repo_root, md_path),
        "json_report": relative_to_repo(repo_root, json_path),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = compare_requirements(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

