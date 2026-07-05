from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.workflow.context_first import context_entry, context_path, load_manifest, manifest_path_for_work_dir, register_context  # noqa: E402


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
    parser.add_argument("--workflow", default="", help="Optional workflow name for dispatch planning evidence.")
    parser.add_argument("--work-id", default="", help="Optional work/issue identifier for dispatch planning evidence.")
    parser.add_argument("--context-file", action="append", default=[], help="Markdown/JSON context file for query planning.")
    parser.add_argument("--work-dir", default="", help="Workflow work/<receipt-id> directory to scan for planning context.")
    parser.add_argument("--dispatch-plan", default="", help="Existing rag-dispatch-plan JSON to execute.")
    parser.add_argument("--repository", default="", help="Optional retrieval filter.")
    parser.add_argument("--branch", default="", help="Optional retrieval filter.")
    parser.add_argument("--project", default="", help="Optional retrieval filter.")
    parser.add_argument("--tag", action="append", default=[], help="Optional retrieval tag filter. Can be repeated.")
    parser.add_argument("--source-type", default="", help="Optional source_type filter, e.g. external-web or internal-work.")
    parser.add_argument("--category", default="", help="Optional external-web category filter.")
    parser.add_argument("--trust-level", default="", help="Optional trust_level filter.")
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
    parser.add_argument("--write-markdown", action="store_true")
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


def default_work_dir(repo_root: Path, args: argparse.Namespace) -> Path | None:
    if args.work_dir:
        return resolve_path(repo_root, args.work_dir)
    if args.work_id:
        return repo_root / "work" / args.work_id
    return None


def execution_plan_reference(repo_root: Path, work_dir: Path | None) -> str:
    if work_dir is None:
        return ""
    manifest_path = manifest_path_for_work_dir(work_dir)
    if manifest_path.exists():
        manifest = load_manifest(work_dir)
        entry = context_entry(manifest, "execution-plan")
        if entry:
            return relative_to_repo(repo_root, context_path(repo_root, entry))
    fallback = work_dir / "context" / "execution-plan.json"
    return relative_to_repo(repo_root, fallback) if fallback.exists() else ""


def execution_plan_gate(repo_root: Path, args: argparse.Namespace, work_dir: Path | None) -> dict[str, Any]:
    if not args.work_id:
        return {
            "status": "not-required",
            "human_check_required": False,
            "execution_plan": "",
            "reason": "work-id was not provided",
        }
    execution_plan = execution_plan_reference(repo_root, work_dir)
    if execution_plan:
        return {
            "status": "ready",
            "human_check_required": False,
            "execution_plan": execution_plan,
            "reason": "",
        }
    return {
        "status": "human-check-required",
        "human_check_required": True,
        "execution_plan": "",
        "reason": "work-id was provided but execution-plan context was not found",
        "human_check_reasons": [
            "Confirm the RAG query plan manually because execution-plan context is missing.",
        ],
    }


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


def collect_planning_context(args: argparse.Namespace, repo_root: Path) -> str:
    context_parts = [args.task]
    for value in args.context_file:
        context_parts.append(read_text_file(resolve_path(repo_root, value)))
    if args.work_dir:
        context_parts.append(collect_work_context(resolve_path(repo_root, args.work_dir)))
    return "\n\n".join(part for part in context_parts if part)


def base_filters_from_args(args: argparse.Namespace) -> dict[str, Any]:
    filters: dict[str, Any] = {
        "project": args.project,
        "repository": args.repository,
        "branch": args.branch,
        "tags": args.tag,
        "source_type": args.source_type,
        "category": args.category,
        "trust_level": args.trust_level,
    }
    return filters


def append_query(query_items: list[dict[str, Any]], query: str, purpose: str, args: argparse.Namespace) -> None:
    normalized = " ".join(query.split()).strip()
    if not normalized:
        return
    query_items.append(
        {
            "query": normalized,
            "purpose": purpose,
            "search_mode": args.search_mode,
            "filters": base_filters_from_args(args),
        }
    )


