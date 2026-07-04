from __future__ import annotations

import json
from pathlib import Path

from runtime.rag import rag_dispatcher


def write_tiny_indexes(tmp_path: Path) -> tuple[Path, Path]:
    chunks = tmp_path / "chunks.jsonl"
    embeddings = tmp_path / "chunks-embeddings.jsonl"
    row = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "source_path": "rag/normalized/doc-1.json",
        "chunk_path": "rag/chunks/chunk-1.json",
        "chunk_index": 0,
        "title": "Workflow doctor and human gate registry",
        "repository": "test-repo",
        "branch": "main",
        "project": "",
        "tags": ["workflow"],
        "heading_path": ["Workflow"],
        "metadata": {},
        "content": "workflow doctor human gate registry close archive pytest regression safety STOP communication loss",
    }
    chunks.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    embeddings.write_text("", encoding="utf-8")
    return chunks, embeddings


def test_dispatcher_writes_query_plan_before_dispatch(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    chunks, embeddings = write_tiny_indexes(tmp_path)
    output_dir = tmp_path / "retrieval"
    args = rag_dispatcher.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--task",
            "workflow doctor human gate registry",
            "--repository",
            "test-repo",
            "--branch",
            "main",
            "--chunks-index",
            str(chunks),
            "--embeddings-index",
            str(embeddings),
            "--output-dir",
            str(output_dir),
            "--max-queries",
            "2",
            "--jobs",
            "1",
            "--top-k",
            "1",
        ]
    )

    result = rag_dispatcher.run(args)

    plan = json.loads(Path(result["dispatch_plan"]).read_text(encoding="utf-8"))
    dispatch = json.loads(Path(result["dispatch_result"]).read_text(encoding="utf-8"))
    assert plan["artifact_type"] == "rag-dispatch-plan"
    assert plan["queries"]
    assert plan["queries"][0]["purpose"]
    assert plan["metadata"]["repository"] == "test-repo"
    assert dispatch["dispatch_plan"] == result["dispatch_plan"]
    assert dispatch["dispatch_plan_id"] == plan["plan_id"]
    assert result["context_pack_count"] == 2


def test_dispatcher_can_reuse_existing_query_plan(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    chunks, embeddings = write_tiny_indexes(tmp_path)
    output_dir = tmp_path / "retrieval"
    plan = {
        "schema_version": "1.0",
        "artifact_type": "rag-dispatch-plan",
        "plan_id": "plan-test",
        "created_at": "2026-07-04T00:00:00+00:00",
        "intent": "reuse plan",
        "metadata": {
            "repository": "test-repo",
            "branch": "main",
            "tags": [],
        },
        "semantic_hints": ["workflow doctor"],
        "queries": [
            {
                "query": "workflow doctor human gate registry",
                "purpose": "reuse shared query plan",
                "search_mode": "hybrid",
                "filters": {
                    "repository": "test-repo",
                    "branch": "main",
                },
            }
        ],
        "stop_conditions": ["RAG indexes are missing"],
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    args = rag_dispatcher.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--dispatch-plan",
            str(plan_path),
            "--chunks-index",
            str(chunks),
            "--embeddings-index",
            str(embeddings),
            "--output-dir",
            str(output_dir),
            "--jobs",
            "1",
            "--top-k",
            "1",
        ]
    )

    result = rag_dispatcher.run(args)
    dispatch = json.loads(Path(result["dispatch_result"]).read_text(encoding="utf-8"))

    assert result["dispatch_plan"] == str(plan_path)
    assert dispatch["dispatch_plan_id"] == "plan-test"
    assert dispatch["context_packs"][0]["purpose"] == "reuse shared query plan"
