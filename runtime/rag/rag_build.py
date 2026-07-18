from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.rag import build_index, chunk_documents, duckdb_store, embed_chunks, ingestion_optimizer, normalize_documents  # noqa: E402
from runtime.rag.paths import (  # noqa: E402
    EMBEDDINGS_INDEX,
    GENERATED_CHUNKS,
    GENERATED_INDEXES,
    GENERATED_NORMALIZED,
    GENERATED_OPTIMIZED_CHUNKS,
    RAG_BUILD_RUN_LATEST,
    SOURCE_CORRECTIVE_ACTION_REPORTS,
)
from runtime.rag import standardize_corrective_report_names  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def resolve_work_dir(repo_root: Path, work_id: str, work_dir: str) -> Path | None:
    if work_dir:
        raw = Path(work_dir)
        return raw if raw.is_absolute() else repo_root / raw
    if work_id:
        return repo_root / "work" / work_id
    return None


def stage_record(name: str, result: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": "completed",
        "result": result,
    }


def should_standardize(args: argparse.Namespace) -> bool:
    if args.skip_standardize:
        return False
    if args.standardize_filenames:
        return True
    return args.document_type == "corrective-action-report" and "corrective-action-report" in args.source_dir.replace("\\", "/")


def build_run_artifact(
    repo_root: Path,
    args: argparse.Namespace,
    stages: list[dict[str, Any]],
) -> dict[str, Any]:
    normalize_result = next((item["result"] for item in stages if item["name"] == "normalize-documents"), {})
    chunk_result = next((item["result"] for item in stages if item["name"] == "chunk-documents"), {})
    optimization_result = next((item["result"] for item in stages if item["name"] == "optimize-ingestion"), {})
    index_result = next((item["result"] for item in stages if item["name"] == "build-index"), {})
    embedding_result = next((item["result"] for item in stages if item["name"] == "embed-chunks"), {})
    duckdb_result = next((item["result"] for item in stages if item["name"] == "duckdb-migrate"), {})
    source_dir = resolve_repo_path(repo_root, args.source_dir).resolve()
    normalized_dir = resolve_repo_path(repo_root, args.normalized_dir).resolve()
    chunks_dir = resolve_repo_path(repo_root, args.chunks_dir).resolve()
    optimized_chunks_dir = resolve_repo_path(repo_root, getattr(args, "optimized_chunks_dir", str(GENERATED_OPTIMIZED_CHUNKS))).resolve()
    indexes_dir = resolve_repo_path(repo_root, args.indexes_dir).resolve()
    embeddings_output = resolve_repo_path(repo_root, args.embeddings_output).resolve()
    human_check_reasons: list[str] = []
    if args.clean_output:
        human_check_reasons.append("clean-output was used for generated RAG artifact directories.")
    if should_standardize(args):
        human_check_reasons.append("source report filenames may be standardized before normalization.")
    return {
        "schema_version": "1.0",
        "artifact_type": "rag-build-run",
        "architecture": "context-first",
        "created_at": utc_now_iso(),
        "status": "completed",
        "pipeline": "file-based-rag-build",
        "work_id": args.work_id,
        "inputs": {
            "source_dir": relative_to_repo(repo_root, source_dir),
            "document_type": args.document_type,
            "standardize_filenames": should_standardize(args),
            "clean_output": bool(args.clean_output),
        },
        "outputs": {
            "normalized_dir": relative_to_repo(repo_root, normalized_dir),
            "chunks_dir": relative_to_repo(repo_root, chunks_dir),
            "optimized_chunks_dir": relative_to_repo(repo_root, optimized_chunks_dir),
            "indexes_dir": relative_to_repo(repo_root, indexes_dir),
            "embeddings_output": relative_to_repo(repo_root, embeddings_output),
            "document_count": normalize_result.get("document_count", 0),
            "raw_chunk_count": chunk_result.get("chunk_count", 0),
            "chunk_count": index_result.get(
                "chunk_count",
                optimization_result.get("accepted_chunk_count", chunk_result.get("chunk_count", 0)),
            ),
            "candidate_chunk_count": optimization_result.get("candidate_chunk_count", 0),
            "accepted_chunk_count": optimization_result.get("accepted_chunk_count", 0),
            "rewritten_chunk_count": optimization_result.get("rewritten_chunk_count", 0),
            "human_check_required_count": optimization_result.get("human_check_required_count", 0),
            "rejected_chunk_count": optimization_result.get("rejected_chunk_count", 0),
            "average_optimization_score": optimization_result.get("average_optimization_score", 0.0),
            "ingestion_evidence_dir": optimization_result.get("evidence_dir", ""),
            "ingestion_summary": optimization_result.get("ingestion_summary", ""),
            "embedding_count": embedding_result.get("embedding_count", 0),
            "documents_index": index_result.get("documents_index", ""),
            "chunks_index": index_result.get("chunks_index", ""),
            "duckdb_enabled": bool(getattr(args, "duckdb_migrate", False)),
            "duckdb_path": duckdb_result.get("db", ""),
            "duckdb_migration_summary": duckdb_result.get("evidence_output", ""),
            "duckdb_registered_count": duckdb_result.get("registered_count", 0),
            "duckdb_updated_count": duckdb_result.get("updated_count", 0),
            "duckdb_skipped_count": duckdb_result.get("skipped_count", 0),
            "duckdb_failed_count": duckdb_result.get("failed_count", 0),
        },
        "stages": stages,
        "human_check_required": bool(human_check_reasons),
        "human_check_reasons": human_check_reasons,
    }


