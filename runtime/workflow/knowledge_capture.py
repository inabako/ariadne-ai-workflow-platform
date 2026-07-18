from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, local_timestamp, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.schemas import KNOWLEDGE_CAPTURE_SCHEMA  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    process_report_dir_for_work_dir,
    target_repository_dir_for_work_dir,
    work_dir_for_id,
)
from runtime.workflow.context_first import (  # noqa: E402
    context_entry,
    context_path,
    load_test_evidence_context,
    load_manifest,
    manifest_path_for_work_dir,
    register_context,
)


RAG_SOURCE_DIRS = ["process-report", "test-specifications", "test-evidence"]
EXPECTED_TEST_SPEC_FILES = ["unit-test-cases.md", "integration-test-cases.md", "human-check-list.md"]
SCAFFOLD_FILE_NAMES = {"README.md"}
EVIDENCE_SCAFFOLD = {
    "": "# Issue Evidence\n\nこのIssueの再利用可能なtest specificationとevidenceを保存します。\n",
    "test_specifications": (
        "# Test Specifications\n\n"
        "test case tableとtest specificationを保存します。\n\n"
        "推奨file:\n\n"
        "- `unit-test-cases.md`\n"
        "- `integration-test-cases.md`\n"
        "- `human-check-list.md`\n"
    ),
    "ut": "# Unit Test Evidence\n\nunit testのcommand、log、resultを保存します。\n",
    "integration": "# Integration Evidence\n\nintegration evidenceはqtest、manual、startupのsubdirectoryへ分けて保存します。\n",
    "integration/qtest": "# QTest Evidence\n\nPyQt / Qt QTestのcommand、log、resultを保存します。\n",
    "integration/manual": "# Manual Integration Evidence\n\n手動integration checkの手順、観察結果、判定を保存します。\n",
    "integration/startup": "# Startup Evidence\n\nstartup command、log、external I/O note、resultを保存します。\n",
    "human_check": "# Human Check Evidence\n\n人間確認項目、承認者、日付、結果を保存します。\n",
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
    parser.add_argument(
        "--allow-legacy-scm-fallback",
        action="store_true",
        help="Allow old work folders without manifest scm-state. Close archives still allow fallback automatically.",
    )
    return parser


def close_archive_target(repo_root: Path, issue: str) -> Path:
    return work_dir_for_id(repo_root, "close") / "improvement" / issue


def list_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted(item for item in path.rglob("*") if item.is_file())


def is_scaffold_file(path: Path) -> bool:
    return path.name in SCAFFOLD_FILE_NAMES


def path_status(path: Path) -> dict[str, Any]:
    files = list_files(path)
    evidence_files = [item for item in files if not is_scaffold_file(item)]
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
        return "- なし"
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
                        "reason": "Workflow evidenceに、再利用しやすい運用知識が含まれているため。",
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
    issue_records = sorted(process_report_dir_for_work_dir(work_dir).glob("github-issue-*.json"))
    if base_work_id:
        issue_records.extend(sorted(process_report_dir_for_work_dir(work_dir_for_id(repo_root, base_work_id)).glob("github-issue-*.json")))
    for path in reversed(issue_records):
        record = read_json(path, default={}) or {}
        title = str(record.get("title", "")).strip()
        if title:
            return title
    return ""


def read_context_with_fallback(
    repo_root: Path,
    work_dir: Path,
    *,
    context_type: str,
    fallback_relative_path: str,
    require_manifest: bool = False,
    allow_legacy_fallback: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_path = manifest_path_for_work_dir(work_dir)
    manifest_exists = manifest_path.exists()
    if manifest_exists:
        manifest = load_manifest(work_dir)
        entry = context_entry(manifest, context_type)
        if entry:
            path = context_path(repo_root, entry)
            data = read_json(path, default={}) or {}
            return data if isinstance(data, dict) else {}, {
                "context_type": context_type,
                "mode": "manifest",
                "path": relative_to_repo(repo_root, path),
                "manifest_path": relative_to_repo(repo_root, manifest_path),
                "found": path.exists(),
            }
    fallback_path = work_dir / fallback_relative_path
    if require_manifest and not allow_legacy_fallback:
        reason = "context-manifest missing" if not manifest_exists else f"{context_type} not registered in context-manifest"
        raise RuntimeError(
            f"Context First gate: knowledge-capture requires manifest {context_type}. "
            f"{reason}. Use --allow-legacy-scm-fallback only for old work folders, or run close archive fallback for archived work: {fallback_path}"
        )
    data = read_json(fallback_path, default={}) or {}
    return data if isinstance(data, dict) else {}, {
        "context_type": context_type,
        "mode": "fallback",
        "path": relative_to_repo(repo_root, fallback_path),
        "manifest_path": relative_to_repo(repo_root, manifest_path) if manifest_exists else "",
        "found": fallback_path.exists(),
        "reason": "context-manifest missing or context entry not registered",
    }


def build_pr_title(issue: str, repository: str, issue_title: str = "") -> str:
    if issue_title:
        return issue_title
    repo_label = repository or "target repository"
    return f"{issue}: corrective action evidenceを確定する for {repo_label}"


def build_pr_description(issue: str, repository: str, branch: str, docs_status: dict[str, Any]) -> str:
    return f"""# Pull Request説明

## Issue

`{issue}`

## Repository / Branch

| Item | Value |
| --- | --- |
| Repository | {repository or "unknown"} |
| Branch | {branch or "unknown"} |
| PR Title Source | GitHub Issue titleが取得できる場合はそれを使用 |

## 改善目的

追跡可能なtest specification、evidence、knowledge-capture artifactとともに、corrective action implementationを完了状態にします。

## 変更内容

- issue branchでcorrective implementationを完了。
- unitおよびintegration / connectivity check向けのtest specificationとevidenceを準備。
- PR資料とknowledge-capture reportを生成。

## 変更の流れ

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

## Test

- Test specification docs directory: `{docs_status["test_specifications"]["relative_path"]}`
- Unit test evidence directory: `{docs_status["ut"]["relative_path"]}`
- Integration / connectivity evidence directory: `{docs_status["integration"]["relative_path"]}`
- Human check evidence directory: `{docs_status["human_check"]["relative_path"]}`

## Human Confirmation

- `docs/evidence/{issue}/` 配下にevidence documentsが存在することを確認する。
- integration / connectivity resultを承認できることを確認する。
- このbranchをpushし、pull requestをopen / mergeできる状態であることを確認する。
"""


def build_merge_comment(issue: str) -> str:
    return f"""# Merge Comment

`{issue}` のcorrective actionについて、次を確認した上でmergeしました。

- PR titleとdescriptionを準備済み。
- Test specificationを `docs/evidence/{issue}/test_specifications` に保存済み。
- Unit test evidenceを `docs/evidence/{issue}/ut` に保存済み。
- Integration / connectivity evidenceを `docs/evidence/{issue}/integration` に保存済み。
- 必要な場合、Human check evidenceを `docs/evidence/{issue}/human_check` に保存済み。
- Human integration checkを承認済み。
- Knowledge-capture reportでRAG候補とdocs候補を整理済み。
"""


def relative_status(repo_root: Path, status: dict[str, Any]) -> dict[str, Any]:
    status["relative_path"] = relative_to_repo(repo_root, status["path"])
    status["path"] = status["relative_path"]
    if "files" in status:
        status["files"] = [relative_to_repo(repo_root, path) for path in status["files"]]
    if "evidence_files" in status:
        status["evidence_files"] = [relative_to_repo(repo_root, path) for path in status["evidence_files"]]
    return status


def knowledge_capture(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_dir = work_dir_for_id(repo_root, args.issue)
    close_target = close_archive_target(repo_root, args.issue)
    if not work_dir.exists() and close_target.exists():
        work_dir = close_target
    if not work_dir.exists():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir_for_id(repo_root, args.issue)}")

    archive_mode = work_dir.resolve() == close_target.resolve()
    scm_state, scm_resolution = read_context_with_fallback(
        repo_root,
        work_dir,
        context_type="scm-state",
        fallback_relative_path="context/scm-state.json",
        require_manifest=not archive_mode,
        allow_legacy_fallback=archive_mode or bool(getattr(args, "allow_legacy_scm_fallback", False)),
    )
    test_evidence_context = load_test_evidence_context(repo_root, work_dir)
    source_dir = Path(args.source_dir).resolve() if args.source_dir else target_repository_dir_for_work_dir(work_dir)
    repository = args.repository or scm_state.get("github_repo") or scm_state.get("repository") or ""
    branch = args.branch or scm_state.get("working_branch") or scm_state.get("current_branch") or ""
    base_work_id = args.base_work_id or str(scm_state.get("base_work_id", ""))

    process_report_dir = process_report_dir_for_work_dir(work_dir)
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
    for key, status in docs_status.items():
        docs_status[key] = relative_status(repo_root, status)
    for key, status in test_spec_file_status.items():
        test_spec_file_status[key] = relative_status(repo_root, status)

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

    archive_status = "already-archived" if work_dir.resolve() == close_target.resolve() else "report-only-ready"
    base_work_dir = work_dir_for_id(repo_root, base_work_id) if base_work_id else None
    base_process_report_dir = process_report_dir_for_work_dir(base_work_dir) if base_work_dir else None
    base_archive_target = close_target if base_work_id else None
    base_work_status = {
        "base_work_id": base_work_id,
        "source": relative_to_repo(repo_root, base_process_report_dir) if base_process_report_dir else "",
        "archive_target": relative_to_repo(repo_root, base_archive_target) if base_archive_target else "",
        "source_exists": bool(base_process_report_dir and base_process_report_dir.exists()),
        "archive_target_exists": bool(base_archive_target and base_archive_target.exists()),
        "action": "summarize-base-process-report-links-then-delete-base-work" if base_work_id else "not_configured",
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

## 要約

`{repository or "unknown repository"}` / `{branch or "unknown branch"}` のfinalizationとknowledge recovery packageです。

## PR資料

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

## 想定Test Case Table

| File | Exists | Size |
| --- | --- | --- |
| `{test_spec_file_status["unit-test-cases.md"]["relative_path"]}` | {test_spec_file_status["unit-test-cases.md"]["exists"]} | {test_spec_file_status["unit-test-cases.md"]["size"]} |
| `{test_spec_file_status["integration-test-cases.md"]["relative_path"]}` | {test_spec_file_status["integration-test-cases.md"]["exists"]} | {test_spec_file_status["integration-test-cases.md"]["size"]} |
| `{test_spec_file_status["human-check-list.md"]["relative_path"]}` | {test_spec_file_status["human-check-list.md"]["exists"]} | {test_spec_file_status["human-check-list.md"]["size"]} |

## RAG候補

{markdown_path_list(repo_root, rag_files)}

## Docs候補

{markdown_path_list(repo_root, [Path(item["source_path"]) for item in docs_candidates]) if docs_candidates else "- なし"}

## Report-only Close Archive

| Item | Value |
| --- | --- |
| Source | `work/{args.issue}` |
| Target | `work/close/improvement/{args.issue}` |
| Status | {archive_status} |
| Policy | source checkout、`.git`、`.venv`、cache、build artifactsは保持しない |

Recommended command:

```powershell
uv run --project runtime python runtime/common/ctl.py --repo-root . close-archive prepare `
  --issue {args.issue}

uv run --project runtime python runtime/common/ctl.py --repo-root . close-archive audit `
  --issue {args.issue}
```

## Base Work Reset

| Item | Value |
| --- | --- |
| Base Work ID | `{base_work_status["base_work_id"] or "not configured"}` |
| Preserve Source | `{base_work_status["source"] or "not configured"}` |
| Archive Target | `{base_work_status["archive_target"] or "not configured"}` |
| Source Exists | {base_work_status["source_exists"]} |
| Archive Target Exists | {base_work_status["archive_target_exists"]} |
| Action | {base_work_status["action"]} |

## Context First Test Evidence

| Item | Value |
| --- | --- |
| Status | {test_evidence_context["status"]} |
| Count | {test_evidence_context["count"]} |

## Human Action

- docs evidenceが `docs/evidence/{args.issue}/test_specifications`, `docs/evidence/{args.issue}/ut`, `docs/evidence/{args.issue}/integration`, 必要に応じて `docs/evidence/{args.issue}/human_check` に保存されていることを確認する。
- feature branchにdocs evidenceをcommitした後にのみ `{branch or 'feature/issue-XXX'}` をpushする。
- 承認後、選択した候補に対してRAG buildを実行する。
- base work folderを削除する前に、base phaseのprocess reportを `work/close/improvement/{args.issue}/links.md` と各summary reportへ要約・リンク化する。
- 承認後、`uv run --project runtime python runtime/common/ctl.py --repo-root . close-archive prepare --issue {args.issue}` でreport-only close packageを作成する。
- source checkout、`.git`、`.venv`、cache削除は `uv run --project runtime python runtime/common/ctl.py --repo-root . close-archive prune --issue {args.issue} --execute --human-check approved` でのみ実行する。
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
            "target": f"work/close/improvement/{args.issue}",
            "status": archive_status,
            "policy": "report-only",
        },
        "base_work_reset": base_work_status,
        "context_resolution": {
            "scm_state": scm_resolution,
            "test_evidence": test_evidence_context,
            "manifest_present": manifest_path_for_work_dir(work_dir).exists(),
            "manifest_scm_state_required": not archive_mode,
            "legacy_scm_fallback_allowed": archive_mode
            or bool(getattr(args, "allow_legacy_scm_fallback", False)),
        },
        "human_actions": [
            f"docs evidenceをcommitした後に {branch or 'feature/issue-XXX'} をpushする。",
            f"承認済み候補について work/{args.issue} からRAG buildを実行する。",
            "base work folderを削除する前にbase work process-reportをsummary/link化する。",
            f"承認後、uv run --project runtime python runtime/common/ctl.py --repo-root . close-archive prepare --issue {args.issue} を実行する。",
            f"承認後、必要なら uv run --project runtime python runtime/common/ctl.py --repo-root . close-archive prune --issue {args.issue} --execute --human-check approved を実行する。",
        ],
    }
    if not args.dry_run:
        write_json(output_paths["knowledge_capture_json"], result)
        register_context(
            repo_root,
            work_dir,
            work_id=args.issue,
            context_type="knowledge-capture",
            path=output_paths["knowledge_capture_json"],
            required=False,
            generated_by="knowledge-capture",
            owner="workflow",
            schema=KNOWLEDGE_CAPTURE_SCHEMA,
        )
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
