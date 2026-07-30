from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.workflow_limits import NOISE_REDUCTION_FINDING_PREVIEW_LIMIT  # noqa: E402
from runtime.workflow.workflow_state import update_state  # noqa: E402


OUTPUT_FILES = [
    "unknown-words-report.md",
    "terminology-conflict-report.md",
    "terminology-alias-report.md",
    "document-conflict-report.md",
    "ambiguous-language-report.md",
    "ai-confusion-report.md",
    "missing-definition-report.md",
    "human-interview-sheet.md",
    "project-glossary.md",
    "readiness-report.md",
]
CRITICAL_KEYWORDS = {
    "repository": ["repository", "リポジトリ", "repo"],
    "target_branch": ["target branch", "ブランチ", "branch"],
    "safety": ["安全", "safety"],
    "stop": ["stop", "停止", "非常停止", "emergency"],
    "communication_loss": ["通信断", "通信ロス", "communication loss", "切断"],
}
AMBIGUOUS_WORDS = [
    "いい感じ",
    "適切",
    "必要に応じて",
    "通常",
    "なるべく",
    "できるだけ",
    "高速",
    "低遅延",
    "安全に",
]
UNKNOWN_MARKERS = ["unknown", "不明", "未定", "TODO", "TBD", "？", "?"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def line_refs(text: str, needles: Sequence[str]) -> list[tuple[int, str, str]]:
    refs: list[tuple[int, str, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        for needle in needles:
            if needle.lower() in lower:
                refs.append((number, needle, line.strip()))
    return refs


def missing_critical_items(text: str) -> list[tuple[str, str]]:
    lower = text.lower()
    missing: list[tuple[str, str]] = []
    for key, labels in CRITICAL_KEYWORDS.items():
        if not any(label.lower() in lower for label in labels):
            missing.append((key, labels[0]))
    return missing


def unknown_terms(text: str) -> list[tuple[int, str, str]]:
    refs = line_refs(text, UNKNOWN_MARKERS)
    candidates: list[tuple[int, str, str]] = []
    for line_no, marker, line in refs:
        candidates.append((line_no, marker, line))
    # ASCII-ish project tokens that are often domain-specific.
    for line_no, line in enumerate(text.splitlines(), start=1):
        for token in re.findall(r"\b[A-Z][A-Z0-9_-]{2,}\b", line):
            if token not in {"TODO", "TBD", "API", "URL", "HTTP", "JSON"}:
                candidates.append((line_no, token, line.strip()))
    seen: set[tuple[int, str]] = set()
    unique: list[tuple[int, str, str]] = []
    for item in candidates:
        key = (item[0], item[1])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:NOISE_REDUCTION_FINDING_PREVIEW_LIMIT]


def ambiguous_expressions(text: str) -> list[tuple[int, str, str]]:
    return line_refs(text, AMBIGUOUS_WORDS)[:NOISE_REDUCTION_FINDING_PREVIEW_LIMIT]


def determine_readiness(missing: list[tuple[str, str]], unknowns: list[tuple[int, str, str]]) -> str:
    if missing:
        return "BLOCK"
    if unknowns:
        return "WARNING"
    return "PASS"


def report_table(rows: list[list[str]], headers: list[str]) -> str:
    table = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        table.append("| " + " | ".join(cell.replace("\n", " ") for cell in row) + " |")
    return "\n".join(table)


def build_reports(repo_root: Path, draft: Path, output_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    text = read_text(draft)
    missing = missing_critical_items(text)
    unknowns = unknown_terms(text)
    ambiguous = ambiguous_expressions(text)
    readiness = determine_readiness(missing, unknowns)
    created_at = utc_now_iso()
    draft_rel = relative_to_repo(repo_root, draft)

    unknown_rows = [
        [f"UW-{idx:03d}", term, draft_rel, f"L{line_no}", context, "意味を人間に確認する", "High", f"HI-{idx:03d}"]
        for idx, (line_no, term, context) in enumerate(unknowns, start=1)
    ]
    missing_rows = [
        [f"MD-{idx:03d}", label, draft_rel, "Critical項目がdraft内で確認できない", "人間が方針を明示する", "High", f"HI-MD-{idx:03d}"]
        for idx, (_key, label) in enumerate(missing, start=1)
    ]
    ambiguous_rows = [
        [f"AL-{idx:03d}", word, draft_rel, f"L{line_no}: {context}", "解釈が複数あり得る", "期待する基準を明示する", "Medium", f"HI-AL-{idx:03d}"]
        for idx, (line_no, word, context) in enumerate(ambiguous, start=1)
    ]

    human_rows: list[list[str]] = []
    for idx, row in enumerate(unknown_rows, start=1):
        human_rows.append([f"HI-{idx:03d}", f"`{row[1]}` のプロジェクト内での意味は何ですか。", row[4], "用語", "High", "unknown-words-report.md", "yes", "", ""])
    for idx, row in enumerate(missing_rows, start=1):
        human_rows.append([f"HI-MD-{idx:03d}", f"`{row[1]}` を明示してください。", row[3], "Critical", "High", "missing-definition-report.md", "yes", "", ""])
    for idx, row in enumerate(ambiguous_rows, start=1):
        human_rows.append([f"HI-AL-{idx:03d}", f"`{row[1]}` の判断基準は何ですか。", row[4], "曖昧表現", "Medium", "ambiguous-language-report.md", "no", "", ""])

    reports = {
        "unknown-words-report.md": f"""---
project:
draft: {draft_rel}
workflow: requirement-discovery
phase: noise-reduction
artifact: unknown-words-report
status: draft
language: ja-JP
created_at: {created_at}
---

# Unknown Words Report

## 検出結果

{report_table(unknown_rows, ["ID", "Term", "Source Document", "Location", "Context", "Why Unknown", "Priority", "Human Interview ID"]) if unknown_rows else "不明ワード候補は検出されませんでした。"}
""",
        "missing-definition-report.md": f"""# Missing Definition Report

## Critical項目の不足

{report_table(missing_rows, ["ID", "Missing Definition", "Source / Context", "Impact", "Required Decision", "Priority", "Human Interview ID"]) if missing_rows else "Critical項目の不足は検出されませんでした。"}
""",
        "ambiguous-language-report.md": f"""# Ambiguous Language Report

## 曖昧表現

{report_table(ambiguous_rows, ["ID", "Expression", "Source", "Context", "Why Ambiguous", "Required Clarification", "Priority", "Human Interview ID"]) if ambiguous_rows else "曖昧表現候補は検出されませんでした。"}
""",
        "human-interview-sheet.md": f"""# Human Interview Sheet

## 質問

{report_table(human_rows, ["ID", "Question", "Reason", "Impact Area", "Priority", "Related Reports", "Blocks Readiness", "Owner", "Answer"]) if human_rows else "現時点で人間確認が必要な質問はありません。"}

## 回答ルール

- `Blocks Readiness` が `yes` の質問に回答がない場合、Readinessは `BLOCK` です。
- 回答後はProject Glossaryまたは該当reportへ反映してください。
""",
        "project-glossary.md": f"""# Project Glossary

## 用語集

{report_table([[f"PG-{idx:03d}", term, "", "", draft_rel, "", "", "unresolved"] for idx, (_line, term, _context) in enumerate(unknowns, start=1)], ["ID", "Official Name", "Alias", "Meaning", "Usage Location", "Related Documents", "Human Answer", "Status"]) if unknowns else "未確定用語はありません。"}
""",
        "readiness-report.md": f"""# Readiness Report

## Readiness

| Field | Value |
| --- | --- |
| Status | {readiness} |
| Reason | {"Critical項目の不足があります。" if readiness == "BLOCK" else "不明ワードがあります。" if readiness == "WARNING" else "Noise Reduction上のblocking itemはありません。"} |
| Human Interview Open High Count | {len(unknown_rows) + len(missing_rows)} |
| Human Interview Open Medium Count | {len(ambiguous_rows)} |
| Human Interview Open Low Count | 0 |
| Requirement Review Draft May Start | {"no" if readiness == "BLOCK" else "yes"} |
| Design / Implementation May Start | no |

## Checklist

| Check | Status | Evidence |
| --- | --- | --- |
| Unknown Words整理済み | {"warning" if unknown_rows else "pass"} | unknown-words-report.md |
| 曖昧表現整理済み | {"warning" if ambiguous_rows else "pass"} | ambiguous-language-report.md |
| 不足定義整理済み | {"block" if missing_rows else "pass"} | missing-definition-report.md |
| Human Interview票作成済み | pass | human-interview-sheet.md |
| Project Glossary作成済み | pass | project-glossary.md |
""",
        "terminology-conflict-report.md": "# Terminology Conflict Report\n\n専用辞書との衝突検出は未設定です。人間回答後に必要な衝突を追記してください。\n",
        "terminology-alias-report.md": "# Terminology Alias Report\n\n表記揺れ候補は必要に応じて追記してください。\n",
        "document-conflict-report.md": "# Document Conflict Report\n\n複数資料間の矛盾は必要に応じて追記してください。\n",
        "ai-confusion-report.md": "# AI Confusion Report\n\nAIが推測しそうな箇所はHuman Interview Sheetへ集約されています。\n",
    }
    summary = {
        "draft": draft_rel,
        "output_dir": relative_to_repo(repo_root, output_dir),
        "readiness": readiness,
        "unknown_count": len(unknown_rows),
        "missing_critical_count": len(missing_rows),
        "ambiguous_count": len(ambiguous_rows),
        "human_question_count": len(human_rows),
    }
    return reports, summary


def resolve_draft(repo_root: Path, draft_value: str) -> Path:
    draft = Path(draft_value)
    if not draft.is_absolute():
        draft = repo_root / draft
    if not draft.exists():
        raise FileNotFoundError(f"Draft not found: {draft}")
    return draft


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    draft = resolve_draft(repo_root, args.draft)
    output_dir = Path(args.output_dir) if args.output_dir else draft.parent / f"{draft.stem}-noise-reduction"
    if not output_dir.is_absolute():
        output_dir = repo_root / output_dir
    reports, summary = build_reports(repo_root, draft, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_FILES:
        write_md(output_dir / name, reports[name])
    work_dir = output_dir
    update_state(
        work_dir,
        workflow="requirement-discovery",
        work_id=draft.stem,
        phase="noise-reduction",
        status="blocked" if summary["readiness"] == "BLOCK" else "review-ready",
        blocking_reason="Human Interviewの回答が必要です。" if summary["readiness"] == "BLOCK" else "",
        next_human_action="human-interview-sheet.md に回答してください。" if summary["readiness"] == "BLOCK" else "Open Questionsを確認してください。",
        artifacts={name.removesuffix(".md"): relative_to_repo(repo_root, output_dir / name) for name in OUTPUT_FILES},
    )
    return {
        "status": "blocked" if summary["readiness"] == "BLOCK" else "ready",
        **summary,
        "created_files": [relative_to_repo(repo_root, output_dir / name) for name in OUTPUT_FILES],
        "state_path": relative_to_repo(repo_root, output_dir / "context" / "workflow-state.json"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Noise Reduction artifacts for requirement discovery.")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--draft", required=True)
    run_parser.add_argument("--output-dir", default="")
    run_parser.add_argument("--repo-root", default="")
    run_parser.set_defaults(handler=run)
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
