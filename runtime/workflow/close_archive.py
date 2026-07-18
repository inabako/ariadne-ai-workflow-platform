from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso  # noqa: E402
from runtime.constants.paths import (  # noqa: E402
    KNOWLEDGE_SOURCE_RAG,
    KNOWLEDGE_SOURCE_REPO,
    SOURCE_GITHUB_KNOWLEDGE,
    SOURCE_WORKSPACE_ENVIRONMENT,
)
from runtime.constants.workspace import (  # noqa: E402
    context_dir_for_work_dir,
    process_report_dir_for_work_dir,
    test_evidence_dir_for_work_dir,
    work_dir_for_id,
)


REPORT_FILES = [
    "00-summary.md",
    "01-work-report.md",
    "02-test-report.md",
    "03-review-report.md",
    "04-human-check.md",
    "05-retrospective.md",
    "links.md",
    "metadata.json",
]
CATEGORY_CHOICES = ["auto", "improvement", "new-system-dev", "github", "vscode"]
TIMESTAMP_ARCHIVE_CATEGORIES = {"github", "vscode"}
ROOT_PRUNE_DIR_NAMES = {"source", "repository"}
PRUNE_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    "__pycache__",
    "coverage",
    "htmlcov",
    "tmp",
    "temp",
    ".cache",
}
PRUNE_FILE_SUFFIXES = {".pyc", ".pyo"}
SUMMARY_CANDIDATES = [
    "process-report/knowledge-capture-report.md",
    "process-report/pull-request-description.md",
    "process-report/merge-comment.md",
    "process-report/simulator-workspace-setup-20260607.md",
]
RAG_SOURCE_DIRS_BY_CATEGORY = {
    "github": [SOURCE_GITHUB_KNOWLEDGE.as_posix()],
    "vscode": [SOURCE_WORKSPACE_ENVIRONMENT.as_posix()],
    "improvement": [KNOWLEDGE_SOURCE_RAG.as_posix()],
    "new-system-dev": [KNOWLEDGE_SOURCE_RAG.as_posix()],
}
RAG_REF_PATTERN = re.compile(
    rf"(?P<path>(?:{re.escape(KNOWLEDGE_SOURCE_REPO.as_posix() + '/')})?rag/[^\s)>\]\"']+?\.md)",
    re.IGNORECASE,
)
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+\.md)\)")
MOJIBAKE_TOKENS = [
    "\u7e3a",
    "\u7e67",
    "\u8b41",
    "\u87b3",
    "\u8708",
    "\u8b6b",
    "\u83a0",
    "\u96b1",
    "\u7e5d",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and maintain lightweight report-only archives under work/close/<category>/."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("audit", "prepare", "prune"):
        sub = subparsers.add_parser(name)
        sub.add_argument("--issue", default="", help="Issue id such as issue-11. Compatibility alias for --work-id.")
        sub.add_argument("--work-id", default="", help="Work folder id under work/.")
        sub.add_argument("--category", choices=CATEGORY_CHOICES, default="auto")
        sub.add_argument("--archive-id", default="", help="Archive folder name under the selected category.")
        sub.add_argument("--repo-root", default=None)
        sub.add_argument("--source-work-dir", default="", help="Source work directory. Default: work/<work-id>.")
        sub.add_argument("--archive-dir", default="", help="Explicit archive directory. Overrides category/archive-id.")
        if name == "prepare":
            sub.add_argument(
                "--source-rag",
                action="append",
                default=[],
                help="RAG source Markdown path. Can be specified multiple times or comma-separated.",
            )
            sub.add_argument(
                "--no-auto-rag",
                action="store_true",
                help="Disable automatic RAG source discovery during report generation.",
            )
            sub.add_argument(
                "--require-rag",
                action="store_true",
                help="Fail prepare when no RAG source is found.",
            )
        if name == "prune":
            sub.add_argument("--execute", action="store_true", help="Actually remove prune targets.")
            sub.add_argument("--human-check", choices=["approved", "pending"], default="pending")
        sub.set_defaults(handler={"audit": run_audit, "prepare": run_prepare, "prune": run_prune}[name])
    return parser


def random_suffix(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def timestamp_archive_id() -> str:
    return f"{datetime.now().strftime('%y%m%d%H%M%S')}_{random_suffix()}"


def resolve_work_id(args: argparse.Namespace) -> str:
    work_id = args.work_id or args.issue
    if not work_id:
        raise ValueError("--work-id or --issue is required")
    return work_id


def derive_category(work_id: str, requested: str) -> str:
    if requested != "auto":
        return requested
    if work_id.startswith("github-knowledge-"):
        return "github"
    if work_id.startswith("vscode-") or work_id == "vscode-environment":
        return "vscode"
    return "improvement"


def derive_archive_id(command: str, work_id: str, category: str, requested: str, explicit_archive_dir: str) -> str:
    if explicit_archive_dir:
        return requested or Path(explicit_archive_dir).name
    if requested:
        return requested
    if category in TIMESTAMP_ARCHIVE_CATEGORIES:
        if command == "prepare":
            return timestamp_archive_id()
        raise ValueError(f"--archive-id or --archive-dir is required for {category} archive {command}")
    return work_id


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, str, str, str]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    work_id = resolve_work_id(args)
    category = derive_category(work_id, args.category)
    archive_id = derive_archive_id(args.command, work_id, category, args.archive_id, args.archive_dir)
    source_work_dir = Path(args.source_work_dir).resolve() if args.source_work_dir else work_dir_for_id(repo_root, work_id)
    archive_dir = (
        Path(args.archive_dir).resolve()
        if args.archive_dir
        else work_dir_for_id(repo_root, "close") / category / archive_id
    )
    return repo_root, source_work_dir, archive_dir, work_id, category, archive_id


def safe_relative(repo_root: Path, path: Path) -> str:
    return relative_to_repo(repo_root, path)


def assert_inside(parent: Path, child: Path) -> None:
    parent_resolved = parent.resolve()
    child_resolved = child.resolve()
    if parent_resolved != child_resolved and parent_resolved not in child_resolved.parents:
        raise ValueError(f"Refusing path outside archive: {child_resolved}")


def collapse_nested_targets(targets: set[Path]) -> list[Path]:
    selected: list[Path] = []
    for target in sorted(targets, key=lambda item: len(item.parts)):
        if any(parent in target.parents for parent in selected):
            continue
        selected.append(target)
    return sorted(selected, key=lambda item: len(item.parts), reverse=True)


def list_prune_targets(archive_dir: Path) -> list[Path]:
    if not archive_dir.exists():
        return []

    targets: set[Path] = set()
    for child in archive_dir.iterdir():
        if child.name not in REPORT_FILES:
            targets.add(child)

    for name in ROOT_PRUNE_DIR_NAMES:
        root_child = archive_dir / name
        if root_child.is_dir():
            targets.add(root_child)

    for path in archive_dir.rglob("*"):
        if path.is_dir() and path.name in PRUNE_DIR_NAMES:
            targets.add(path)
        elif path.is_file() and path.suffix in PRUNE_FILE_SUFFIXES:
            targets.add(path)
    return collapse_nested_targets(targets)


def read_sample(path: Path, max_chars: int = 4000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")[:max_chars].strip()


def collect_files(directory: Path, limit: int = 40) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(path for path in directory.rglob("*") if path.is_file())[:limit]


def split_cli_paths(values: Sequence[str]) -> list[str]:
    paths: list[str] = []
    for value in values:
        for item in value.split(","):
            cleaned = item.strip().strip('"').strip("'")
            if cleaned:
                paths.append(cleaned)
    return paths


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root / path


def unique_paths(paths: Sequence[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def read_text_safe(path: Path, max_chars: int | None = None) -> str:
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    return text[:max_chars] if max_chars is not None else text


def extract_rag_references(text: str) -> list[str]:
    refs = [match.group("path").replace("\\", "/") for match in RAG_REF_PATTERN.finditer(text)]
    for _label, target in MARKDOWN_LINK_PATTERN.findall(text):
        normalized = target.replace("\\", "/")
        if normalized.startswith("rag/"):
            refs.append(normalized)
    return refs


def collect_referenced_rag_sources(repo_root: Path, source_work_dir: Path) -> list[Path]:
    if not source_work_dir.exists():
        return []
    refs: list[Path] = []
    for path in collect_files(source_work_dir, limit=300):
        if path.suffix.lower() not in {".md", ".json", ".txt"}:
            continue
        text = read_text_safe(path, max_chars=20000)
        for ref in extract_rag_references(text):
            candidate = resolve_repo_path(repo_root, ref)
            if candidate.exists() and candidate.is_file():
                refs.append(candidate)
    return unique_paths(refs)


def significant_tokens(work_id: str, _category: str) -> list[str]:
    raw_tokens = re.split(r"[^a-zA-Z0-9]+", work_id)
    ignored = {"work", "issue", "github", "knowledge", "recent", "environment", "close", "test"}
    return [token.lower() for token in raw_tokens if len(token) >= 4 and token.lower() not in ignored]


def candidate_rag_files(repo_root: Path, category: str) -> list[Path]:
    dirs = RAG_SOURCE_DIRS_BY_CATEGORY.get(category, ["rag"])
    candidates: list[Path] = []
    for relative in dirs:
        root = repo_root / relative
        if root.exists():
            candidates.extend(path for path in sorted(root.rglob("*.md")) if path.name.lower() != "readme.md")
    return unique_paths(candidates)


def score_rag_candidate(path: Path, repo_root: Path, work_id: str, category: str) -> int:
    rel = safe_relative(repo_root, path).replace("\\", "/").lower()
    text = read_text_safe(path, max_chars=30000).lower()
    tokens = significant_tokens(work_id, category)
    score = 0
    if work_id.lower() in rel or work_id.lower() in text:
        score += 12
    if category == "github" and rel.startswith(SOURCE_GITHUB_KNOWLEDGE.as_posix() + "/"):
        score += 5
    if category == "vscode" and rel.startswith(SOURCE_WORKSPACE_ENVIRONMENT.as_posix() + "/"):
        score += 5
    for token in tokens:
        if token in rel:
            score += 4
        if token in text:
            score += 2
    return score


def discover_rag_sources(
    repo_root: Path,
    source_work_dir: Path,
    work_id: str,
    category: str,
    explicit_values: Sequence[str],
    auto_discovery: bool,
) -> list[Path]:
    explicit_paths = [resolve_repo_path(repo_root, value) for value in split_cli_paths(explicit_values)]
    explicit_existing = [path for path in explicit_paths if path.exists() and path.is_file()]
    refs = collect_referenced_rag_sources(repo_root, source_work_dir) if auto_discovery else []

    scored: list[tuple[int, Path]] = []
    if auto_discovery:
        for candidate in candidate_rag_files(repo_root, category):
            score = score_rag_candidate(candidate, repo_root, work_id, category)
            if score > 5:
                scored.append((score, candidate))
    scored_paths = [
        path
        for _score, path in sorted(scored, key=lambda item: (-item[0], safe_relative(repo_root, item[1])))[:8]
    ]
    return unique_paths([*explicit_existing, *refs, *scored_paths])


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.removeprefix("# ").strip() or fallback
    return fallback


def strip_front_matter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip()
    return text


def metadata_title(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:80]:
        if line.strip() == "---":
            break
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def first_paragraph(text: str, max_chars: int = 700) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if lines:
                break
            continue
        if stripped.startswith("#"):
            continue
        lines.append(stripped)
        if sum(len(item) for item in lines) >= max_chars:
            break
    paragraph = " ".join(lines).strip()
    return paragraph[:max_chars].rstrip()


def markdown_headings(text: str, limit: int = 8) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^#{2,4}\s+", stripped):
            headings.append(re.sub(r"^#{2,4}\s+", "", stripped))
        if len(headings) >= limit:
            break
    return headings


def markdown_bullets(text: str, limit: int = 12) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+\.\s+", stripped):
            cleaned = re.sub(r"^([-*]|\d+\.)\s+", "", stripped)
            if cleaned and cleaned not in bullets:
                bullets.append(cleaned[:240])
        if len(bullets) >= limit:
            break
    return bullets


def has_mojibake(text: str) -> bool:
    return any(token in text for token in MOJIBAKE_TOKENS)


def summarize_rag_source(repo_root: Path, path: Path) -> dict[str, Any]:
    text = read_text_safe(path, max_chars=60000)
    body = strip_front_matter(text)
    rel = safe_relative(repo_root, path)
    return {
        "path": rel,
        "title": first_heading(body, metadata_title(text) or Path(rel).stem),
        "excerpt": first_paragraph(body),
        "headings": markdown_headings(body),
        "bullets": markdown_bullets(body),
        "has_mojibake": has_mojibake(text),
    }


def build_rag_context(repo_root: Path, paths: Sequence[Path]) -> list[dict[str, Any]]:
    return [summarize_rag_source(repo_root, path) for path in unique_paths(paths)]


def format_rag_source_list(rag_context: Sequence[dict[str, Any]]) -> str:
    if not rag_context:
        return "- 自動検出されたRAG sourceはありません。必要に応じて `--source-rag` を指定してください。"
    return "\n".join(f"- `{item['path']}`: {item['title']}" for item in rag_context)


def format_rag_digest(rag_context: Sequence[dict[str, Any]]) -> str:
    if not rag_context:
        return "RAG sourceを自動検出できませんでした。このarchiveは標準レポートのみで作成されています。"

    sections: list[str] = []
    for item in rag_context:
        lines = [
            f"### {item['title']}",
            "",
            f"- Source: `{item['path']}`",
        ]
        if item["excerpt"]:
            lines.extend(["", item["excerpt"]])
        if item["headings"]:
            lines.extend(["", "主な見出し:", *[f"- {heading}" for heading in item["headings"]]])
        if item["bullets"]:
            lines.extend(["", "主な要点:", *[f"- {bullet}" for bullet in item["bullets"]]])
        if item["has_mojibake"]:
            lines.extend(["", "注意: このRAG sourceには文字化け疑いの文字列が含まれます。原文確認が必要です。"])
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def bullet_paths(repo_root: Path, files: list[Path]) -> str:
    if not files:
        return "- なし"
    return "\n".join(f"- `{safe_relative(repo_root, path)}`" for path in files)


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def source_hint(source_work_dir: Path, relative: str) -> str:
    sample = read_sample(source_work_dir / relative, max_chars=2000)
    return sample or "元成果物が見つからないため、必要に応じてGitHub Issue / PR / Commit / RAG sourceを参照してください。"


def archive_title(work_id: str, category: str, archive_id: str) -> str:
    return f"{category}/{archive_id} ({work_id})"


def build_reports(
    repo_root: Path,
    work_id: str,
    category: str,
    archive_id: str,
    source_work_dir: Path,
    archive_dir: Path,
    rag_context: Sequence[dict[str, Any]],
    auto_rag_enabled: bool,
) -> dict[str, str]:
    process_files = collect_files(process_report_dir_for_work_dir(source_work_dir))
    test_spec_files = collect_files(source_work_dir / "test-specifications")
    test_evidence_files = collect_files(test_evidence_dir_for_work_dir(source_work_dir))
    context_files = collect_files(context_dir_for_work_dir(source_work_dir))
    summary_text = ""
    for relative in SUMMARY_CANDIDATES:
        summary_text = read_sample(source_work_dir / relative)
        if summary_text:
            break

    title = archive_title(work_id, category, archive_id)
    rag_sources = format_rag_source_list(rag_context)
    rag_digest = format_rag_digest(rag_context)
    rag_status = "auto-discovered" if auto_rag_enabled else "explicit-only"
    rag_warning_count = sum(1 for item in rag_context if item["has_mojibake"])
    reports = {
        "00-summary.md": f"""# {title} Summary

## 完了作業

- Work ID: `{work_id}`
- Category: `{category}`
- Archive ID: `{archive_id}`
- Status: closed / archived
- Archive type: report-only
- Source snapshot retained: no
- Created at: {utc_now_iso()}
- RAG source mode: {rag_status}
- RAG source count: {len(rag_context)}

## 作業概要

{summary_text or "作業概要は `01-work-report.md` と `links.md`、または対応するIssue / PR / RAG sourceを参照してください。"}

## 自動吸収したRAG source

{rag_sources}

## RAGから抽出した要約

{rag_digest}
""",
        "01-work-report.md": f"""# Work Report

## 実施した作業

{source_hint(source_work_dir, "process-report/knowledge-capture-report.md")}

## RAG吸収内容から見た作業内容

{rag_digest}

## 参照した作業レポート

{bullet_paths(repo_root, process_files)}
""",
        "02-test-report.md": f"""# Test Report

## テスト仕様書

{bullet_paths(repo_root, test_spec_files)}

## テストエビデンス

{bullet_paths(repo_root, test_evidence_files)}

## 注意

`work/close` にはテスト用source checkout、仮想環境、cache、log原本を保持しません。再確認が必要な場合はGitHub branch、PR、target repository docs/evidence、RAG sourceを参照してください。

## RAG sourceから見た検証・証跡

{rag_digest}
""",
        "03-review-report.md": f"""# Review Report

## レビュー結果

{source_hint(source_work_dir, "process-report/knowledge-capture-report.md")}

## RAG source確認

{rag_digest}

## 未解決事項

- archive時点で未解決事項がある場合は、関連Issue / PR / docs / RAG sourceへリンクしてください。
- RAG sourceが自動検出されなかった場合は、`prepare --source-rag <path>` または `--require-rag` を使って抜け漏れを防止してください。
""",
        "04-human-check.md": f"""# Human Check

## 確認記録

- 確認者: 未記録
- 確認日時: 未記録
- 確認観点: 完了作業のsummary、test、review、linksが読める状態であること
- 判定: 未記録
- 差し戻し理由: なし

## 自動RAG反映の確認

- RAG source mode: {rag_status}
- RAG source count: {len(rag_context)}
- 文字化け疑いRAG source数: {rag_warning_count}

確認時は、`00-summary.md` と `01-work-report.md` にRAG由来の具体内容が入っていることを見てください。

## 人間判断が必要だった箇所

- prune / 元work directory削除は、人間の `削除承認` 後にだけ実行してください。
""",
        "05-retrospective.md": f"""# Retrospective

## 良かった点

- report-only archiveとして作業概要を軽量に残せる状態にした。
- RAG sourceを自動検出し、close reportへ具体内容を転記できる状態にした。

## 詰まった点

- 詳細は対応する作業レポート、RAG source、Issue / PRを参照する。
- RAG sourceが存在しない、または命名とwork-idが結びつかない場合は自動検出できない可能性がある。

## 次回改善したい点

- archive作成後に、空欄、文字化け、存在しないローカルパスが残っていないか確認する。
- 重要なRAG sourceは `--source-rag` で明示指定する。必須にしたい場合は `--require-rag` を使う。

## 再利用できる知見 / RAG候補

- `links.md` と下記のRAG sourceを参照する。

{rag_sources}
""",
        "links.md": f"""# Links

## Workflow Artifacts

### Process Reports

{bullet_paths(repo_root, process_files)}

### Context

{bullet_paths(repo_root, context_files)}

### Test Specifications

{bullet_paths(repo_root, test_spec_files)}

### Test Evidence

{bullet_paths(repo_root, test_evidence_files)}

## External Links

- GitHub Issue: 未記録
- GitHub PR: 未記録
- Commit: 未記録
- ADR: 未記録
- Docs: 未記録
- Evidence: 未記録
- RAG: 下記参照

## RAG Sources

{rag_sources}
""",
    }
    metadata = {
        "work_id": work_id,
        "category": category,
        "archive_id": archive_id,
        "status": "closed",
        "archive_type": "report-only",
        "source_work_dir": safe_relative(repo_root, source_work_dir),
        "archive_dir": safe_relative(repo_root, archive_dir),
        "created_at": utc_now_iso(),
        "has_source_snapshot": False,
        "report_only": True,
        "process_report_count": len(process_files),
        "test_specification_count": len(test_spec_files),
        "test_evidence_count": len(test_evidence_files),
        "rag_source_mode": rag_status,
        "rag_source_count": len(rag_context),
        "rag_sources": [item["path"] for item in rag_context],
        "rag_source_mojibake_warning_count": rag_warning_count,
    }
    reports["metadata.json"] = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    return reports


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, _source_work_dir, archive_dir, work_id, category, archive_id = resolve_paths(args)
    targets = list_prune_targets(archive_dir)
    missing_reports = [name for name in REPORT_FILES if not (archive_dir / name).exists()]
    return {
        "status": "ok",
        "work_id": work_id,
        "category": category,
        "archive_id": archive_id,
        "archive_dir": safe_relative(repo_root, archive_dir),
        "exists": archive_dir.exists(),
        "missing_report_files": missing_reports,
        "prune_target_count": len(targets),
        "prune_targets": [safe_relative(repo_root, path) for path in targets[:200]],
        "report_only_ready": archive_dir.exists() and not missing_reports and not targets,
    }


def run_prepare(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, source_work_dir, archive_dir, work_id, category, archive_id = resolve_paths(args)
    auto_rag_enabled = not args.no_auto_rag
    rag_paths = discover_rag_sources(
        repo_root=repo_root,
        source_work_dir=source_work_dir,
        work_id=work_id,
        category=category,
        explicit_values=args.source_rag,
        auto_discovery=auto_rag_enabled,
    )
    if args.require_rag and not rag_paths:
        raise FileNotFoundError(
            "RAG source was required but not found. Specify --source-rag or run without --require-rag."
        )
    rag_context = build_rag_context(repo_root, rag_paths)
    reports = build_reports(
        repo_root,
        work_id,
        category,
        archive_id,
        source_work_dir,
        archive_dir,
        rag_context,
        auto_rag_enabled,
    )
    for name, content in reports.items():
        path = archive_dir / name
        if name == "metadata.json":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        else:
            write_markdown(path, content)
    return {
        "status": "prepared",
        "work_id": work_id,
        "category": category,
        "archive_id": archive_id,
        "archive_dir": safe_relative(repo_root, archive_dir),
        "rag_source_count": len(rag_context),
        "rag_sources": [item["path"] for item in rag_context],
        "created_files": [safe_relative(repo_root, archive_dir / name) for name in REPORT_FILES],
        "next_action": "Review generated reports, then run prune with --execute --human-check approved if cleanup is approved.",
    }


def run_prune(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, _source_work_dir, archive_dir, work_id, category, archive_id = resolve_paths(args)
    targets = list_prune_targets(archive_dir)
    for target in targets:
        assert_inside(archive_dir, target)
    if args.execute and args.human_check != "approved":
        raise PermissionError("--execute requires --human-check approved")
    missing_reports = [name for name in REPORT_FILES if not (archive_dir / name).exists()]
    if args.execute and missing_reports:
        raise FileNotFoundError(f"Refusing prune because report files are missing: {missing_reports}")

    removed: list[str] = []
    if args.execute:
        for target in targets:
            if not target.exists():
                continue
            if target.is_dir():
                remove_tree(target)
            else:
                remove_file(target)
            removed.append(safe_relative(repo_root, target))
    return {
        "status": "pruned" if args.execute else "dry-run",
        "work_id": work_id,
        "category": category,
        "archive_id": archive_id,
        "archive_dir": safe_relative(repo_root, archive_dir),
        "execute": bool(args.execute),
        "target_count": len(targets),
        "targets": [safe_relative(repo_root, path) for path in targets[:200]],
        "removed": removed,
    }


def remove_file(path: Path) -> None:
    try:
        path.unlink()
    except PermissionError:
        os.chmod(path, 0o700)
        path.unlink()


def remove_tree(path: Path) -> None:
    def on_error(function: Any, failed_path: str, _exc_info: Any) -> None:
        os.chmod(failed_path, 0o700)
        function(failed_path)

    shutil.rmtree(path, onerror=on_error)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
