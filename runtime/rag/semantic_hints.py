from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, slugify, utc_now_iso  # noqa: E402
from runtime.constants.cli_defaults import (  # noqa: E402
    RAG_CHUNK_OVERLAP_DEFAULT,
    RAG_CHUNK_SIZE_DEFAULT,
    RAG_EMBEDDING_DIMENSIONS_DEFAULT,
    RAG_RETRIEVE_MAX_CHARS_DEFAULT,
    RAG_RETRIEVE_TOP_K_DEFAULT,
    RAG_STANDARDIZE_RANDOM_LENGTH_DEFAULT,
)
from runtime.constants.paths import (  # noqa: E402
    CHUNKS_INDEX,
    DUCKDB_DEFAULT_PATH,
    EMBEDDINGS_INDEX,
    GENERATED_CHUNKS,
    GENERATED_INDEXES,
    GENERATED_NORMALIZED,
    GENERATED_OPTIMIZED_CHUNKS,
    GENERATED_RETRIEVAL,
    SEMANTIC_HINT_BACKUPS,
    SOURCE_SEMANTIC_HINTS,
)
from runtime.rag import rag_build, retrieve_context  # noqa: E402


DEFAULT_DOCUMENT_TYPE = "semantic-hint"
DEFAULT_BUILD_OUTPUT = GENERATED_RETRIEVAL / "semantic-hints-build-latest.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate, build, and read semantic hints for RAG.")
    parser.add_argument("--repo-root", default="")
    subparsers = parser.add_subparsers(dest="semantic_hints_command")

    generate = subparsers.add_parser("generate", help="Generate RAG source Markdown from semantic hint backup JSON.")
    generate.add_argument("--source-file", action="append", default=[])
    generate.add_argument("--source-dir", default=str(SEMANTIC_HINT_BACKUPS))
    generate.add_argument("--output-dir", default=str(SOURCE_SEMANTIC_HINTS))
    generate.add_argument("--project", default="ariadne")
    generate.add_argument("--repository", default="ariadne-ai-workflow-platform")
    generate.add_argument("--status", default="approved")
    generate.add_argument("--clean-output", action="store_true")

    build = subparsers.add_parser("build", help="Generate semantic hint RAG sources and run the RAG build pipeline.")
    build.add_argument("--source-file", action="append", default=[])
    build.add_argument("--source-dir", default=str(SEMANTIC_HINT_BACKUPS))
    build.add_argument("--rag-source-dir", default=str(SOURCE_SEMANTIC_HINTS))
    build.add_argument("--document-type", default=DEFAULT_DOCUMENT_TYPE)
    build.add_argument("--normalized-dir", default=str(GENERATED_NORMALIZED))
    build.add_argument("--chunks-dir", default=str(GENERATED_CHUNKS))
    build.add_argument("--optimized-chunks-dir", default=str(GENERATED_OPTIMIZED_CHUNKS))
    build.add_argument("--indexes-dir", default=str(GENERATED_INDEXES))
    build.add_argument("--embeddings-output", default=str(EMBEDDINGS_INDEX))
    build.add_argument("--output", default=str(DEFAULT_BUILD_OUTPUT))
    build.add_argument("--project", default="ariadne")
    build.add_argument("--repository", default="ariadne-ai-workflow-platform")
    build.add_argument("--branch", default="")
    build.add_argument("--commit", default="")
    build.add_argument("--status", default="approved")
    build.add_argument("--chunk-size", type=int, default=RAG_CHUNK_SIZE_DEFAULT)
    build.add_argument("--chunk-overlap", type=int, default=RAG_CHUNK_OVERLAP_DEFAULT)
    build.add_argument("--embedding-dimensions", type=int, default=RAG_EMBEDDING_DIMENSIONS_DEFAULT)
    build.add_argument("--skip-optimization", action="store_true")
    build.add_argument("--duckdb-migrate", action="store_true")
    build.add_argument("--duckdb-path", default=str(DUCKDB_DEFAULT_PATH))
    build.add_argument("--clean-output", action="store_true")

    read = subparsers.add_parser("read", help="Read generated semantic hints or retrieve RAG context with semantic hints.")
    read.add_argument("--source-dir", default=str(SOURCE_SEMANTIC_HINTS))
    read.add_argument("--backup-dir", default=str(SEMANTIC_HINT_BACKUPS))
    read.add_argument("--query", default="")
    read.add_argument("--semantic-hint", default="")
    read.add_argument("--backend", choices=["source", "file", "duckdb"], default="source")
    read.add_argument("--top-k", type=int, default=RAG_RETRIEVE_TOP_K_DEFAULT)
    read.add_argument("--chunks-index", default=str(CHUNKS_INDEX))
    read.add_argument("--embeddings-index", default=str(EMBEDDINGS_INDEX))
    read.add_argument("--duckdb-path", default=str(DUCKDB_DEFAULT_PATH))
    read.add_argument("--output-dir", default=str(GENERATED_RETRIEVAL))
    read.add_argument("--project", default="")
    return parser


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Semantic hint backup must be a JSON object: {path}")
    return payload


