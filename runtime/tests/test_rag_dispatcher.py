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
    work_dir = tmp_path / "work" / "issue-9001"
    context_dir = work_dir / "context"
    context_dir.mkdir(parents=True)
    execution_plan = context_dir / "execution-plan.json"
    execution_plan.write_text(
        json.dumps({"schema_version": "1.0", "artifact_type": "execution-plan"}),
        encoding="utf-8",
    )
    args = rag_dispatcher.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--work-id",
            "issue-9001",
            "--work-dir",
            str(work_dir),
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
    assert plan["execution_plan"] == str(execution_plan)
    assert plan["execution_plan_gate"]["status"] == "ready"
    assert dispatch["dispatch_plan"] == result["dispatch_plan"]
    assert dispatch["dispatch_plan_id"] == plan["plan_id"]
    assert dispatch["execution_plan"] == str(execution_plan)
    assert dispatch["human_check_required"] is False
    assert result["context_pack_count"] == 2
    manifest = json.loads((context_dir / "context-manifest.json").read_text(encoding="utf-8"))
    assert {"rag-dispatch-plan", "rag-load-dispatch"} <= {item["type"] for item in manifest["contexts"]}


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


def test_dispatcher_warns_when_work_id_has_no_execution_plan(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    chunks, embeddings = write_tiny_indexes(tmp_path)
    output_dir = tmp_path / "retrieval"
    work_dir = tmp_path / "work" / "issue-9002"
    work_dir.mkdir(parents=True)
    args = rag_dispatcher.build_parser().parse_args(
        [
            "--repo-root",
            str(repo_root),
            "--work-id",
            "issue-9002",
            "--work-dir",
            str(work_dir),
            "--task",
            "workflow doctor human gate registry",
            "--chunks-index",
            str(chunks),
            "--embeddings-index",
            str(embeddings),
            "--output-dir",
            str(output_dir),
            "--max-queries",
            "1",
            "--jobs",
            "1",
            "--top-k",
            "1",
        ]
    )

    result = rag_dispatcher.run(args)

    plan = json.loads(Path(result["dispatch_plan"]).read_text(encoding="utf-8"))
    dispatch = json.loads(Path(result["dispatch_result"]).read_text(encoding="utf-8"))
    assert plan["execution_plan_gate"]["status"] == "human-check-required"
    assert plan["human_check_required"] is True
    assert dispatch["human_check_required"] is True
    assert result["human_check_required"] is True
