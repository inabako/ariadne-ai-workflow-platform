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

from runtime.common import find_repo_root, relative_to_repo, slugify, utc_now_iso, write_json  # noqa: E402
from runtime.rag.cleanup_guard import assert_safe_clean_output_target  # noqa: E402
from runtime.rag.paths import GENERATED_NORMALIZED, SOURCE_CORRECTIVE_ACTION_REPORTS  # noqa: E402


FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
LIST_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$")
KEY_VALUE_RE = re.compile(r"^([A-Za-z0-9_. -]+):\s*(.*)$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize Markdown reports into JSON documents for file-based RAG indexing."
    )
    parser.add_argument(
        "--source-dir",
        default=str(SOURCE_CORRECTIVE_ACTION_REPORTS),
        help="Directory containing source Markdown documents.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(GENERATED_NORMALIZED),
        help="Directory where normalized JSON documents are written.",
    )
    parser.add_argument("--document-type", default="corrective-action-report")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--project", default="")
    parser.add_argument("--repository", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--commit", default="")
    parser.add_argument("--status", default="draft")
    parser.add_argument("--clean-output", action="store_true")
    return parser


def parse_scalar(value: str) -> str | list[str]:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        items = [item.strip().strip("'\"") for item in value.strip("[]").split(",")]
        return [item for item in items if item]
    return value.strip("'\"")


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def parse_front_matter_value(lines: list[str], start_index: int) -> tuple[str | list[str], int]:
    key, raw_value = lines[start_index].split(":", 1)
    value = raw_value.strip()
    if value:
        return parse_scalar(value), start_index + 1

    items: list[str] = []
    index = start_index + 1
    while index < len(lines):
        match = LIST_ITEM_RE.match(lines[index])
        if not match:
            break
        items.append(match.group(1).strip().strip("'\""))
        index += 1
    if items:
        return items, index
    return "", index


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text

    metadata: dict[str, Any] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            index += 1
            continue
        key = line.split(":", 1)[0].strip()
        value, next_index = parse_front_matter_value(lines, index)
        metadata[key] = value
        index = next_index
    return metadata, text[match.end() :]


def title_from_content(content: str, source: Path) -> str:
    for match in HEADING_RE.finditer(content):
        return match.group(2).strip()
    return source.stem


def headings_from_content(content: str) -> list[str]:
    return [match.group(2).strip() for match in HEADING_RE.finditer(content)]


def ensure_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def first_string(*values: Any) -> str:
    for value in values:
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value if str(item).strip())
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def external_web_metadata(front_matter: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "artifact_type": first_string(front_matter.get("artifact_type")),
        "source_type": first_string(front_matter.get("source_type")),
        "source_kind": first_string(front_matter.get("source_kind")),
        "source_owner": first_string(front_matter.get("source_owner")),
        "category": first_string(front_matter.get("category")),
        "topic": first_string(front_matter.get("topic")),
        "trust_level": first_string(front_matter.get("trust_level")),
        "retrieved_at": first_string(front_matter.get("retrieved_at")),
        "freshness_policy": first_string(front_matter.get("freshness_policy")),
        "sources": ensure_list(front_matter.get("sources")),
        "urls": ensure_list(front_matter.get("urls")),
        "claims": ensure_list(front_matter.get("claims")),
        "verification_notes": ensure_list(front_matter.get("verification_notes")),
    }
    if "verify_before_use" in front_matter:
        fields["verify_before_use"] = parse_bool(front_matter.get("verify_before_use"))
    return {
        key: value
        for key, value in fields.items()
        if not (value == "" or value == [])
    }


def normalize_document(
    repo_root: Path,
    source: Path,
    output_dir: Path,
    args: argparse.Namespace,
) -> dict[str, Any]:
    raw_text = source.read_text(encoding="utf-8-sig", errors="replace")
    front_matter, content = parse_front_matter(raw_text)
    title = first_string(front_matter.get("title"), title_from_content(content, source))
    document_type = first_string(front_matter.get("type"), args.document_type)
    legacy_document_id = slugify(f"{document_type}-{source.stem}")
    document_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-document:{relative_to_repo(repo_root, source)}"))
    output_path = output_dir / f"{document_id}.json"

    metadata = {
        "project": first_string(front_matter.get("project"), args.project),
        "repository": first_string(front_matter.get("repository"), args.repository),
        "branch": first_string(front_matter.get("branch"), args.branch),
        "commit": first_string(front_matter.get("commit"), args.commit, "unknown"),
        "workflow": first_string(front_matter.get("workflow"), "rag-normalization"),
        "phase": first_string(front_matter.get("phase"), "knowledge-capture"),
        "agent": first_string(front_matter.get("agent"), front_matter.get("owner_agent"), "runtime-rag"),
        "status": first_string(front_matter.get("status"), args.status),
        "created_at": first_string(front_matter.get("created_at"), utc_now_iso()),
        "updated_at": first_string(front_matter.get("updated_at")),
        "source": relative_to_repo(repo_root, source),
        "severity_focus": ensure_list(front_matter.get("severity_focus")),
        "areas": ensure_list(front_matter.get("areas")),
        "tags": ensure_list(front_matter.get("tags")) or [document_type],
    }
    metadata.update(external_web_metadata(front_matter))
    metadata["front_matter"] = front_matter

    normalized = {
        "schema_version": "1.0",
        "document_id": document_id,
        "legacy_document_id": legacy_document_id,
        "source_path": relative_to_repo(repo_root, source),
        "normalized_path": relative_to_repo(repo_root, output_path),
        "document_type": document_type,
        "title": title,
        "content": content.strip() + "\n",
        "summary": first_string(front_matter.get("summary")),
        "metadata": metadata,
        "headings": headings_from_content(content),
    }
    write_json(output_path, normalized)
    return normalized


def discover_sources(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"RAG source directory not found: {source_dir}")
    return sorted(
        path
        for path in source_dir.rglob("*.md")
        if path.is_file() and path.name.lower() != "readme.md"
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    source_dir = (repo_root / args.source_dir).resolve() if not Path(args.source_dir).is_absolute() else Path(args.source_dir)
    output_dir = (repo_root / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    if args.clean_output:
        assert_safe_clean_output_target(repo_root, output_dir)
    if args.clean_output and output_dir.exists():
        for path in output_dir.glob("*.json"):
            path.unlink()
    sources = discover_sources(source_dir)
    documents = [normalize_document(repo_root, source, output_dir, args) for source in sources]
    return {
        "source_dir": relative_to_repo(repo_root, source_dir),
        "output_dir": relative_to_repo(repo_root, output_dir),
        "document_count": len(documents),
        "documents": [document["normalized_path"] for document in documents],
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
