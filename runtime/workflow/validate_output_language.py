from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import gate_restart  # noqa: E402
from runtime.constants.paths import (  # noqa: E402
    GENERATED_CHUNKS,
    GENERATED_EMBEDDINGS,
    GENERATED_INDEXES,
    GENERATED_JSONIZED,
    GENERATED_NORMALIZED,
    GENERATED_OPTIMIZED_CHUNKS,
    GENERATED_RETRIEVAL,
)

DEFAULT_PATHS = ["work", "rag", "docs"]
DEFAULT_EXCLUDES = [
    ".git",
    ".venv",
    "__pycache__",
    GENERATED_NORMALIZED.as_posix(),
    GENERATED_CHUNKS.as_posix(),
    GENERATED_INDEXES.as_posix(),
    GENERATED_EMBEDDINGS.as_posix(),
    GENERATED_RETRIEVAL.as_posix(),
    GENERATED_JSONIZED.as_posix(),
    GENERATED_OPTIMIZED_CHUNKS.as_posix(),
    "work/*/source",
    "work/close/**/source",
    "templates/boilerplates",
]
ALLOWED_ENGLISH_TERMS = {
    "ai",
    "api",
    "branch",
    "cli",
    "commit",
    "docker",
    "evidence",
    "github",
    "json",
    "localty",
    "markdown",
    "pr",
    "python",
    "rag",
    "readme",
    "repository",
    "runtime",
    "schema",
    "test",
    "vscode",
    "workflow",
}


@dataclass(frozen=True)
class LanguageFinding:
    path: Path
    japanese_chars: int
    english_words: int
    english_ratio: float
    reason: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Detect human-facing Markdown artifacts that are likely English-dominant.")
    parser.add_argument("--paths", nargs="+", default=DEFAULT_PATHS, help="Files or directories to scan.")
    parser.add_argument("--exclude", nargs="*", default=DEFAULT_EXCLUDES, help="Path patterns to exclude.")
    parser.add_argument("--english-ratio-threshold", type=float, default=0.62)
    parser.add_argument("--min-english-words", type=int, default=35)
    parser.add_argument("--min-japanese-chars", type=int, default=20)
    parser.add_argument("--fail-on-violation", action="store_true")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--json", action="store_true")
    return parser


def normalize_path(path: Path) -> str:
    return path.as_posix().lower()


def is_excluded(path: Path, repo_root: Path, patterns: list[str]) -> bool:
    try:
        rel = path.relative_to(repo_root)
    except ValueError:
        rel = path
    rel_text = normalize_path(rel)
    for pattern in patterns:
        normalized = pattern.replace("\\", "/").lower().rstrip("/")
        if (
            rel.match(pattern)
            or rel.match(pattern.rstrip("/") + "/**")
            or fnmatch.fnmatch(rel_text, normalized)
            or fnmatch.fnmatch(rel_text, normalized + "/*")
            or rel_text == normalized
            or rel_text.startswith(normalized + "/")
        ):
            return True
    return False


def iter_markdown(paths: list[str], repo_root: Path, excludes: list[str]) -> list[Path]:
    results: list[Path] = []
    for raw_path in paths:
        path = (repo_root / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
        if not path.exists():
            continue
        candidates = [path] if path.is_file() else sorted(path.rglob("*.md"))
        for candidate in candidates:
            if candidate.suffix.lower() != ".md":
                continue
            if is_excluded(candidate, repo_root, excludes):
                continue
            results.append(candidate)
    return sorted(set(results))


def strip_non_prose(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"^---\s.*?^---\s", " ", text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", " ", text, flags=re.MULTILINE)
    return text


def count_japanese_chars(text: str) -> int:
    return len(re.findall(r"[\u3040-\u30ff\u3400-\u9fff]", text))


def count_english_words(text: str) -> int:
    words = re.findall(r"\b[A-Za-z][A-Za-z'-]{2,}\b", text)
    return sum(1 for word in words if word.lower() not in ALLOWED_ENGLISH_TERMS)


def analyze(path: Path, args: argparse.Namespace) -> LanguageFinding | None:
    try:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return None
    prose = strip_non_prose(text)
    japanese_chars = count_japanese_chars(prose)
    english_words = count_english_words(prose)
    total = japanese_chars + english_words
    english_ratio = english_words / total if total else 0.0
    if english_words < args.min_english_words:
        return None
    if japanese_chars >= args.min_japanese_chars and english_ratio < args.english_ratio_threshold:
        return None
    reason = "英語語数が多く、日本語本文が少ない可能性があります。"
    return LanguageFinding(path, japanese_chars, english_words, english_ratio, reason)


def build_result(repo_root: Path, findings: list[LanguageFinding]) -> dict[str, Any]:
    status = "fail" if findings else "pass"
    records = []
    for finding in findings:
        try:
            rel = finding.path.relative_to(repo_root)
        except ValueError:
            rel = finding.path
        records.append(
            {
                "path": rel.as_posix(),
                "japanese_chars": finding.japanese_chars,
                "english_words": finding.english_words,
                "english_ratio": finding.english_ratio,
                "reason": finding.reason,
            }
        )
    return {
        "schema_version": "1.0",
        "artifact_type": "output-language-check",
        "status": status,
        "finding_count": len(findings),
        "findings": records,
        "gate_restart": gate_restart.build_gate_restart(
            "output-language-gate",
            restart_reason="english-dominant-markdown" if findings else "normal-output-language-gate",
            repair_available=False,
            status_after_restart=status,
        ),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd().resolve()
    findings = [finding for path in iter_markdown(args.paths, repo_root, args.exclude) if (finding := analyze(path, args))]
    result = build_result(repo_root, findings)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if findings and args.fail_on_violation else 0

    if not findings:
        print("Output language check OK: English-dominant Markdown artifacts were not detected.")
        return 0

    print("Output language check found likely English-dominant Markdown artifacts:")
    for finding in findings:
        try:
            rel = finding.path.relative_to(repo_root)
        except ValueError:
            rel = finding.path
        print(
            f"- {rel}: japanese_chars={finding.japanese_chars}, "
            f"english_words={finding.english_words}, english_ratio={finding.english_ratio:.2f} "
            f"({finding.reason})"
        )
    return 1 if args.fail_on_violation else 0


if __name__ == "__main__":
    raise SystemExit(main())