def discover_backup_files(repo_root: Path, source_dir: str, source_files: Sequence[str]) -> list[Path]:
    if source_files:
        return sorted(resolve_repo_path(repo_root, item).resolve() for item in source_files)
    root = resolve_repo_path(repo_root, source_dir).resolve()
    if not root.exists():
        raise FileNotFoundError(f"Semantic hint backup directory not found: {root}")
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def entry_text(entry: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"### {entry.get('id', 'semantic-hint')}",
            "",
            f"- Category: {entry.get('category', '')}",
            f"- Project scope: {entry.get('project_scope', '')}",
            f"- Source path: `{entry.get('source_path', '')}`",
            f"- Source marker: `{entry.get('source_marker', 'semantic_hint')}`",
            "",
            "#### Semantic Hint",
            "",
            str(entry.get("content", "")).strip(),
            "",
            "#### Replacement Summary",
            "",
            str(entry.get("replacement_summary", "")).strip(),
        ]
    ).strip()


def semantic_hint_value(entry: dict[str, Any]) -> str:
    return " ".join(
        str(entry.get(key, "")).strip()
        for key in ("id", "category", "project_scope", "content")
        if str(entry.get(key, "")).strip()
    )


def render_markdown(repo_root: Path, payload: dict[str, Any], source_path: Path, args: argparse.Namespace) -> tuple[str, str]:
    entries = [entry for entry in payload.get("entries", []) if isinstance(entry, dict)]
    if not entries:
        raise ValueError(f"Semantic hint backup has no entries: {source_path}")
    title = payload.get("title") or source_path.stem.replace("-", " ").title()
    hints = [semantic_hint_value(entry) for entry in entries]
    semantic_hint = " | ".join(hint for hint in hints if hint)
    body = "\n\n".join(entry_text(entry) for entry in entries)
    front_matter = {
        "title": str(title),
        "type": DEFAULT_DOCUMENT_TYPE,
        "project": getattr(args, "project", "ariadne"),
        "repository": getattr(args, "repository", "ariadne-ai-workflow-platform"),
        "workflow": "semantic-hints",
        "phase": "knowledge-capture",
        "status": getattr(args, "status", "approved"),
        "created_at": payload.get("created_at") or utc_now_iso(),
        "source": relative_to_repo(repo_root, source_path),
        "semantic_hint": semantic_hint,
        "tags": ["semantic-hint", "project-specific", "knowledge-reuse"],
    }
    front_lines = ["---"]
    for key, value in front_matter.items():
        if isinstance(value, list):
            front_lines.append(f"{key}:")
            front_lines.extend(f"  - {item}" for item in value)
        else:
            escaped = str(value).replace("\n", " ").strip()
            front_lines.append(f"{key}: {escaped}")
    front_lines.append("---")
    markdown = "\n".join(front_lines) + f"\n\n# {title}\n\n{body}\n"
    return markdown, semantic_hint


def output_filename(source_path: Path) -> str:
    return f"{slugify(source_path.stem)}.md"


def clean_markdown_outputs(output_dir: Path) -> None:
    if output_dir.exists():
        for path in output_dir.glob("*.md"):
            if path.name.lower() != "readme.md":
                path.unlink()