def register_rag_build_context(
    repo_root: Path,
    args: argparse.Namespace,
    artifact_path: Path,
) -> None:
    work_dir = resolve_work_dir(repo_root, args.work_id, args.work_dir)
    if work_dir is None:
        return
    work_id = args.work_id or work_dir.name
    register_context(
        repo_root,
        work_dir,
        work_id=work_id,
        context_type="rag-build-run",
        path=artifact_path,
        required=False,
        generated_by="runtime-rag-build",
        owner="workflow",
        schema=".github/schemas/rag-build-run.schema.json",
    )


def register_duckdb_migration_context(
    repo_root: Path,
    args: argparse.Namespace,
    evidence_path: Path,
    migration_result: dict[str, Any],
) -> None:
    work_dir = resolve_work_dir(repo_root, args.work_id, args.work_dir)
    if work_dir is None:
        return
    work_id = args.work_id or work_dir.name
    register_context(
        repo_root,
        work_dir,
        work_id=work_id,
        context_type="rag-duckdb-migration",
        path=evidence_path,
        required=False,
        generated_by="runtime-rag-build",
        owner="workflow",
        schema=".github/schemas/rag-duckdb-migration.schema.json",
        status="available" if migration_result.get("failed_count", 0) == 0 else "human-check-required",
    )


