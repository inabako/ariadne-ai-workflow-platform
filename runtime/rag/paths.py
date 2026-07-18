from __future__ import annotations

from pathlib import Path


KNOWLEDGE_SOURCE_REPO = Path("work/db/ariadne-knowledge-platform")
KNOWLEDGE_SOURCE_RAG = KNOWLEDGE_SOURCE_REPO / "rag"
GENERATED_RAG = Path("db/rag")

SOURCE_CORRECTIVE_ACTION_REPORTS = KNOWLEDGE_SOURCE_RAG / "corrective-action-report"
SOURCE_GITHUB_KNOWLEDGE = KNOWLEDGE_SOURCE_RAG / "github-knowledge"
SOURCE_WORKSPACE_ENVIRONMENT = KNOWLEDGE_SOURCE_RAG / "workspace-environment"

GENERATED_NORMALIZED = GENERATED_RAG / "normalized"
GENERATED_CHUNKS = GENERATED_RAG / "chunks"
GENERATED_OPTIMIZED_CHUNKS = GENERATED_RAG / "optimized-chunks"
GENERATED_JSONIZED = GENERATED_RAG / "jsonized"
GENERATED_INDEXES = GENERATED_RAG / "indexes"
GENERATED_EMBEDDINGS = GENERATED_RAG / "embeddings"
GENERATED_RETRIEVAL = GENERATED_RAG / "retrieval"

CHUNKS_INDEX = GENERATED_INDEXES / "chunks.jsonl"
EMBEDDINGS_INDEX = GENERATED_EMBEDDINGS / "chunks-embeddings.jsonl"
RAG_BUILD_RUN_LATEST = GENERATED_RETRIEVAL / "rag-build-run-latest.json"

SOURCE_REPO_STANDARD_DIRS = [
    Path("rag/optimized-chunks"),
    Path("rag/chunks"),
    Path("rag/jsonized"),
    Path("rag/normalized"),
]

LOCAL_GENERATED_STANDARD_DIRS = [
    GENERATED_OPTIMIZED_CHUNKS,
    GENERATED_CHUNKS,
    GENERATED_JSONIZED,
    GENERATED_NORMALIZED,
]
