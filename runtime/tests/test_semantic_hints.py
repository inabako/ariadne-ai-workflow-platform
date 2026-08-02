from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime.rag import normalize_documents, semantic_hints


def write_backup(repo: Path) -> Path:
    backup_dir = repo / "work" / "db" / "ariadne-knowledge-platform" / "semantic-hints"
    backup_dir.mkdir(parents=True)
    backup = backup_dir / "project-specific-semantic-hints.json"
    backup.write_text(
        json.dumps(
            {
                "artifact_type": "semantic-hint-backup",
                "created_at": "2026-08-02T00:00:00Z",
                "entries": [
                    {
                        "id": "gui-simulator-check",
                        "category": "test-guidance",
                        "project_scope": "GUI simulator integration",
                        "source_path": ".ariadne/agents/tester.md",
                        "source_marker": "semantic_hint",
                        "content": "GUI simulator needs connection and telemetry confirmation.",
                        "replacement_summary": "Generic GUI simulator guidance remains in prompt text.",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return backup


def test_semantic_hints_generate_writes_rag_source_markdown(tmp_path: Path) -> None:
    backup = write_backup(tmp_path)

    result = semantic_hints.generate(
        argparse.Namespace(
            repo_root=str(tmp_path),
            source_file=[str(backup)],
            source_dir="unused",
            output_dir="work/db/ariadne-knowledge-platform/rag/semantic-hints",
            project="ariadne",
            repository="ariadne-ai-workflow-platform",
            status="approved",
            clean_output=False,
        )
    )

    assert result["generated_count"] == 1
    markdown = tmp_path / result["generated"][0]["markdown"]
    text = markdown.read_text(encoding="utf-8")
    assert "type: semantic-hint" in text
    assert "semantic_hint: gui-simulator-check" in text
    assert "GUI simulator needs connection" in text


def test_semantic_hints_read_filters_backup_entries(tmp_path: Path) -> None:
    write_backup(tmp_path)

    result = semantic_hints.read(
        argparse.Namespace(
            repo_root=str(tmp_path),
            source_dir="work/db/ariadne-knowledge-platform/rag/semantic-hints",
            backup_dir="work/db/ariadne-knowledge-platform/semantic-hints",
            query="telemetry",
            semantic_hint="",
            backend="source",
            top_k=5,
        )
    )

    assert result["hint_count"] == 1
    assert result["hints"][0]["id"] == "gui-simulator-check"

    calls: list[argparse.Namespace] = []
    original_retrieve = semantic_hints.retrieve_context.run

    def fake_retrieve(args: argparse.Namespace) -> dict[str, object]:
        calls.append(args)
        return {"retrieval_result": "rag/retrieval/result.json", "context_pack": "rag/retrieval/context.json"}

    semantic_hints.retrieve_context.run = fake_retrieve
    try:
        retrieval_result = semantic_hints.read(
            argparse.Namespace(
                repo_root=str(tmp_path),
                source_dir="work/db/ariadne-knowledge-platform/rag/semantic-hints",
                backup_dir="work/db/ariadne-knowledge-platform/semantic-hints",
                query="telemetry",
                semantic_hint="gui simulator",
                backend="file",
                top_k=3,
                chunks_index="rag/indexes/chunks.jsonl",
                embeddings_index="rag/embeddings/chunks-embeddings.jsonl",
                duckdb_path="db/rag/ariadne-knowledge.duckdb",
                output_dir="rag/retrieval",
                project="ariadne",
            )
        )
    finally:
        semantic_hints.retrieve_context.run = original_retrieve

    assert retrieval_result["backend"] == "file"
    assert calls[0].source_type == ""
    assert calls[0].write_markdown is False
    assert calls[0].project == "ariadne"


def test_semantic_hints_build_generates_then_runs_rag_build(monkeypatch, tmp_path: Path) -> None:
    backup = write_backup(tmp_path)
    calls: list[argparse.Namespace] = []

    def fake_rag_build(args: argparse.Namespace) -> dict[str, object]:
        calls.append(args)
        return {
            "status": "completed",
            "rag_build_run": "work/db/ariadne-knowledge-platform/rag/retrieval/semantic-hints-build-latest.json",
            "document_count": 1,
            "chunk_count": 1,
        }

    monkeypatch.setattr(semantic_hints.rag_build, "run", fake_rag_build)

    result = semantic_hints.build(
        argparse.Namespace(
            repo_root=str(tmp_path),
            source_file=[str(backup)],
            source_dir="unused",
            rag_source_dir="work/db/ariadne-knowledge-platform/rag/semantic-hints",
            document_type="semantic-hint",
            normalized_dir="rag/normalized",
            chunks_dir="rag/chunks",
            optimized_chunks_dir="rag/optimized-chunks",
            indexes_dir="rag/indexes",
            embeddings_output="rag/embeddings/chunks-embeddings.jsonl",
            output="rag/retrieval/semantic-hints-build-latest.json",
            project="ariadne",
            repository="ariadne-ai-workflow-platform",
            branch="main",
            commit="abc123",
            status="approved",
            chunk_size=500,
            chunk_overlap=50,
            embedding_dimensions=64,
            skip_optimization=True,
            duckdb_migrate=False,
            duckdb_path="db/rag/ariadne-knowledge.duckdb",
            clean_output=False,
        )
    )

    assert result["artifact_type"] == "semantic-hints-build"
    assert result["document_count"] == 1
    assert calls[0].source_dir == "work/db/ariadne-knowledge-platform/rag/semantic-hints"
    assert calls[0].document_type == "semantic-hint"
    assert calls[0].skip_standardize is True


def test_normalize_documents_preserves_semantic_hint(tmp_path: Path) -> None:
    source = tmp_path / "rag" / "semantic-hints"
    source.mkdir(parents=True)
    (source / "hint.md").write_text(
        "---\n"
        "title: Hint\n"
        "type: semantic-hint\n"
        "semantic_hint: gui simulator telemetry\n"
        "---\n\n"
        "# Hint\n\n"
        "Use this hint when GUI simulator telemetry evidence is needed.\n",
        encoding="utf-8",
    )

    result = normalize_documents.run(
        argparse.Namespace(
            repo_root=str(tmp_path),
            source_dir="rag/semantic-hints",
            output_dir="rag/normalized",
            document_type="semantic-hint",
            project="",
            repository="",
            branch="",
            commit="",
            status="approved",
            clean_output=False,
        )
    )

    normalized = json.loads((tmp_path / result["documents"][0]).read_text(encoding="utf-8"))
    assert normalized["semantic_hint"] == "gui simulator telemetry"
    assert normalized["metadata"]["semantic_hint"] == "gui simulator telemetry"
