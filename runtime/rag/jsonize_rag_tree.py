from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.rag.cleanup_guard import assert_safe_clean_output_target  # noqa: E402


UUID_JSON_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert RAG files into UUID-named JSON wrapper documents.")
    parser.add_argument("--rag-dir", default="rag")
    parser.add_argument("--output-dir", default="rag/jsonized")
    parser.add_argument("--include-readme", action="store_true")
    parser.add_argument("--delete-source", action="store_true")
    parser.add_argument("--clean-output", action="store_true")
    parser.add_argument("--repo-root", default=None)
    return parser


def should_convert(path: Path, include_readme: bool) -> bool:
    if not path.is_file():
        return False
    if path.name.lower() == "readme.md" and not include_readme:
        return False
    if path.suffix.lower() == ".json":
        return not UUID_JSON_RE.match(path.name.lower())
    return path.suffix.lower() in {".jsonl", ".md", ".txt"}


def read_jsonl(path: Path) -> list[Any]:
    rows: list[Any] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            rows.append({"line_number": line_number, "raw": line, "parse_error": str(exc)})
    return rows


def source_payload(source: Path) -> tuple[str, Any, str]:
    suffix = source.suffix.lower()
    text = source.read_text(encoding="utf-8-sig", errors="replace")
    if suffix == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            payload = {"raw": text, "parse_error": str(exc)}
        return "json", payload, text
    if suffix == ".jsonl":
        payload = read_jsonl(source)
        return "jsonl", payload, text
    return "text", None, text


def jsonize_file(repo_root: Path, rag_dir: Path, output_dir: Path, source: Path) -> dict[str, Any]:
    rel_source = relative_to_repo(repo_root, source)
    artifact_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-jsonized:{rel_source}"))
    output_path = output_dir / f"{artifact_id}.json"
    source_format, payload, text = source_payload(source)
    artifact = {
        "schema_version": "1.0",
        "artifact_id": artifact_id,
        "artifact_type": "rag-jsonized-source",
        "source_path": rel_source,
        "source_extension": source.suffix.lower(),
        "source_format": source_format,
        "created_at": utc_now_iso(),
        "content": text,
        "payload": payload,
        "metadata": {
            "original_name": source.name,
            "relative_to_rag": source.resolve().relative_to(rag_dir.resolve()).as_posix(),
        },
    }
    write_json(output_path, artifact)
    return {
        "artifact_id": artifact_id,
        "source_path": rel_source,
        "json_path": relative_to_repo(repo_root, output_path),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    rag_dir = (repo_root / args.rag_dir if not Path(args.rag_dir).is_absolute() else Path(args.rag_dir)).resolve()
    output_dir = (repo_root / args.output_dir if not Path(args.output_dir).is_absolute() else Path(args.output_dir)).resolve()
    if not rag_dir.exists():
        raise FileNotFoundError(f"RAG directory not found: {rag_dir}")
    if args.clean_output:
        assert_safe_clean_output_target(repo_root, output_dir)
    if args.clean_output and output_dir.exists():
        for path in output_dir.glob("*.json"):
            path.unlink()

    sources = [
        path
        for path in sorted(rag_dir.rglob("*"))
        if output_dir not in [path, *path.parents] and should_convert(path, args.include_readme)
    ]
    converted = [jsonize_file(repo_root, rag_dir, output_dir, source) for source in sources]
    if args.delete_source:
        for source in sources:
            source.unlink()
    return {
        "rag_dir": relative_to_repo(repo_root, rag_dir),
        "output_dir": relative_to_repo(repo_root, output_dir),
        "converted_count": len(converted),
        "deleted_source": bool(args.delete_source),
        "artifacts": converted,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