def derive_query_items(args: argparse.Namespace, repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    explicit = unique_keep_order([str(query) for query in args.query if str(query).strip()])
    if explicit:
        query_items: list[dict[str, Any]] = []
        for query in explicit[: args.max_queries]:
            append_query(query_items, query, "explicit user-provided retrieval query", args)
        return query_items, explicit[: args.max_queries]

    context = collect_planning_context(args, repo_root)
    components = extract_component_terms(context)
    query_items = []
    semantic_hints: list[str] = []
    semantic_hints.extend(components)

    repo_branch = " ".join(part for part in [args.repository, args.branch] if part)
    if repo_branch:
        append_query(query_items, f"{repo_branch} corrective action report", "target repository and branch history", args)

    if components:
        append_query(
            query_items,
            " ".join(components[:4]) + " architecture responsibility boundary",
            "component responsibility and architecture boundary",
            args,
        )
        append_query(query_items, " ".join(components[:4]) + " test gap refactor", "component test and regression risk", args)

    lower_context = context.lower()
    safety_hits = [term for term in SAFETY_TERMS if term.lower() in lower_context]
    semantic_hints.extend(safety_hits)
    if safety_hits:
        append_query(
            query_items,
            " ".join(safety_hits[:5]) + " safety risk corrective action",
            "safety, STOP, rollback, or operational risk",
            args,
        )
    else:
        append_query(query_items, DEFAULT_QUERIES[1], "default safety and communication-loss baseline", args)

    if "test" in lower_context or "pytest" in lower_context or "ci" in lower_context:
        append_query(query_items, "test gap CI regression smoke integration", "test gap and CI regression history", args)

    if "documentation" in lower_context or "docs" in lower_context or "README" in context:
        append_query(
            query_items,
            "documentation gap operations README corrective action",
            "documentation and operations gap history",
            args,
        )

    for query in DEFAULT_QUERIES:
        append_query(query_items, query, "default corrective-action retrieval baseline", args)
    return dedupe_query_items(query_items)[: args.max_queries], unique_keep_order(semantic_hints)


def dedupe_query_items(query_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in query_items:
        query = " ".join(str(item.get("query", "")).split()).strip()
        key = query.lower()
        if not query or key in seen:
            continue
        seen.add(key)
        item["query"] = query
        result.append(item)
    return result


def normalize_plan_query_items(plan: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    metadata = plan.get("metadata", {}) if isinstance(plan.get("metadata"), dict) else {}
    base_filters = {
        "project": metadata.get("project", ""),
        "repository": metadata.get("repository", ""),
        "branch": metadata.get("branch", ""),
        "tags": metadata.get("tags", []),
        "source_type": metadata.get("source_type", ""),
        "category": metadata.get("category", ""),
        "trust_level": metadata.get("trust_level", ""),
    }
    query_items: list[dict[str, Any]] = []
    for item in plan.get("queries", []):
        if isinstance(item, str):
            query_items.append(
                {
                    "query": item,
                    "purpose": "legacy string query from dispatch plan",
                    "search_mode": args.search_mode,
                    "filters": base_filters,
                }
            )
            continue
        if not isinstance(item, dict):
            continue
        filters = {**base_filters}
        item_filters = item.get("filters", {}) if isinstance(item.get("filters"), dict) else {}
        for key, value in item_filters.items():
            if value not in ("", None) and value != []:
                filters[key] = value
        query_items.append(
            {
                "query": item.get("query", ""),
                "purpose": item.get("purpose", ""),
                "search_mode": item.get("search_mode") or plan.get("search_mode") or args.search_mode,
                "filters": filters,
            }
        )
    return dedupe_query_items(query_items)[: args.max_queries]


def build_dispatch_plan(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    if args.dispatch_plan:
        data = read_json(resolve_path(repo_root, args.dispatch_plan), default={})
        if not isinstance(data, dict):
            raise ValueError(f"Invalid dispatch plan: {args.dispatch_plan}")
        if data.get("artifact_type") != "rag-dispatch-plan":
            raise ValueError(f"Dispatch plan artifact_type must be rag-dispatch-plan: {args.dispatch_plan}")
        data.setdefault("schema_version", "1.0")
        data.setdefault("plan_id", str(uuid.uuid4()))
        data.setdefault("queries", [])
        if args.work_id and "execution_plan_gate" not in data:
            gate = execution_plan_gate(repo_root, args, default_work_dir(repo_root, args))
            if data.get("execution_plan") and not gate.get("execution_plan"):
                gate = {
                    "status": "ready",
                    "human_check_required": False,
                    "execution_plan": str(data.get("execution_plan", "")),
                    "reason": "execution-plan was provided by the existing dispatch plan",
                }
            data.setdefault("execution_plan", gate.get("execution_plan", ""))
            data["execution_plan_gate"] = gate
            data["human_check_required"] = bool(gate.get("human_check_required", False))
            data["human_check_reasons"] = gate.get("human_check_reasons", [])
        return data

    query_items, semantic_hints = derive_query_items(args, repo_root)
    work_dir = default_work_dir(repo_root, args)
    gate = execution_plan_gate(repo_root, args, work_dir)
    execution_plan = str(gate.get("execution_plan", ""))
    return {
        "schema_version": "1.0",
        "artifact_type": "rag-dispatch-plan",
        "plan_id": str(uuid.uuid4()),
        "created_at": utc_now_iso(),
        "workflow": args.workflow,
        "work_id": args.work_id,
        "intent": args.task,
        "task": args.task,
        "planning_method": "explicit-query" if args.query else "task-context-heuristic",
        "metadata": base_filters_from_args(args),
        "semantic_hints": semantic_hints,
        "queries": query_items,
        "stop_conditions": [
            "RAG indexes are missing",
            "safety-critical prior finding is relevant to the current task",
            "retrieval returns no useful context for a critical unknown",
        ],
        "inputs": {
            "context_files": args.context_file,
            "work_dir": args.work_dir,
            "execution_plan": execution_plan,
        },
        "execution_plan": execution_plan,
        "execution_plan_gate": gate,
        "human_check_required": bool(gate.get("human_check_required", False)),
        "human_check_reasons": gate.get("human_check_reasons", []),
    }


def write_dispatch_plan(repo_root: Path, output_dir: Path, plan: dict[str, Any], source_path: str) -> str:
    if source_path:
        return relative_to_repo(repo_root, resolve_path(repo_root, source_path))
    plan_id = str(plan.get("plan_id") or uuid.uuid4())
    plan["plan_id"] = plan_id
    plan_path = output_dir / f"{plan_id}.json"
    write_json(plan_path, plan)
    return relative_to_repo(repo_root, plan_path)


def register_rag_contexts(
    repo_root: Path,
    args: argparse.Namespace,
    *,
    dispatch_plan_path: str,
    dispatch_result_path: str = "",
) -> None:
    work_dir = default_work_dir(repo_root, args)
    if work_dir is None or not args.work_id:
        return
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True, exist_ok=True)
    register_context(
        repo_root,
        work_dir,
        work_id=args.work_id,
        context_type="rag-dispatch-plan",
        path=resolve_path(repo_root, dispatch_plan_path),
        required=False,
        generated_by="rag-load",
        owner="workflow",
        schema=".github/schemas/rag-dispatch-plan.schema.json",
    )
    if dispatch_result_path:
        register_context(
            repo_root,
            work_dir,
            work_id=args.work_id,
            context_type="rag-load-dispatch",
            path=resolve_path(repo_root, dispatch_result_path),
            required=False,
            generated_by="rag-load",
            owner="workflow",
            schema=".github/schemas/rag-load-dispatch.schema.json",
        )


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
            "--clean-output",
        ],
        [
            args.python,
            "runtime/rag/chunk_documents.py",
            "--input-dir",
            "rag/normalized",
            "--output-dir",
            "rag/chunks",
            "--clean-output",
        ],
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


def retrieval_command(args: argparse.Namespace, query_item: dict[str, Any]) -> list[str]:
    query = str(query_item.get("query", ""))
    filters = query_item.get("filters", {}) if isinstance(query_item.get("filters"), dict) else {}
    search_mode = str(query_item.get("search_mode") or args.search_mode)
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
        search_mode,
        "--top-k",
        str(args.top_k),
        "--max-chars",
        str(args.max_chars),
    ]
    for option in ["project", "repository", "branch"]:
        value = filters.get(option, getattr(args, option))
        if value:
            command.extend([f"--{option}", value])
    for option in ["source_type", "category", "trust_level"]:
        value = filters.get(option, getattr(args, option))
        if value:
            command.extend([f"--{option.replace('_', '-')}", value])
    tags = filters.get("tags", args.tag)
    for tag in tags if isinstance(tags, list) else [tags]:
        command.extend(["--tag", tag])
    if args.write_markdown:
        command.append("--write-markdown")
    return command


def run_retrievals(args: argparse.Namespace, repo_root: Path, query_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    max_workers = max(1, min(args.jobs, len(query_items)))
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_command, retrieval_command(args, query_item), repo_root): query_item
            for query_item in query_items
        }
        for future in as_completed(futures):
            query_item = futures[future]
            result = future.result()
            result["query"] = query_item.get("query", "")
            result["purpose"] = query_item.get("purpose", "")
            result["search_mode"] = query_item.get("search_mode", args.search_mode)
            result["filters"] = query_item.get("filters", {})
            results.append(result)
    order = {str(item.get("query", "")): index for index, item in enumerate(query_items)}
    results.sort(key=lambda item: order.get(str(item.get("query", "")), 0))
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
    query_lines = "\n".join(
        f"- {item.get('query', '')}: {item.get('purpose', '')}"
        for item in data.get("queries", [])
        if isinstance(item, dict)
    )
    pack_lines = "\n".join(
        f"- `{item.get('context_markdown', '')}` ({item.get('selected_chunk_count', 0)} chunks)"
        for item in data.get("context_packs", [])
    )
    text = f"""# RAG Load Dispatch Summary

Created At: `{data.get('created_at', '')}`

Dispatch Plan: `{data.get('dispatch_plan', '')}`

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
    output_dir = resolve_path(repo_root, args.output_dir)
    plan = build_dispatch_plan(args, repo_root)
    query_items = normalize_plan_query_items(plan, args)
    if not query_items:
        raise ValueError("No RAG queries were provided or derived.")
    dispatch_plan_path = write_dispatch_plan(repo_root, output_dir, plan, args.dispatch_plan)
    register_rag_contexts(repo_root, args, dispatch_plan_path=dispatch_plan_path)
    ensure_indexes(args, repo_root)

    retrievals = run_retrievals(args, repo_root, query_items)
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
                "purpose": item.get("purpose", ""),
                "search_mode": item.get("search_mode", args.search_mode),
                "filters": item.get("filters", {}),
                "retrieval_result": payload.get("retrieval_result", ""),
                "context_pack": payload.get("context_pack", ""),
                "context_markdown": payload.get("context_markdown", ""),
                "candidate_count": payload.get("candidate_count", 0),
                "selected_chunk_count": payload.get("selected_chunk_count", 0),
                "estimated_tokens": payload.get("estimated_tokens", 0),
            }
        )

    aggregate_context, sources = aggregate_context_packs(repo_root, retrievals, args.aggregate_max_chars)
    dispatch_id = str(uuid.uuid4())
    json_path = output_dir / f"{dispatch_id}.json"
    markdown_path = output_dir / f"{dispatch_id}.md"
    result = {
        "schema_version": "1.0",
        "artifact_type": "rag-load-dispatch",
        "dispatch_id": dispatch_id,
        "dispatch_plan_id": plan.get("plan_id", ""),
        "dispatch_plan": dispatch_plan_path,
        "created_at": utc_now_iso(),
        "queries": query_items,
        "search_mode": args.search_mode,
        "filters": plan.get("metadata", base_filters_from_args(args)),
        "execution_plan": plan.get("execution_plan", ""),
        "execution_plan_gate": plan.get("execution_plan_gate", {}),
        "human_check_required": bool(plan.get("human_check_required", False)),
        "human_check_reasons": plan.get("human_check_reasons", []),
        "context_packs": context_packs,
        "aggregate_context": aggregate_context,
        "sources": sources,
    }
    write_json(json_path, result)
    dispatch_result_path = relative_to_repo(repo_root, json_path)
    register_rag_contexts(
        repo_root,
        args,
        dispatch_plan_path=dispatch_plan_path,
        dispatch_result_path=dispatch_result_path,
    )
    if args.write_markdown:
        write_dispatch_markdown(markdown_path, result)
    return {
        "dispatch_plan": dispatch_plan_path,
        "dispatch_result": dispatch_result_path,
        "dispatch_markdown": relative_to_repo(repo_root, markdown_path) if args.write_markdown else "",
        "execution_plan": plan.get("execution_plan", ""),
        "execution_plan_gate": plan.get("execution_plan_gate", {}),
        "human_check_required": bool(plan.get("human_check_required", False)),
        "query_count": len(query_items),
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
