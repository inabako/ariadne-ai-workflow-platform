from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, local_timestamp, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402


RAG_SOURCE_DIRS = ["process-report", "test-specifications", "test-evidence"]
EXPECTED_TEST_SPEC_FILES = ["unit-test-cases.md", "integration-test-cases.md", "human-check-list.md"]
SCAFFOLD_FILE_NAMES = {"README.md"}
EVIDENCE_SCAFFOLD = {
    "": "# Issue Evidence\n\nStore durable test specifications and evidence for this issue here.\n",
    "test_specifications": (
        "# Test Specifications\n\n"
        "Store test case tables and test specifications here.\n\n"
        "Recommended files:\n\n"
        "- `unit-test-cases.md`\n"
        "- `integration-test-cases.md`\n"
        "- `human-check-list.md`\n"
    ),
    "ut": "# Unit Test Evidence\n\nStore unit test commands, logs, and results here.\n",
    "integration": "# Integration Evidence\n\nStore integration evidence under qtest, manual, and startup subdirectories.\n",
    "integration/qtest": "# QTest Evidence\n\nStore PyQt / Qt QTest commands, logs, and results here.\n",
    "integration/manual": "# Manual Integration Evidence\n\nStore manual integration check steps, observations, and results here.\n",
    "integration/startup": "# Startup Evidence\n\nStore startup commands, logs, external I/O notes, and results here.\n",
    "human_check": "# Human Check Evidence\n\nStore human confirmation items, approver, date, and results here.\n",
}
DOCS_CANDIDATE_KEYWORDS = [
    "Docker",
    "UDP Broadcast",
    "MSYS2",
    "Docker Desktop",
    "Simulator",
    "Fault Injection",
    "Packet Monitor",
    "PyQt6",
    "QTimer",
    "Thread",
    "camera",
    "カメラ",
    "テストエビデンス",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare knowledge-capture reports for a completed issue workflow.")
    parser.add_argument("--issue", required=True, help="Issue work id such as issue-11.")
    parser.add_argument("--repository", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--base-work-id", default="", help="Base work folder such as develop. Used for base process-report preservation guidance.")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--source-dir", default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def list_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(item for item in path.rglob("*") if item.is_file())


def is_scaffold_file(path: Path) -> bool:
    return path.name in SCAFFOLD_FILE_NAMES


def path_status(path: Path) -> dict[str, Any]:
    files = list_files(path)
    evidence_files = [path for path in files if not is_scaffold_file(path)]
    return {
        "path": path,
        "exists": path.exists(),
        "file_count": len(files),
        "evidence_file_count": len(evidence_files),
        "files": files,
        "evidence_files": evidence_files,
    }


def file_status(path: Path) -> dict[str, Any]:
    return {
        "path": path,
        "exists": path.exists() and path.is_file(),
        "size": path.stat().st_size if path.exists() and path.is_file() else 0,
    }


def read_text_sample(path: Path, max_chars: int = 1200) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")[:max_chars]
    except OSError:
        return ""


def markdown_path_list(repo_root: Path, files: list[Path], limit: int = 30) -> str:
    if not files:
        return "- None"
    lines = [f"- `{relative_to_repo(repo_root, path)}`" for path in files[:limit]]
    remaining = len(files) - limit
    if remaining > 0:
        lines.append(f"- ... {remaining} more")
    return "\n".join(lines)


def find_docs_candidates(files: list[Path]) -> list[dict[str, str]]:
    candidates: dict[str, dict[str, str]] = {}
    for path in files:
        text = read_text_sample(path, max_chars=6000)
        for keyword in DOCS_CANDIDATE_KEYWORDS:
            if keyword.lower() in text.lower():
                candidates.setdefault(
                    keyword,
                    {
                        "topic": keyword,
                        "reason": "Repeated or operationally useful knowledge appeared in workflow evidence.",
                        "source_path": str(path),
                    },
                )
    return sorted(candidates.values(), key=lambda item: item["topic"].lower())


def write_markdown(path: Path, text: str, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def scaffold_evidence_docs(docs_root: Path, dry_run: bool) -> list[dict[str, Any]]:
    scaffold_results = []
    for relative_dir, readme_text in EVIDENCE_SCAFFOLD.items():
        directory = docs_root / relative_dir if relative_dir else docs_root
        readme_path = directory / "README.md"
        existed = readme_path.exists()
        if not dry_run:
            directory.mkdir(parents=True, exist_ok=True)
            if not existed:
                readme_path.write_text(readme_text.rstrip() + "\n", encoding="utf-8")
        scaffold_results.append(
            {
                "path": directory,
                "readme": readme_path,
                "created": not existed and not dry_run,
                "planned": not existed and dry_run,
            }
        )
    return scaffold_results


def latest_issue_title(repo_root: Path, work_dir: Path, base_work_id: str = "") -> str:
    issue_records = sorted((work_dir / "process-report").glob("github-issue-*.json"))
    if base_work_id:
        issue_records.extend(sorted((repo_root / "work" / base_work_id / "process-report").glob("github-issue-*.json")))
    for path in reversed(issue_records):
        record = read_json(path, default={}) or {}
        title = str(record.get("title", "")).strip()
        if title:
            return title
    return ""


def build_pr_title(issue: str, repository: str, issue_title: str = "") -> str:
    if issue_title:
        return issue_title
    repo_label = repository or "target repository"
    return f"{issue}: finalize corrective action evidence for {repo_label}"


def build_pr_description(issue: str, repository: str, branch: str, docs_status: dict[str, Any]) -> str:
    return f"""# Pull Request Description

## Issue

`{issue}`

## Repository / Branch

| Item | Value |
| --- | --- |
| Repository | {repository or "unknown"} |
| Branch | {branch or "unknown"} |
| PR Title Source | GitHub Issue title when available |

## Improvement Purpose

Finalize the corrective action implementation with traceable test specifications, evidence, and knowledge-capture artifacts.

## Changes

- Corrective implementation completed in the issue branch.
- Test specifications and evidence prepared for unit and integration / connectivity checks.
- PR materials and knowledge-capture report generated.

## Change Sequence

```mermaid
sequenceDiagram
  participant Issue as GitHub Issue
  participant Branch as feature/issue branch
  participant Tests as Tests / Evidence
  participant PR as Pull Request
  participant Develop as develop
  Issue->>Branch: create linked issue branch
  Branch->>Tests: implement change and run tests
  Tests->>Branch: commit source, test specs, and evidence
  Branch->>PR: push issue branch
  PR->>Develop: open pull request to develop
```

## Tests

- Test specification docs directory: `{docs_status["test_specifications"]["relative_path"]}`
- Unit test evidence directory: `{docs_status["ut"]["relative_path"]}`
- Integration / connectivity evidence directory: `{docs_status["integration"]["relative_path"]}`
- Human check evidence directory: `{docs_status["human_check"]["relative_path"]}`

## Human Confirmation

- Confirm the evidence documents are present under `docs/evidence/{issue}/`.
- Confirm the integration / connectivity result is accepted.
- Confirm this branch is ready to push and open / merge the pull request.
"""


def build_merge_comment(issue: str) -> str:
    return f"""# Merge Comment

Merged corrective action for `{issue}` after confirming:

- PR title and description were prepared.
- Test specifications were stored under `docs/evidence/{issue}/test_specifications`.
- Unit test evidence was stored under `docs/evidence/{issue}/ut`.
- Integration / connectivity evidence was stored under `docs/evidence/{issue}/integration`.
- Human check evidence was stored under `docs/evidence/{issue}/human_check` when required.
- Human integration check was accepted.
- Knowledge-capture report identified RAG and docs candidates.
"""


def knowledge_capture(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = repo_root / "work" / args.issue
    close_target = repo_root / "work" / "close" / args.issue
    if not work_dir.exists() and close_target.exists():
        work_dir = close_target
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {repo_root / 'work' / args.issue}")

    scm_state = read_json(work_dir / "context" / "scm-state.json", default={}) or {}
    source_dir = Path(args.source_dir).resolve() if args.source_dir else work_dir / "source" / "repository"
    repository = args.repository or scm_state.get("github_repo") or scm_state.get("repository") or ""
    branch = args.branch or scm_state.get("working_branch") or scm_state.get("current_branch") or ""
    base_work_id = args.base_work_id or str(scm_state.get("base_work_id", ""))

    process_report_dir = work_dir / "process-report"
    docs_root = source_dir / "docs" / "evidence" / args.issue
    scaffold_status = scaffold_evidence_docs(docs_root, args.dry_run)
    docs_status = {
        "test_specifications": path_status(docs_root / "test_specifications"),
        "ut": path_status(docs_root / "ut"),
        "integration": path_status(docs_root / "integration"),
        "human_check": path_status(docs_root / "human_check"),
    }
    test_spec_file_status = {
        name: file_status(docs_root / "test_specifications" / name)
        for name in EXPECTED_TEST_SPEC_FILES
    }
    for status in docs_status.values():
        status["relative_path"] = relative_to_repo(repo_root, status["path"])
        status["path"] = status["relative_path"]
        status["files"] = [relative_to_repo(repo_root, path) for path in status["files"]]
        status["evidence_files"] = [relative_to_repo(repo_root, path) for path in status["evidence_files"]]
    for status in test_spec_file_status.values():
        status["relative_path"] = relative_to_repo(repo_root, status["path"])
        status["path"] = status["relative_path"]

    scaffold_status = [
        {
            "path": relative_to_repo(repo_root, item["path"]),
            "readme": relative_to_repo(repo_root, item["readme"]),
            "created": item["created"],
            "planned": item["planned"],
        }
        for item in scaffold_status
    ]

    rag_sources: dict[str, dict[str, Any]] = {}
    rag_files: list[Path] = []
    for dirname in RAG_SOURCE_DIRS:
        status = path_status(work_dir / dirname)
        rag_sources[dirname] = {
            "path": relative_to_repo(repo_root, status["path"]),
            "exists": status["exists"],
            "file_count": status["file_count"],
            "files": [relative_to_repo(repo_root, path) for path in status["files"]],
        }
        rag_files.extend(status["files"])

    docs_candidates = find_docs_candidates(rag_files)
    for candidate in docs_candidates:
        candidate["source_path"] = relative_to_repo(repo_root, Path(candidate["source_path"]))
    archive_status = "already-archived" if work_dir.resolve() == close_target.resolve() else ("ready" if not close_target.exists() else "blocked-target-exists")
    base_work_dir = repo_root / "work" / base_work_id if base_work_id else None
    base_process_report_dir = base_work_dir / "process-report" if base_work_dir else None
    base_preserve_dir = close_target / "process-report" / f"base-work-{base_work_id}" if base_work_id else None
    base_work_status = {
        "base_work_id": base_work_id,
        "source": relative_to_repo(repo_root, base_process_report_dir) if base_process_report_dir else "",
        "preserve_target": relative_to_repo(repo_root, base_preserve_dir) if base_preserve_dir else "",
        "source_exists": bool(base_process_report_dir and base_process_report_dir.exists()),
        "preserve_target_exists": bool(base_preserve_dir and base_preserve_dir.exists()),
        "action": "copy-process-report-then-delete-base-work" if base_work_id else "not_configured",
    }

    timestamp = utc_now_iso()
    output_paths = {
        "pull_request_title": process_report_dir / "pull-request-title.md",
        "pull_request_description": process_report_dir / "pull-request-description.md",
        "merge_comment": process_report_dir / "merge-comment.md",
        "knowledge_capture_report": process_report_dir / "knowledge-capture-report.md",
        "knowledge_capture_json": process_report_dir / f"knowledge-capture-{local_timestamp()}.json",
    }

    issue_title = latest_issue_title(repo_root, work_dir, base_work_id)
    title = build_pr_title(args.issue, str(repository), issue_title)
    write_markdown(output_paths["pull_request_title"], title, args.dry_run)
    write_markdown(output_paths["pull_request_description"], build_pr_description(args.issue, str(repository), str(branch), docs_status), args.dry_run)
    write_markdown(output_paths["merge_comment"], build_merge_comment(args.issue), args.dry_run)

    report = f"""# Knowledge Capture Report

## Issue

`{args.issue}`

## Summary

Finalization and knowledge recovery package for `{repository or "unknown repository"}` / `{branch or "unknown branch"}`.

## PR Documents

- `{relative_to_repo(repo_root, output_paths["pull_request_title"])}`
- `{relative_to_repo(repo_root, output_paths["pull_request_description"])}`
- `{relative_to_repo(repo_root, output_paths["merge_comment"])}`

## Test Evidence Docs

| Area | Path | Exists | File Count | Evidence File Count |
| --- | --- | --- | --- | --- |
| Test Specifications | `{docs_status["test_specifications"]["relative_path"]}` | {docs_status["test_specifications"]["exists"]} | {docs_status["test_specifications"]["file_count"]} | {docs_status["test_specifications"]["evidence_file_count"]} |
| Unit Test | `{docs_status["ut"]["relative_path"]}` | {docs_status["ut"]["exists"]} | {docs_status["ut"]["file_count"]} | {docs_status["ut"]["evidence_file_count"]} |
| Integration / Connectivity Test | `{docs_status["integration"]["relative_path"]}` | {docs_status["integration"]["exists"]} | {docs_status["integration"]["file_count"]} | {docs_status["integration"]["evidence_file_count"]} |
| Human Check | `{docs_status["human_check"]["relative_path"]}` | {docs_status["human_check"]["exists"]} | {docs_status["human_check"]["file_count"]} | {docs_status["human_check"]["evidence_file_count"]} |

## Expected Test Case Tables

| File | Exists | Size |
| --- | --- | --- |
| `{test_spec_file_status["unit-test-cases.md"]["relative_path"]}` | {test_spec_file_status["unit-test-cases.md"]["exists"]} | {test_spec_file_status["unit-test-cases.md"]["size"]} |
| `{test_spec_file_status["integration-test-cases.md"]["relative_path"]}` | {test_spec_file_status["integration-test-cases.md"]["exists"]} | {test_spec_file_status["integration-test-cases.md"]["size"]} |
| `{test_spec_file_status["human-check-list.md"]["relative_path"]}` | {test_spec_file_status["human-check-list.md"]["exists"]} | {test_spec_file_status["human-check-list.md"]["size"]} |

## RAG Candidates

{markdown_path_list(repo_root, rag_files)}

## Docs Candidates

{markdown_path_list(repo_root, [Path(item["source_path"]) for item in docs_candidates]) if docs_candidates else "- None"}

## Archive

| Item | Value |
| --- | --- |
| Source | `work/{args.issue}` |
| Target | `work/close/{args.issue}` |
| Status | {archive_status} |

## Base Work Reset

| Item | Value |
| --- | --- |
| Base Work ID | `{base_work_status["base_work_id"] or "not configured"}` |
| Preserve Source | `{base_work_status["source"] or "not configured"}` |
| Preserve Target | `{base_work_status["preserve_target"] or "not configured"}` |
| Source Exists | {base_work_status["source_exists"]} |
| Preserve Target Exists | {base_work_status["preserve_target_exists"]} |
| Action | {base_work_status["action"]} |

## Human Action

- Confirm docs evidence is stored under `docs/evidence/{args.issue}/test_specifications`, `docs/evidence/{args.issue}/ut`, `docs/evidence/{args.issue}/integration`, and `docs/evidence/{args.issue}/human_check` when required.
- Push `feature/{args.issue}` only after docs evidence is committed in the feature branch.
- Run RAG build for selected candidates after approval.
- Preserve `work/<base-work-id>/process-report` under `work/close/{args.issue}/process-report/base-work-<base-work-id>` before deleting the base work folder.
- Move `work/{args.issue}` to `work/close/{args.issue}` after approval.
"""
    write_markdown(output_paths["knowledge_capture_report"], report, args.dry_run)

    result = {
        "schema_version": "1.0",
        "issue": args.issue,
        "repository": repository,
        "branch": branch,
        "issue_title": issue_title,
        "pull_request_title": title,
        "generated_at": timestamp,
        "dry_run": bool(args.dry_run),
        "pr_documents": {key: relative_to_repo(repo_root, path) for key, path in output_paths.items() if key != "knowledge_capture_json"},
        "scaffold_status": scaffold_status,
        "docs_status": docs_status,
        "test_specification_files": test_spec_file_status,
        "rag_sources": rag_sources,
        "rag_candidate_count": len(rag_files),
        "docs_candidates": docs_candidates,
        "archive": {
            "source": f"work/{args.issue}",
            "target": f"work/close/{args.issue}",
            "status": archive_status,
        },
        "base_work_reset": base_work_status,
        "human_actions": [
            f"Push {branch or 'feature/issue-XXX'} after docs evidence is committed.",
            f"Run RAG build for approved candidates from work/{args.issue}.",
            "Preserve base work process-report before deleting the base work folder.",
            f"Move work/{args.issue} to work/close/{args.issue} after approval.",
        ],
    }
    if not args.dry_run:
        write_json(output_paths["knowledge_capture_json"], result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = knowledge_capture(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
