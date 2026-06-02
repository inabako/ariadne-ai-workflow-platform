from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, local_timestamp, read_json, relative_to_repo, slugify, utc_now_iso, write_json  # noqa: E402


DEFAULT_QUERIES = [
    "architecture responsibility boundary corrective action",
    "STOP shutdown safe state communication loss",
    "test gap documentation gap observability rollback",
]

SAFETY_TERMS = [
    "STOP",
    "safe state",
    "shutdown",
    "startup",
    "communication loss",
    "rollback",
    "telemetry",
    "watchdog",
    "observability",
    "operator",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dispatch parallel RAG retrieval queries and aggregate compressed context packs."
    )
    parser.add_argument("--query", action="append", default=[], help="Explicit retrieval query. Can be repeated.")
    parser.add_argument("--task", default="", help="Task summary used to derive queries when --query is omitted.")
    parser.add_argument("--context-file", action="append", default=[], help="Markdown/JSON context file for query planning.")
    parser.add_argument("--work-dir", default="", help="Workflow work/<receipt-id> directory to scan for planning context.")
    parser.add_argument("--repository", default="", help="Optional retrieval filter.")
    parser.add_argument("--branch", default="", help="Optional retrieval filter.")
    parser.add_argument("--project", default="", help="Optional retrieval filter.")
    parser.add_argument("--tag", action="append", default=[], help="Optional retrieval tag filter. Can be repeated.")
    parser.add_argument("--chunks-index", default="rag/indexes/chunks.jsonl")
    parser.add_argument("--embeddings-index", default="rag/embeddings/chunks-embeddings.jsonl")
    parser.add_argument("--output-dir", default="rag/retrieval")
    parser.add_argument("--search-mode", default="hybrid", choices=["keyword", "semantic", "hybrid"])
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--max-chars", type=int, default=4000)
    parser.add_argument("--max-queries", type=int, default=5)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--aggregate-max-chars", type=int, default=12000)
    parser.add_argument("--build-if-missing", action="store_true")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--python", default=sys.executable)
    return parser


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def read_text_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def collect_work_context(work_dir: Path) -> str:
    if not work_dir.exists():
        return ""
    parts: list[str] = []
    for pattern in [
        "design-document/*.md",
        "process-report/*.md",
        "context/*.json",
    ]:
        for path in sorted(work_dir.glob(pattern)):
            text = read_text_file(path)
            if text:
                parts.append(f"# {path.name}\n{text}")
    return "\n\n".join(parts)


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = " ".join(value.split()).strip()
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def extract_component_terms(text: str) -> list[str]:
    import re

    candidates: list[str] = []
    candidates.extend(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]+\.py\b", text))
    candidates.extend(re.findall(r"\b[A-Z][A-Za-z0-9]*(?:Window|Service|Session|Controller|Client|Widget|Logic|Receiver)\b", text))
    candidates.extend(re.findall(r"\b[A-Za-z0-9_-]*(?:telemetry|watchdog|gstreamer|discovery|control|video)[A-Za-z0-9_-]*\b", text, flags=re.IGNORECASE))
    return unique_keep_order(candidates)[:8]


def derive_queries(args: argparse.Namespace, repo_root: Path) -> list[str]:
    explicit = unique_keep_order([str(query) for query in args.query if str(query).strip()])
    if explicit:
        return explicit[: args.max_queries]

    context_parts = [args.task]
    for value in args.context_file:
        context_parts.append(read_text_file(resolve_path(repo_root, value)))
    if args.work_dir:
        context_parts.append(collect_work_context(resolve_path(repo_root, args.work_dir)))

    context = "\n\n".join(part for part in context_parts if part)
    components = extract_component_terms(context)
    queries: list[str] = []

    repo_branch = " ".join(part for part in [args.repository, args.branch] if part)
    if repo_branch:
        queries.append(f"{repo_branch} corrective action report")

    if components:
        queries.append(" ".join(components[:4]) + " architecture responsibility boundary")
        queries.append(" ".join(components[:4]) + " test gap refactor")

    lower_context = context.lower()
    safety_hits = [term for term in SAFETY_TERMS if term.lower() in lower_context]
    if safety_hits:
        queries.append(" ".join(safety_hits[:5]) + " safety risk corrective action")
    else:
        queries.append(DEFAULT_QUERIES[1])

    if "test" in lower_context or "pytest" in lower_context or "ci" in lower_context:
        queries.append("test gap CI regression smoke integration")

    if "documentation" in lower_context or "docs" in lower_context or "README" in context:
        queries.append("documentation gap operations README corrective action")

    queries.extend(DEFAULT_QUERIES)
    return unique_keep_order(queries)[: args.max_queries]