def write_duckdb_migration_evidence(
    repo_root: Path,
    evidence_path: Path,
    migration_result: dict[str, Any],
    *,
    rag_build_run_path: Path,
) -> dict[str, Any]:
    payload = {
        "schema_version": "1.0",
        "artifact_type": "rag-duckdb-migration",
        "created_at": utc_now_iso(),
        "status": migration_result.get("status", "unknown"),
        "rag_build_run": relative_to_repo(repo_root, rag_build_run_path),
        "migration": migration_result,
    }
    write_json(evidence_path, payload)
    return {**migration_result, "evidence_output": relative_to_repo(repo_root, evidence_path)}


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    stages: list[dict[str, Any]] = []

    if should_standardize(args):
        standardize_result = standardize_corrective_report_names.run(
            argparse.Namespace(
                source_dir=args.source_dir,
                repo_root=str(repo_root),
                replace_references=args.replace_references,
                random_length=args.random_length,
            )
        )
        stages.append(stage_record("standardize-corrective-report-filenames", standardize_result))

    normalize_result = normalize_documents.run(
        argparse.Namespace(
            source_dir=args.source_dir,
            output_dir=args.normalized_dir,
            document_type=args.document_type,
            repo_root=str(repo_root),
            project=args.project,
            repository=args.repository,
            branch=args.branch,
            commit=args.commit,
            status=args.status,
            clean_output=args.clean_output,
        )
    )
    stages.append(stage_record("normalize-documents", normalize_result))

    chunk_result = chunk_documents.run(
        argparse.Namespace(
            input_dir=args.normalized_dir,
            output_dir=args.chunks_dir,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            repo_root=str(repo_root),
            clean_output=args.clean_output,
        )
    )
    stages.append(stage_record("chunk-documents", chunk_result))

    index_chunks_dir = args.chunks_dir
    if not getattr(args, "skip_optimization", False):
        optimization_result = ingestion_optimizer.run(
            argparse.Namespace(
                chunks_dir=args.chunks_dir,
                output_dir=getattr(args, "optimized_chunks_dir", str(GENERATED_OPTIMIZED_CHUNKS)),
                evidence_dir=getattr(args, "ingestion_evidence_dir", "db/rag/evidence/ingestion"),
                policy=getattr(args, "ingestion_policy", "runtime/rag/policies/knowledge-ingestion-policy.json"),
                repo_root=str(repo_root),
                clean_output=args.clean_output,
            )
        )
        stages.append(stage_record("optimize-ingestion", optimization_result))
        index_chunks_dir = getattr(args, "optimized_chunks_dir", str(GENERATED_OPTIMIZED_CHUNKS))

    index_result = build_index.run(
        argparse.Namespace(
            normalized_dir=args.normalized_dir,
            chunks_dir=index_chunks_dir,
            output_dir=args.indexes_dir,
            repo_root=str(repo_root),
        )
    )
    stages.append(stage_record("build-index", index_result))

    embedding_result = embed_chunks.run(
        argparse.Namespace(
            chunks_index=str(resolve_repo_path(repo_root, args.indexes_dir) / "chunks.jsonl"),
            output=args.embeddings_output,
            dimensions=args.embedding_dimensions,
            repo_root=str(repo_root),
        )
    )
    stages.append(stage_record("embed-chunks", embedding_result))

    duckdb_migration_result: dict[str, Any] = {}
    artifact_path = resolve_repo_path(repo_root, args.output).resolve()
    if getattr(args, "duckdb_migrate", False):
        duckdb_path = resolve_repo_path(repo_root, getattr(args, "duckdb_path", str(duckdb_store.DEFAULT_DB_PATH))).resolve()
        duckdb_source_value = getattr(args, "duckdb_source_dir", "") or index_chunks_dir
        duckdb_source_dir = resolve_repo_path(
            repo_root,
            duckdb_source_value,
        ).resolve()
        duckdb_error_log = resolve_repo_path(
            repo_root,
            getattr(args, "duckdb_error_log", str(duckdb_store.DEFAULT_ERROR_LOG)),
        ).resolve()
        duckdb_policy_value = getattr(args, "duckdb_policy", "") or getattr(
            args,
            "ingestion_policy",
            "runtime/rag/policies/knowledge-ingestion-policy.json",
        )
        duckdb_policy = ingestion_optimizer.load_policy(repo_root, duckdb_policy_value)
        raw_duckdb_result = duckdb_store.migrate_directory(
            repo_root,
            duckdb_path,
            duckdb_source_dir,
            duckdb_policy,
            duckdb_error_log,
        )
        evidence_path = resolve_repo_path(
            repo_root,
            getattr(args, "duckdb_evidence_output", "db/rag/evidence/migration-summary.json"),
        ).resolve()
        duckdb_migration_result = write_duckdb_migration_evidence(
            repo_root,
            evidence_path,
            raw_duckdb_result,
            rag_build_run_path=artifact_path,
        )
        stages.append(stage_record("duckdb-migrate", duckdb_migration_result))

    artifact = build_run_artifact(repo_root, args, stages)
    write_json(artifact_path, artifact)
    register_rag_build_context(repo_root, args, artifact_path)
    if duckdb_migration_result:
        register_duckdb_migration_context(
            repo_root,
            args,
            resolve_repo_path(repo_root, duckdb_migration_result["evidence_output"]).resolve(),
            duckdb_migration_result,
        )
    return {
        "status": "completed",
        "rag_build_run": relative_to_repo(repo_root, artifact_path),
        "document_count": artifact["outputs"]["document_count"],
        "chunk_count": artifact["outputs"]["chunk_count"],
        "embedding_count": artifact["outputs"]["embedding_count"],
        "duckdb_enabled": artifact["outputs"]["duckdb_enabled"],
        "duckdb_migration_summary": artifact["outputs"]["duckdb_migration_summary"],
        "stages": [item["name"] for item in stages],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the file-based RAG build pipeline and register Context First output.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--work-id", default="")
    parser.add_argument("--work-dir", default="")
    parser.add_argument("--source-dir", default=str(SOURCE_CORRECTIVE_ACTION_REPORTS))
    parser.add_argument("--document-type", default="corrective-action-report")
    parser.add_argument("--normalized-dir", default=str(GENERATED_NORMALIZED))
    parser.add_argument("--chunks-dir", default=str(GENERATED_CHUNKS))
    parser.add_argument("--optimized-chunks-dir", default=str(GENERATED_OPTIMIZED_CHUNKS))
    parser.add_argument("--indexes-dir", default=str(GENERATED_INDEXES))
    parser.add_argument("--embeddings-output", default=str(EMBEDDINGS_INDEX))
    parser.add_argument("--output", default=str(RAG_BUILD_RUN_LATEST))
    parser.add_argument("--ingestion-evidence-dir", default="db/rag/evidence/ingestion")
    parser.add_argument("--ingestion-policy", default="runtime/rag/policies/knowledge-ingestion-policy.json")
    parser.add_argument("--skip-optimization", action="store_true")
    parser.add_argument("--duckdb-migrate", action="store_true")
    parser.add_argument("--duckdb-path", default=str(duckdb_store.DEFAULT_DB_PATH))
    parser.add_argument("--duckdb-source-dir", default="")
    parser.add_argument("--duckdb-error-log", default=str(duckdb_store.DEFAULT_ERROR_LOG))
    parser.add_argument("--duckdb-evidence-output", default="db/rag/evidence/migration-summary.json")
    parser.add_argument("--duckdb-policy", default="")
    parser.add_argument("--project", default="")
    parser.add_argument("--repository", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--commit", default="")
    parser.add_argument("--status", default="draft")
    parser.add_argument("--chunk-size", type=int, default=1800)
    parser.add_argument("--chunk-overlap", type=int, default=180)
    parser.add_argument("--embedding-dimensions", type=int, default=768)
    parser.add_argument("--clean-output", action="store_true")
    parser.add_argument("--standardize-filenames", action="store_true")
    parser.add_argument("--skip-standardize", action="store_true")
    parser.add_argument("--replace-references", action="store_true")
    parser.add_argument("--random-length", type=int, default=8, choices=range(5, 9))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
