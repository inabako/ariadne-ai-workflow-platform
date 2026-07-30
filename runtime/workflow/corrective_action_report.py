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
from runtime.common import ensure_work_tree, find_repo_root, read_json, relative_to_repo, slugify, utc_now_iso, write_json  # noqa: E402
from runtime.constants.schemas import CORRECTIVE_ACTION_REPORT_SCHEMA  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    context_dir_for_work_dir,
    context_file,
    manifest_path_for_work_dir,
    resolve_work_dir as workspace_resolve_work_dir,
    work_dir_for_id,
)
from runtime.workflow.context_first import register_context  # noqa: E402
from runtime.workflow import work_cleanup_hint  # noqa: E402


FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
FINDING_ROW_RE = re.compile(r"^\|\s*(?:CAR|F|CA|RISK|DOC|TEST)?[-_]?\d+", re.IGNORECASE)


def branch_to_work_id(branch_name: str) -> str:
    value = branch_name.replace("\\", "/").strip("/")
    return slugify(value.replace("/", "-"))


def parse_scalar(value: str) -> str | list[str]:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("'\"") for item in value.strip("[]").split(",") if item.strip()]
    return value.strip("'\"")


def parse_front_matter(text: str) -> dict[str, Any]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}
    metadata: dict[str, Any] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            index += 1
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value:
            metadata[key] = parse_scalar(value)
            index += 1
            continue
        items: list[str] = []
        index += 1
        while index < len(lines):
            item = lines[index].strip()
            if not item.startswith("- "):
                break
            items.append(item[2:].strip().strip("'\""))
            index += 1
        metadata[key] = items if items else ""
    return metadata


def count_section_items(text: str, heading: str) -> int:
    marker = f"## {heading}".lower()
    lines = text.splitlines()
    in_section = False
    count = 0
    for line in lines:
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("## "):
            if in_section:
                break
            in_section = lower == marker
            continue
        if not in_section:
            continue
        if stripped.startswith("- ") or FINDING_ROW_RE.match(stripped):
            count += 1
    return count


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    raw = Path(value)
    return raw if raw.is_absolute() else repo_root / raw


def resolve_work_dir(repo_root: Path, args: argparse.Namespace) -> tuple[str, Path]:
    if args.work_dir:
        work_dir = workspace_resolve_work_dir(repo_root, args.work_id or "", args.work_dir)
        return args.work_id or work_dir.name, work_dir
    work_id = args.work_id or branch_to_work_id(args.target_branch)
    return work_id, workspace_resolve_work_dir(repo_root, work_id)


def build_report_context(repo_root: Path, args: argparse.Namespace, report_path: Path) -> dict[str, Any]:
    report_text = report_path.read_text(encoding="utf-8-sig", errors="replace") if report_path.exists() else ""
    front_matter = parse_front_matter(report_text)
    repository = args.repository or str(front_matter.get("repository", ""))
    target_branch = args.target_branch or str(front_matter.get("branch", ""))
    target_commit = str(front_matter.get("commit", ""))
    report_rel = relative_to_repo(repo_root, report_path)
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "corrective-action-report",
        "architecture": "context-first",
        "created_at": utc_now_iso(),
        "repository": repository,
        "target_branch": target_branch,
        "target_commit": target_commit,
        "status": str(front_matter.get("status", "draft")),
        "report_path": report_rel,
        "report_filename": report_path.name,
        "report_exists": report_path.exists(),
        "rag_candidate": True,
        "rag_source_path": report_rel,
        "docs_candidate": False,
        "finding_summary": {
            "finding_count": count_section_items(report_text, "Findings"),
            "rag_capture_candidate_count": count_section_items(report_text, "RAG Capture Candidates"),
        },
        "front_matter": front_matter,
        "source": {
            "schema": CORRECTIVE_ACTION_REPORT_SCHEMA,
            "registered_by": "runtime-workflow-corrective-action-report",
        },
    }


def register_report_context(repo_root: Path, work_dir: Path, work_id: str, context_path: Path) -> None:
    register_context(
        repo_root,
        work_dir,
        work_id=work_id,
        context_type="corrective-action-report",
        path=context_path,
        required=False,
        generated_by="corrective-action-report",
        owner="workflow",
        schema=CORRECTIVE_ACTION_REPORT_SCHEMA,
    )


def run_register(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    report_path = resolve_repo_path(repo_root, args.report_path).resolve()
    work_id, work_dir = resolve_work_dir(repo_root, args)
    if work_dir == work_dir_for_id(repo_root, work_id):
        ensure_work_tree(repo_root, work_id)
    else:
        (context_dir_for_work_dir(work_dir)).mkdir(parents=True, exist_ok=True)
    context_path = context_file(work_dir, "corrective-action-report.json")
    context = build_report_context(repo_root, args, report_path)
    write_json(context_path, context)
    register_report_context(repo_root, work_dir, work_id, context_path)
    work_cleanup_hint.register_long_lived_artifact(
        repo_root,
        work_dir,
        work_id=work_id,
        workflow_name="corrective-action-report",
        artifact_id="CORRECTIVE-ACTION-REPORT",
        title=report_path.name,
        path=report_path,
        artifact_type="rag-source",
        status=str(context.get("status", "draft")),
        owner_agent="corrective-action-report",
        summary="Corrective action report RAG source.",
    )
    work_cleanup = work_cleanup_hint.record(repo_root, work_dir, work_id)
    return {
        "status": "registered" if context["report_exists"] else "registered-missing-report",
        "work_id": work_id,
        "work_dir": relative_to_repo(repo_root, work_dir),
        "context_path": relative_to_repo(repo_root, context_path),
        "report_path": context["report_path"],
        "manifest_path": relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir)),
        "work_cleanup": work_cleanup,
        "next_action": work_cleanup_hint.next_action(
            work_cleanup,
            reason="Approved corrective action report Knowledge source is available in the long-lived knowledge area.",
        ),
    }


def run_show(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_id, work_dir = resolve_work_dir(repo_root, args)
    context_path = context_file(work_dir, "corrective-action-report.json")
    context = read_json(context_path, default={})
    return {
        "status": "ok" if context else "missing",
        "work_id": work_id,
        "context_path": relative_to_repo(repo_root, context_path),
        "context": context,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Register corrective action report output as Context First artifact.")
    parser.add_argument("--repo-root", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="Register a corrective action report artifact in context-manifest.")
    register.add_argument("--report-path", required=True)
    register.add_argument("--repository", default="")
    register.add_argument("--target-branch", default="")
    register.add_argument("--work-id", default="")
    register.add_argument("--work-dir", default="")
    register.set_defaults(handler=run_register)

    show = sub.add_parser("show", help="Show corrective action report context for a work area.")
    show.add_argument("--target-branch", default="")
    show.add_argument("--work-id", default="")
    show.add_argument("--work-dir", default="")
    show.set_defaults(handler=run_show)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") not in {"failed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