def run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result: dict[str, Any] = {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode == 0 and completed.stdout.strip():
        try:
            result["json"] = json.loads(completed.stdout)
        except json.JSONDecodeError:
            result["json"] = None
    return result


def ensure_indexes(args: argparse.Namespace, repo_root: Path) -> None:
    chunks_index = resolve_path(repo_root, args.chunks_index)
    embeddings_index = resolve_path(repo_root, args.embeddings_index)
    missing = [path for path in [chunks_index, embeddings_index] if not path.exists()]
    if not missing:
        return
    if not args.build_if_missing:
        missing_text = ", ".join(relative_to_repo(repo_root, path) for path in missing)
        raise FileNotFoundError(f"RAG index files are missing: {missing_text}. Run /rag-build first.")

    build_commands = [
        [
            args.python,
            "runtime/rag/normalize_documents.py",
            "--source-dir",
            "rag/corrective-action-report",
            "--output-dir",
            "rag/normalized",
            "--document-type",
            "corrective-action-report",
        ],
        [args.python, "runtime/rag/chunk_documents.py", "--input-dir", "rag/normalized", "--output-dir", "rag/chunks"],
        [
            args.python,
            "runtime/rag/build_index.py",
            "--normalized-dir",
            "rag/normalized",
            "--chunks-dir",
            "rag/chunks",
            "--output-dir",
            "rag/indexes",
        ],
        [
            args.python,
            "runtime/rag/embed_chunks.py",
            "--chunks-index",
            "rag/indexes/chunks.jsonl",
            "--output",
            "rag/embeddings/chunks-embeddings.jsonl",
        ],
    ]
    for command in build_commands:
        result = run_command(command, repo_root)
        if result["returncode"] != 0:
            raise RuntimeError(f"RAG build stage failed: {' '.join(command)}\n{result['stderr']}")


def retrieval_command(args: argparse.Namespace, query: str) -> list[str]:
    command = [
        args.python,
        "runtime/rag/retrieve_context.py",
        query,
        "--chunks-index",
        args.chunks_index,
        "--embeddings-index",
        args.embeddings_index,
        "--output-dir",
        args.output_dir,
        "--search-mode",
        args.search_mode,
        "--top-k",
        str(args.top_k),
        "--max-chars",
        str(args.max_chars),
    ]
    for option in ["project", "repository", "branch"]:
        value = getattr(args, option)
        if value:
            command.extend([f"--{option}", value])
    for tag in args.tag:
        command.extend(["--tag", tag])
    return command


def run_retrievals(args: argparse.Namespace, repo_root: Path, queries: list[str]) -> list[dict[str, Any]]:
    max_workers = max(1, min(args.jobs, len(queries)))
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_command, retrieval_command(args, query), repo_root): query
            for query in queries
        }
        for future in as_completed(futures):
            query = futures[future]
            result = future.result()
            result["query"] = query
            results.append(result)
    results.sort(key=lambda item: queries.index(str(item.get("query", ""))))
    return results


def load_context_pack(repo_root: Path, path_value: str) -> dict[str, Any]:
    path = resolve_path(repo_root, path_value)
    data = read_json(path, default={})
    return data if isinstance(data, dict) else {}


