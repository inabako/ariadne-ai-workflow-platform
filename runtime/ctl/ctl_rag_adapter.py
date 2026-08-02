from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from runtime.ctl.ctl_adapter_utils import workflow_args
from runtime.rag import (
    build_index,
    chunk_documents,
    embed_chunks,
    ingestion_optimizer,
    jsonize_rag_tree,
    migrate_legacy_root_rag,
    migrate_retrieval_artifacts,
    normalize_documents,
    rag_build,
    rag_dispatcher,
    retrieve_context,
    semantic_hints,
    standardize_corrective_report_names,
)


RAG_RUNNERS: dict[str, Callable[[argparse.Namespace], dict[str, Any]]] = {
    "build": rag_build.run,
    "load": rag_dispatcher.run,
    "retrieve": retrieve_context.run,
    "normalize": normalize_documents.run,
    "chunk": chunk_documents.run,
    "index": build_index.run,
    "embed": embed_chunks.run,
    "optimize": ingestion_optimizer.run,
    "standardize": standardize_corrective_report_names.run,
    "jsonize": jsonize_rag_tree.run,
    "migrate-retrieval": migrate_retrieval_artifacts.run,
    "migrate-legacy-root": migrate_legacy_root_rag.migrate_legacy_root_rag,
    "semantic-hints": semantic_hints.run,
}


def _value(args: argparse.Namespace, name: str) -> Any:
    return getattr(args, name, "")


def _path_value(args: argparse.Namespace, name: str) -> str:
    value = _value(args, name)
    return str(value).replace("\\", "/") if value not in {None, ""} else ""


def _paths_from_args(args: argparse.Namespace, names: list[str]) -> list[dict[str, str]]:
    paths: list[dict[str, str]] = []
    for name in names:
        value = _path_value(args, name)
        if value:
            paths.append({"role": name.replace("_", "-"), "path": value})
    return paths


def _source_files_from_args(args: argparse.Namespace) -> list[dict[str, str]]:
    reads: list[dict[str, str]] = []
    for item in getattr(args, "source_file", []) or []:
        reads.append({"role": "source-file", "path": str(item).replace("\\", "/")})
    return reads


def rag_dry_run_plan(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    dry_args = workflow_args(args, repo_root, command)
    effective_command = f"rag {command}"
    if command == "semantic-hints":
        semantic_command = getattr(args, "semantic_hints_command", "") or ""
        effective_command = f"rag semantic-hints {semantic_command}".rstrip()

    read_names: list[str] = []
    write_names: list[str] = []
    if command == "build":
        read_names = ["source_dir", "ingestion_policy"]
        write_names = ["normalized_dir", "chunks_dir", "indexes_dir", "embeddings_output", "output", "ingestion_evidence_dir"]
    elif command == "normalize":
        read_names = ["source_dir"]
        write_names = ["output_dir"]
    elif command == "chunk":
        read_names = ["input_dir"]
        write_names = ["output_dir"]
    elif command == "index":
        read_names = ["normalized_dir", "chunks_dir"]
        write_names = ["output_dir"]
    elif command == "embed":
        read_names = ["chunks_index"]
        write_names = ["output"]
    elif command == "optimize":
        read_names = ["chunks_dir", "policy"]
        write_names = ["output_dir", "evidence_dir"]
    elif command == "standardize":
        read_names = ["source_dir"]
        write_names = ["source_dir"]
    elif command == "jsonize":
        read_names = ["rag_dir"]
        write_names = ["output_dir"]
    elif command == "migrate-retrieval":
        read_names = ["retrieval_dir", "jsonized_dir"]
        write_names = ["jsonized_dir"]
    elif command == "migrate-legacy-root":
        read_names = ["legacy_dir"]
        write_names = ["target_rag_dir"]
    elif command == "semantic-hints":
        semantic_command = getattr(dry_args, "semantic_hints_command", "")
        if semantic_command == "generate":
            read_names = ["source_dir"]
            write_names = ["output_dir"]
        elif semantic_command == "build":
            read_names = ["source_dir"]
            write_names = ["rag_source_dir", "normalized_dir", "chunks_dir", "indexes_dir", "embeddings_output", "output"]

    reads = _paths_from_args(dry_args, read_names) + _source_files_from_args(dry_args)
    writes = _paths_from_args(dry_args, write_names)
    if command == "build":
        writes.append({"role": "rag-build-run", "path": _path_value(dry_args, "output")})
        if not getattr(dry_args, "skip_optimization", False):
            writes.append({"role": "optimized-chunks-dir", "path": _path_value(dry_args, "optimized_chunks_dir")})
        if getattr(dry_args, "duckdb_migrate", False):
            reads.extend(_paths_from_args(dry_args, ["duckdb_source_dir", "duckdb_policy"]))
            writes.extend(_paths_from_args(dry_args, ["duckdb_path", "duckdb_error_log", "duckdb_evidence_output"]))
        if getattr(dry_args, "standardize_filenames", False) and not getattr(dry_args, "skip_standardize", False):
            writes.append({"role": "standardized-source-dir", "path": _path_value(dry_args, "source_dir")})
    if command == "semantic-hints" and getattr(dry_args, "semantic_hints_command", "") == "build":
        writes.append({"role": "generated-semantic-hint-source", "path": _path_value(dry_args, "rag_source_dir")})
        if not getattr(dry_args, "skip_optimization", False):
            writes.append({"role": "optimized-chunks-dir", "path": _path_value(dry_args, "optimized_chunks_dir")})
        if getattr(dry_args, "duckdb_migrate", False):
            writes.append({"role": "duckdb-path", "path": _path_value(dry_args, "duckdb_path")})
    if getattr(dry_args, "clean_output", False):
        writes.append({"role": "clean-output", "path": "enabled"})
    if getattr(dry_args, "delete_source", False):
        writes.append({"role": "delete-source", "path": "enabled"})
    if getattr(dry_args, "replace_references", False):
        writes.append({"role": "replace-references", "path": "enabled"})

    return {
        "schema_version": "1.0",
        "artifact_type": "rag-dry-run-plan",
        "status": "dry-run",
        "command": effective_command,
        "repo_root": str(repo_root),
        "would_run": False,
        "reads": [item for item in reads if item.get("path")],
        "writes": [item for item in writes if item.get("path")],
        "options": {
            "clean_output": bool(getattr(dry_args, "clean_output", False)),
            "delete_source": bool(getattr(dry_args, "delete_source", False)),
            "duckdb_migrate": bool(getattr(dry_args, "duckdb_migrate", False)),
            "reset": bool(getattr(dry_args, "reset", False)),
            "skip_optimization": bool(getattr(dry_args, "skip_optimization", False)),
            "standardize_filenames": bool(getattr(dry_args, "standardize_filenames", False)),
        },
        "next_action": "内容を確認し、問題なければ --dry-run を外して同じコマンドを実行してください。",
    }


def run_rag(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    runner = RAG_RUNNERS.get(command)
    if runner is None:
        raise KeyError(command)
    if getattr(args, "dry_run", False):
        return rag_dry_run_plan(args, repo_root, command)
    return runner(workflow_args(args, repo_root, command))
