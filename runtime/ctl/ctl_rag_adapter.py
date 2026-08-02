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


def run_rag(args: argparse.Namespace, repo_root: Path, command: str) -> dict[str, Any]:
    runner = RAG_RUNNERS.get(command)
    if runner is None:
        raise KeyError(command)
    return runner(workflow_args(args, repo_root, command))