def aggregate_context_packs(repo_root: Path, retrievals: list[dict[str, Any]], max_chars: int) -> tuple[str, list[dict[str, Any]]]:
    sections: list[str] = []
    sources: list[dict[str, Any]] = []
    remaining = max_chars
    seen_sources: set[str] = set()

    for result in retrievals:
        payload = result.get("json") if isinstance(result.get("json"), dict) else {}
        context_pack_path = str(payload.get("context_pack", ""))
        if not context_pack_path:
            continue
        pack = load_context_pack(repo_root, context_pack_path)
        context = str(pack.get("context", "")).strip()
        if not context:
            continue
        header = f"## Query: {result.get('query', '')}\n\nContext Pack: `{context_pack_path}`"
        section = f"{header}\n\n{context}".strip()
        if len(section) > remaining:
            section = section[: max(0, remaining - 20)].rstrip() + "\n\n[truncated]"
        if section:
            sections.append(section)
            remaining -= len(section) + 2
        for source in pack.get("sources", []):
            key = str(source.get("chunk_id") or source.get("source_path") or source)
            if key in seen_sources:
                continue
            seen_sources.add(key)
            sources.append(source)
        if remaining <= 200:
            break
    return "\n\n".join(sections).strip(), sources


def write_dispatch_markdown(path: Path, data: dict[str, Any]) -> None:
    query_lines = "\n".join(f"- {query}" for query in data.get("queries", []))
    pack_lines = "\n".join(
        f"- `{item.get('context_markdown', '')}` ({item.get('selected_chunk_count', 0)} chunks)"
        for item in data.get("context_packs", [])
    )
    text = f"""# RAG Load Dispatch Summary

Created At: `{data.get('created_at', '')}`

Search Mode: `{data.get('search_mode', '')}`

## Queries

{query_lines}

## Context Packs

{pack_lines}

## Aggregate Compressed Context

{data.get('aggregate_context', '')}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.max_queries <= 0:
        raise ValueError("--max-queries must be positive.")
    if args.jobs <= 0:
        raise ValueError("--jobs must be positive.")

    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    ensure_indexes(args, repo_root)
    queries = derive_queries(args, repo_root)
    if not queries:
        raise ValueError("No RAG queries were provided or derived.")

    retrievals = run_retrievals(args, repo_root, queries)
    failures = [item for item in retrievals if int(item.get("returncode", 1)) != 0]
    if failures:
        first = failures[0]
        raise RuntimeError(f"RAG retrieval failed for query '{first.get('query')}': {first.get('stderr', '')}")

    context_packs: list[dict[str, Any]] = []
    for item in retrievals:
        payload = item.get("json") if isinstance(item.get("json"), dict) else {}
        context_packs.append(
            {
                "query": item.get("query", ""),
                "retrieval_result": payload.get("retrieval_result", ""),
                "context_pack": payload.get("context_pack", ""),
                "context_markdown": payload.get("context_markdown", ""),
                "candidate_count": payload.get("candidate_count", 0),
                "selected_chunk_count": payload.get("selected_chunk_count", 0),
                "estimated_tokens": payload.get("estimated_tokens", 0),
            }
        )

    aggregate_context, sources = aggregate_context_packs(repo_root, retrievals, args.aggregate_max_chars)
    output_dir = resolve_path(repo_root, args.output_dir)
    timestamp = local_timestamp()
    base_name = f"{timestamp}_rag-load-dispatch"
    json_path = output_dir / f"{base_name}.json"
    markdown_path = output_dir / f"{base_name}.md"
    result = {
        "schema_version": "1.0",
        "created_at": utc_now_iso(),
        "queries": queries,
        "search_mode": args.search_mode,
        "filters": {
            "project": args.project,
            "repository": args.repository,
            "branch": args.branch,
            "tags": args.tag,
        },
        "context_packs": context_packs,
        "aggregate_context": aggregate_context,
        "sources": sources,
    }
    write_json(json_path, result)
    write_dispatch_markdown(markdown_path, result)
    return {
        "dispatch_result": relative_to_repo(repo_root, json_path),
        "dispatch_markdown": relative_to_repo(repo_root, markdown_path),
        "query_count": len(queries),
        "context_pack_count": len(context_packs),
        "source_count": len(sources),
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