def generate(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()
    source_files = discover_backup_files(repo_root, args.source_dir, args.source_file)
    output_dir = resolve_repo_path(repo_root, args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if getattr(args, "clean_output", False):
        clean_markdown_outputs(output_dir)
    generated: list[dict[str, Any]] = []
    for source_path in source_files:
        payload = load_json(source_path)
        markdown, hint = render_markdown(repo_root, payload, source_path, args)
        target = output_dir / output_filename(source_path)
        target.write_text(markdown, encoding="utf-8")
        generated.append(
            {
                "source": relative_to_repo(repo_root, source_path),
                "markdown": relative_to_repo(repo_root, target),
                "entry_count": len([entry for entry in payload.get("entries", []) if isinstance(entry, dict)]),
                "semantic_hint": hint,
            }
        )
    return {
        "status": "completed",
        "artifact_type": "semantic-hints-generate",
        "source_count": len(source_files),
        "generated_count": len(generated),
        "output_dir": relative_to_repo(repo_root, output_dir),
        "generated": generated,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()
    generate_result = generate(
        argparse.Namespace(
            repo_root=str(repo_root),
            source_file=args.source_file,
            source_dir=args.source_dir,
            output_dir=args.rag_source_dir,
            project=args.project,
            repository=args.repository,
            status=args.status,
            clean_output=args.clean_output,
        )
    )
    build_result = rag_build.run(
        argparse.Namespace(
            repo_root=str(repo_root),
            work_id="",
            work_dir="",
            source_dir=args.rag_source_dir,
            document_type=args.document_type,
            normalized_dir=args.normalized_dir,
            chunks_dir=args.chunks_dir,
            optimized_chunks_dir=args.optimized_chunks_dir,
            indexes_dir=args.indexes_dir,
            embeddings_output=args.embeddings_output,
            output=args.output,
            ingestion_evidence_dir="db/rag/evidence/ingestion",
            ingestion_policy="runtime/rag/policies/knowledge-ingestion-policy.json",
            skip_optimization=args.skip_optimization,
            duckdb_migrate=args.duckdb_migrate,
            duckdb_path=args.duckdb_path,
            duckdb_source_dir="",
            duckdb_error_log="db/rag/migration-errors.jsonl",
            duckdb_evidence_output="db/rag/evidence/migration-summary.json",
            duckdb_policy="",
            project=args.project,
            repository=args.repository,
            branch=args.branch,
            commit=args.commit,
            status=args.status,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            embedding_dimensions=args.embedding_dimensions,
            clean_output=args.clean_output,
            standardize_filenames=False,
            skip_standardize=True,
            replace_references=False,
            random_length=RAG_STANDARDIZE_RANDOM_LENGTH_DEFAULT,
        )
    )
    return {
        "status": "completed",
        "artifact_type": "semantic-hints-build",
        "generated": generate_result,
        "rag_build": build_result,
        "rag_build_run": build_result.get("rag_build_run", ""),
        "document_count": build_result.get("document_count", 0),
        "chunk_count": build_result.get("chunk_count", 0),
    }


def read_source_hints(repo_root: Path, source_dir: str, backup_dir: str) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    for path in sorted(resolve_repo_path(repo_root, backup_dir).rglob("*.json")) if resolve_repo_path(repo_root, backup_dir).exists() else []:
        payload = load_json(path)
        for entry in payload.get("entries", []):
            if isinstance(entry, dict):
                hints.append(
                    {
                        "id": entry.get("id", ""),
                        "category": entry.get("category", ""),
                        "project_scope": entry.get("project_scope", ""),
                        "content": entry.get("content", ""),
                        "source_path": entry.get("source_path", ""),
                        "backup": relative_to_repo(repo_root, path),
                    }
                )
    for path in sorted(resolve_repo_path(repo_root, source_dir).glob("*.md")) if resolve_repo_path(repo_root, source_dir).exists() else []:
        text = path.read_text(encoding="utf-8-sig")
        hints.append(
            {
                "id": path.stem,
                "category": DEFAULT_DOCUMENT_TYPE,
                "project_scope": "",
                "content": text[:1000],
                "source_path": relative_to_repo(repo_root, path),
                "backup": "",
            }
        )
    return hints


def read(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if getattr(args, "repo_root", "") else find_repo_root()
    if args.backend == "source":
        hints = read_source_hints(repo_root, args.source_dir, args.backup_dir)
        query = (args.query or args.semantic_hint).strip().lower()
        if query:
            hints = [hint for hint in hints if query in json.dumps(hint, ensure_ascii=False).lower()]
        return {
            "status": "completed",
            "artifact_type": "semantic-hints-read",
            "backend": "source",
            "hint_count": len(hints),
            "hints": hints[: args.top_k],
        }
    result = retrieve_context.run(
        argparse.Namespace(
            repo_root=str(repo_root),
            backend=args.backend,
            query=args.query or args.semantic_hint,
            semantic_hint=args.semantic_hint,
            document_type=DEFAULT_DOCUMENT_TYPE,
            chunks_index=args.chunks_index,
            embeddings_index=args.embeddings_index,
            duckdb_path=args.duckdb_path,
            output_dir=args.output_dir,
            top_k=args.top_k,
            max_chars=RAG_RETRIEVE_MAX_CHARS_DEFAULT,
            search_mode="hybrid",
            repository="",
            branch="",
            project=getattr(args, "project", ""),
            workflow="semantic-hints",
            tag=["semantic-hint"],
            source_type="",
            category="",
            trust_level="",
            environment="",
            min_reliability=None,
            min_freshness=None,
            context_file=[],
            json=True,
            write_markdown=False,
        )
    )
    return {
        "status": "completed",
        "artifact_type": "semantic-hints-read",
        "backend": args.backend,
        "retrieval": result,
    }


RUNNERS = {
    "generate": generate,
    "build": build,
    "read": read,
}


def run(args: argparse.Namespace) -> dict[str, Any]:
    command = getattr(args, "semantic_hints_command", "")
    if command not in RUNNERS:
        raise KeyError(command)
    return RUNNERS[command](args)


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
