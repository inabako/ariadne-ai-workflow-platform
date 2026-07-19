from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso  # noqa: E402
from runtime.constants.paths import (  # noqa: E402
    CHUNKS_DIR_NAME,
    DUCKDB_DEFAULT_PATH,
    DUCKDB_ERROR_LOG,
    DUCKDB_REFERENCE_CHECK_OUTPUT,
    DUCKDB_REFERENCE_CHECK_WORK_DIR,
    JSONIZED_DIR_NAME,
    KNOWLEDGE_SOURCE_REPO,
    KNOWLEDGE_SOURCE_REPO_URL,
    LOCAL_GENERATED_STANDARD_DIRS,
    NORMALIZED_DIR_NAME,
    OPTIMIZED_CHUNKS_DIR_NAME,
    SOURCE_REPO_STANDARD_DIRS,
)
from runtime.constants.schemas import RAG_DUCKDB_REFERENCE_CHECK_SCHEMA  # noqa: E402
from runtime.constants.workspace import (  # noqa: E402
    context_path_pattern,
    manifest_path_for_work_dir,
    work_dir_for_id,
)
from runtime.rag import ingestion_optimizer  # noqa: E402
from runtime.workflow.context_first import register_context  # noqa: E402


DEFAULT_DB_PATH = DUCKDB_DEFAULT_PATH
DEFAULT_ERROR_LOG = DUCKDB_ERROR_LOG
DEFAULT_REFERENCE_CHECK_OUTPUT = DUCKDB_REFERENCE_CHECK_OUTPUT
DEFAULT_REFERENCE_CHECK_WORK_DIR = DUCKDB_REFERENCE_CHECK_WORK_DIR
DEFAULT_REFERENCE_CHECK_WORK_ID = "duckdb-reference-check"
DEFAULT_SOURCE_REPO_URL = KNOWLEDGE_SOURCE_REPO_URL
DEFAULT_SOURCE_REPO_PATH = KNOWLEDGE_SOURCE_REPO
SCHEMA_VERSION = "1.1"
STANDARD_SOURCE_DIRS = SOURCE_REPO_STANDARD_DIRS
LOCAL_STANDARD_SOURCE_DIRS = LOCAL_GENERATED_STANDARD_DIRS
DEFAULT_REFERENCE_QUERIES = ["workflow", "runtime", "RAG"]


@dataclass(frozen=True)
class KnowledgeRecord:
    knowledge_id: str
    title: str
    content: str
    summary: str
    semantic_hint: str
    category: str
    document_type: str
    source: str
    source_path: str
    environment: str
    workflow: str
    content_hash: str
    status: str
    metadata: dict[str, Any]
    source_file: str
    source_kind: str
    created_at: str
    updated_at: str
    tags: list[str]


@dataclass(frozen=True)
class SearchFilters:
    query: str
    semantic_hint: str
    category: str
    tags: list[str]
    source: str
    document_type: str
    environment: str
    workflow: str
    min_reliability: float | None
    min_freshness: float | None
    limit: int


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Maintain a generated DuckDB read model for file-based Ariadne RAG artifacts."
    )
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Generated DuckDB file path.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create the generated DuckDB schema.")

    ingest = subparsers.add_parser("ingest", help="Register one JSON RAG record into DuckDB.")
    ingest.add_argument("--file", required=True, help="JSON RAG record to register.")
    ingest.add_argument("--policy", default=str(ingestion_optimizer.DEFAULT_POLICY_PATH))

    migrate = subparsers.add_parser("migrate", help="Register JSON RAG records from a directory.")
    migrate.add_argument("--source", required=True, help="Directory containing JSON RAG records.")
    migrate.add_argument("--policy", default=str(ingestion_optimizer.DEFAULT_POLICY_PATH))
    migrate.add_argument("--error-log", default=str(DEFAULT_ERROR_LOG))

    source = subparsers.add_parser("source", help="Manage the external RAG source repository clone.")
    source.add_argument("--path", default=str(DEFAULT_SOURCE_REPO_PATH), help="Local source repository path.")
    source.add_argument("--url", default=DEFAULT_SOURCE_REPO_URL, help="Remote source repository URL.")
    source_sub = source.add_subparsers(dest="source_command", required=True)
    source_sub.add_parser("status", help="Inspect local source repository clone.")
    source_clone = source_sub.add_parser("clone", help="Clone the source repository when missing.")
    source_clone.add_argument("--pull-if-exists", action="store_true", help="Run pull when the clone already exists.")
    source_sub.add_parser("pull", help="Pull the existing source repository clone.")
    source_import = source_sub.add_parser("import-local", help="Copy local RAG JSON sources into the source repository clone.")
    source_import.add_argument("--clean", action="store_true", help="Clean copied standard source directories first.")

    rebuild = subparsers.add_parser("rebuild", help="Rebuild DuckDB read model from standard RAG JSON sources.")
    rebuild.add_argument("--source", action="append", default=[], help="Source directory. Can be repeated.")
    rebuild.add_argument("--source-repo", default="", help="Local knowledge source repository clone.")
    rebuild.add_argument("--source-repo-url", default=DEFAULT_SOURCE_REPO_URL)
    rebuild.add_argument("--policy", default=str(ingestion_optimizer.DEFAULT_POLICY_PATH))
    rebuild.add_argument("--error-log", default=str(DEFAULT_ERROR_LOG))
    rebuild.add_argument("--reset", action="store_true", help="Delete the generated DuckDB file before migration.")

    search = subparsers.add_parser("search", help="Search generated DuckDB RAG read model.")
    add_search_arguments(search)

    export = subparsers.add_parser("export-context", help="Export search results as Agent context JSON.")
    add_search_arguments(export)
    export.add_argument("--output", required=True, help="Context JSON output path.")
    export.add_argument("--max-chars", type=int, default=4000, help="Maximum content characters per exported result.")

    verify = subparsers.add_parser("verify", help="Verify DuckDB references by running representative searches.")
    verify.add_argument("--query", action="append", default=[], help="Reference query. Can be repeated.")
    verify.add_argument("--min-results", type=int, default=1)
    verify.add_argument("--limit", type=int, default=5)
    verify.add_argument("--output", default=str(DEFAULT_REFERENCE_CHECK_OUTPUT))
    verify.add_argument("--work-id", default="", help=f"Register reference check evidence under {context_path_pattern()}.")
    verify.add_argument("--work-dir", default="", help="Explicit work directory for Context First registration.")
    verify.add_argument("--source-repo", default="", help="Local knowledge source repository clone used for the DB.")
    return parser


def add_search_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--query", default="", help="Keyword query.")
    parser.add_argument("--semantic-hint", default="", help="Semantic hint filter / ranking hint.")
    parser.add_argument("--category", default="")
    parser.add_argument("--tag", dest="tags", action="append", default=[])
    parser.add_argument("--source", default="")
    parser.add_argument("--document-type", default="")
    parser.add_argument("--environment", default="")
    parser.add_argument("--workflow", default="")
    parser.add_argument("--min-reliability", type=float, default=None)
    parser.add_argument("--min-freshness", type=float, default=None)
    parser.add_argument("--limit", type=int, default=10)


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def resolve_work_dir(repo_root: Path, work_id: str = "", work_dir: str = "") -> Path | None:
    if work_dir:
        path = Path(work_dir)
        return path if path.is_absolute() else repo_root / path
    if work_id:
        return work_dir_for_id(repo_root, work_id)
    return None


def run_git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)


def git_output(cwd: Path, args: list[str]) -> str:
    result = run_git(cwd, args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def source_repo_metadata(repo_root: Path, source_repo: Path, url: str = DEFAULT_SOURCE_REPO_URL) -> dict[str, Any]:
    path = source_repo.resolve()
    exists = path.exists()
    is_git_repo = (path / ".git").exists()
    metadata: dict[str, Any] = {
        "url": url,
        "path": relative_to_repo(repo_root, path),
        "exists": exists,
        "is_git_repo": is_git_repo,
        "branch": "",
        "commit": "",
        "dirty": False,
        "status": "missing",
    }
    if not exists:
        return metadata
    if not is_git_repo:
        metadata["status"] = "not-a-git-repository"
        return metadata
    try:
        metadata["branch"] = git_output(path, ["rev-parse", "--abbrev-ref", "HEAD"])
        metadata["commit"] = git_output(path, ["rev-parse", "HEAD"])
        dirty_output = git_output(path, ["status", "--short"])
        metadata["dirty"] = bool(dirty_output)
        metadata["status"] = "dirty" if metadata["dirty"] else "clean"
    except RuntimeError as exc:
        metadata["status"] = "error"
        metadata["error"] = str(exc)
    return metadata


def clone_source_repo(repo_root: Path, source_repo: Path, url: str, *, pull_if_exists: bool = False) -> dict[str, Any]:
    target = source_repo.resolve()
    if target.exists():
        if not (target / ".git").exists():
            raise RuntimeError(f"Knowledge source path exists but is not a Git repository: {target}")
        action = "pulled" if pull_if_exists else "skipped"
        if pull_if_exists:
            result = run_git(target, ["pull", "--ff-only"])
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git pull failed")
        return {
            "status": "completed",
            "artifact_type": "rag-knowledge-source",
            "action": action,
            "source_repository": source_repo_metadata(repo_root, target, url),
        }
    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["git", "clone", url, str(target)], cwd=repo_root, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git clone failed")
    return {
        "status": "completed",
        "artifact_type": "rag-knowledge-source",
        "action": "cloned",
        "source_repository": source_repo_metadata(repo_root, target, url),
    }


def pull_source_repo(repo_root: Path, source_repo: Path, url: str) -> dict[str, Any]:
    target = source_repo.resolve()
    if not (target / ".git").exists():
        raise RuntimeError(f"Knowledge source repository is not cloned: {target}")
    before = source_repo_metadata(repo_root, target, url)
    result = run_git(target, ["pull", "--ff-only"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git pull failed")
    after = source_repo_metadata(repo_root, target, url)
    return {
        "status": "completed",
        "artifact_type": "rag-knowledge-source",
        "action": "pulled",
        "before": before,
        "source_repository": after,
    }


def source_repo_standard_sources(repo_root: Path, source_repo: Path) -> list[Path]:
    base = source_repo.resolve()
    candidates = [base / source for source in STANDARD_SOURCE_DIRS]
    existing = [path for path in candidates if path.exists()]
    if existing:
        return existing
    return [base] if base.exists() else []


def copy_tree_contents(source: Path, target: Path, *, clean: bool = False) -> dict[str, int]:
    if clean and target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    copied_files = 0
    copied_dirs = 0
    for item in source.iterdir():
        destination = target / item.name
        if item.is_dir():
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(item, destination)
            copied_dirs += 1
            copied_files += sum(1 for path in destination.rglob("*") if path.is_file())
        elif item.is_file():
            shutil.copy2(item, destination)
            copied_files += 1
    return {"copied_files": copied_files, "copied_dirs": copied_dirs}


def import_local_rag_sources(
    repo_root: Path,
    source_repo: Path,
    url: str = DEFAULT_SOURCE_REPO_URL,
    *,
    clean: bool = False,
) -> dict[str, Any]:
    target_root = source_repo.resolve()
    if not (target_root / ".git").exists():
        raise RuntimeError(f"Knowledge source repository is not cloned: {target_root}")
    imports: list[dict[str, Any]] = []
    total_files = 0
    for relative_source, target_relative in zip(LOCAL_STANDARD_SOURCE_DIRS, STANDARD_SOURCE_DIRS, strict=True):
        source = repo_root / relative_source
        if not source.exists():
            continue
        target = target_root / target_relative
        if source.resolve() == target.resolve():
            imports.append(
                {
                    "source": relative_to_repo(repo_root, source),
                    "target": relative_to_repo(repo_root, target),
                    "copied_files": 0,
                    "skipped": "source and target are identical",
                }
            )
            continue
        result = copy_tree_contents(source, target, clean=clean)
        total_files += result["copied_files"]
        imports.append(
            {
                "source": relative_to_repo(repo_root, source),
                "target": relative_to_repo(repo_root, target),
                **result,
            }
        )
    return {
        "status": "completed",
        "artifact_type": "rag-knowledge-source",
        "action": "import-local",
        "imported_file_count": total_files,
        "imports": imports,
        "source_repository": source_repo_metadata(repo_root, target_root, url),
    }


def connect(db_path: Path, read_only: bool = False):
    try:
        import duckdb
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency boundary
        raise RuntimeError("DuckDB is not installed. Run runtime via uv so pyproject dependencies are available.") from exc
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path), read_only=read_only)


def init_schema(db_path: Path) -> dict[str, Any]:
    with connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                knowledge_id VARCHAR PRIMARY KEY,
                title VARCHAR,
                content TEXT NOT NULL,
                summary TEXT,
                semantic_hint VARCHAR,
                category VARCHAR,
                document_type VARCHAR,
                source VARCHAR,
                source_path VARCHAR,
                environment VARCHAR,
                workflow VARCHAR,
                content_hash VARCHAR,
                status VARCHAR DEFAULT 'active',
                metadata_json TEXT,
                source_file VARCHAR,
                source_kind VARCHAR,
                created_at VARCHAR,
                updated_at VARCHAR,
                registered_at VARCHAR
            )
            """
        )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_documents_content_hash "
            "ON knowledge_documents(content_hash)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_tags (
                knowledge_id VARCHAR NOT NULL,
                tag VARCHAR NOT NULL,
                PRIMARY KEY (knowledge_id, tag)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_scores (
                knowledge_id VARCHAR PRIMARY KEY,
                reliability_score DOUBLE,
                relevance_score DOUBLE,
                freshness_score DOUBLE,
                duplication_score DOUBLE,
                total_score DOUBLE,
                optimization_score DOUBLE,
                optimization_decision VARCHAR,
                scored_at VARCHAR
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_store_metadata (
                key VARCHAR PRIMARY KEY,
                value VARCHAR,
                updated_at VARCHAR
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_migration_runs (
                run_id VARCHAR PRIMARY KEY,
                source VARCHAR,
                status VARCHAR,
                target_file_count INTEGER,
                registered_count INTEGER,
                updated_count INTEGER,
                skipped_count INTEGER,
                failed_count INTEGER,
                error_log VARCHAR,
                started_at VARCHAR,
                completed_at VARCHAR,
                summary_json TEXT
            )
            """
        )
        now = utc_now_iso()
        conn.execute(
            "INSERT OR REPLACE INTO rag_store_metadata VALUES (?, ?, ?)",
            ["schema_version", SCHEMA_VERSION, now],
        )
    return {
        "status": "completed",
        "artifact_type": "rag-duckdb-schema",
        "db": str(db_path),
        "schema_version": SCHEMA_VERSION,
        "tables": [
            "knowledge_documents",
            "knowledge_tags",
            "knowledge_scores",
            "rag_store_metadata",
            "rag_migration_runs",
        ],
    }


def metadata_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    metadata = payload.get("metadata")
    return dict(metadata) if isinstance(metadata, dict) else {}


def first_text(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if value is not None and not isinstance(value, (dict, list, tuple, set)):
            text = str(value).strip()
            if text:
                return text
    return ""


def list_text(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Iterable) and not isinstance(value, (dict, bytes)):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def source_kind_from_path(path: Path) -> str:
    parent_names = {part.lower() for part in path.parts}
    if OPTIMIZED_CHUNKS_DIR_NAME in parent_names:
        return "optimized-chunk"
    if CHUNKS_DIR_NAME in parent_names:
        return "chunk"
    if NORMALIZED_DIR_NAME in parent_names:
        return "normalized-document"
    if JSONIZED_DIR_NAME in parent_names:
        return "jsonized-artifact"
    return "knowledge-json"


def deterministic_id(source_file: str, content: str) -> str:
    seed = f"{source_file}\n{ingestion_optimizer.content_hash(content)}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def normalize_record(repo_root: Path, path: Path, payload: dict[str, Any]) -> KnowledgeRecord:
    metadata = metadata_from_payload(payload)
    content = first_text(payload.get("content"), metadata.get("content"), payload.get("body"), payload.get("text"))
    if not content:
        raise ValueError("RAG record requires non-empty content.")

    source_file = relative_to_repo(repo_root, path)
    hash_value = first_text(payload.get("content_hash"), metadata.get("content_hash"))
    if not hash_value:
        hash_value = ingestion_optimizer.content_hash(content)

    knowledge_id = first_text(
        payload.get("knowledge_id"),
        payload.get("chunk_id"),
        payload.get("document_id"),
        metadata.get("knowledge_id"),
        metadata.get("chunk_id"),
        metadata.get("document_id"),
    )
    if not knowledge_id:
        knowledge_id = deterministic_id(source_file, content)

    tags = sorted(
        set(
            list_text(payload.get("tags"))
            + list_text(metadata.get("tags"))
            + list_text(metadata.get("keywords"))
            + list_text(payload.get("heading_path"))
        )
    )
    now = utc_now_iso()
    return KnowledgeRecord(
        knowledge_id=knowledge_id,
        title=first_text(payload.get("title"), metadata.get("title"), payload.get("document_title")),
        content=content,
        summary=first_text(payload.get("summary"), metadata.get("summary")),
        semantic_hint=first_text(payload.get("semantic_hint"), metadata.get("semantic_hint")),
        category=first_text(payload.get("category"), metadata.get("category"), metadata.get("source_type")),
        document_type=first_text(payload.get("document_type"), metadata.get("document_type"), payload.get("type")),
        source=first_text(payload.get("source"), metadata.get("source"), metadata.get("repository")),
        source_path=first_text(payload.get("source_path"), metadata.get("source_path"), source_file),
        environment=first_text(payload.get("environment"), metadata.get("environment")),
        workflow=first_text(payload.get("workflow"), metadata.get("workflow")),
        content_hash=hash_value,
        status=first_text(payload.get("status"), metadata.get("status"), "active"),
        metadata=metadata,
        source_file=source_file,
        source_kind=source_kind_from_path(path),
        created_at=first_text(payload.get("created_at"), metadata.get("created_at"), now),
        updated_at=first_text(payload.get("updated_at"), metadata.get("updated_at"), now),
        tags=tags,
    )


def record_as_optimizer_chunk(record: KnowledgeRecord) -> dict[str, Any]:
    metadata = dict(record.metadata)
    metadata.update(
        {
            "title": record.title,
            "document_type": record.document_type,
            "status": record.status,
            "source": record.source,
            "source_path": record.source_path,
            "tags": record.tags,
        }
    )
    return {
        "chunk_id": record.knowledge_id,
        "document_id": record.knowledge_id,
        "source_path": record.source_path,
        "heading_path": record.tags,
        "content": record.content,
        "content_hash": record.content_hash,
        "metadata": metadata,
    }


def score_record(record: KnowledgeRecord, policy: dict[str, Any], seen_hashes: set[str]) -> dict[str, Any]:
    existing_score = record.metadata.get("optimization_score")
    existing_decision = record.metadata.get("optimization_decision")
    evaluation = ingestion_optimizer.evaluate_chunk(record_as_optimizer_chunk(record), policy, seen_hashes)
    scores = evaluation["scores"]
    freshness = 1.0 if record.updated_at or record.created_at else 0.5
    duplication = 1.0 - float(scores.get("duplication_penalty", 0.0))
    optimization_score = float(existing_score) if isinstance(existing_score, (int, float)) else float(evaluation["score"])
    optimization_decision = first_text(existing_decision, evaluation["decision"])
    return {
        "reliability_score": float(scores.get("source_reliability", 0.0)),
        "relevance_score": float(scores.get("retrieval_usefulness", 0.0)),
        "freshness_score": freshness,
        "duplication_score": duplication,
        "total_score": float(evaluation["score"]),
        "optimization_score": optimization_score,
        "optimization_decision": optimization_decision,
    }


def fetch_one_value(conn: Any, sql: str, params: list[Any]) -> Any:
    row = conn.execute(sql, params).fetchone()
    return row[0] if row else None


def existing_content_hashes(conn: Any) -> set[str]:
    return {str(row[0]) for row in conn.execute("SELECT content_hash FROM knowledge_documents").fetchall() if row[0]}


def register_record(db_path: Path, record: KnowledgeRecord, policy: dict[str, Any]) -> dict[str, Any]:
    init_schema(db_path)
    now = utc_now_iso()
    with connect(db_path) as conn:
        same_id_hash = fetch_one_value(
            conn,
            "SELECT content_hash FROM knowledge_documents WHERE knowledge_id = ?",
            [record.knowledge_id],
        )
        same_hash_id = fetch_one_value(
            conn,
            "SELECT knowledge_id FROM knowledge_documents WHERE content_hash = ?",
            [record.content_hash],
        )
        if same_id_hash == record.content_hash:
            action = "skipped"
        elif same_hash_id and same_hash_id != record.knowledge_id:
            action = "skipped"
        else:
            action = "updated" if same_id_hash else "registered"
            metadata_json = json.dumps(record.metadata, ensure_ascii=False, sort_keys=True)
            values = [
                record.knowledge_id,
                record.title,
                record.content,
                record.summary,
                record.semantic_hint,
                record.category,
                record.document_type,
                record.source,
                record.source_path,
                record.environment,
                record.workflow,
                record.content_hash,
                record.status,
                metadata_json,
                record.source_file,
                record.source_kind,
                record.created_at,
                record.updated_at,
                now,
            ]
            if same_id_hash:
                conn.execute(
                    """
                    UPDATE knowledge_documents
                    SET title = ?, content = ?, summary = ?, semantic_hint = ?, category = ?,
                        document_type = ?, source = ?, source_path = ?, environment = ?, workflow = ?,
                        content_hash = ?, status = ?, metadata_json = ?, source_file = ?,
                        source_kind = ?, created_at = ?, updated_at = ?, registered_at = ?
                    WHERE knowledge_id = ?
                    """,
                    values[1:] + [record.knowledge_id],
                )
            else:
                conn.execute(
                    """
                    INSERT INTO knowledge_documents
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    values,
                )
            conn.execute("DELETE FROM knowledge_tags WHERE knowledge_id = ?", [record.knowledge_id])
            for tag in record.tags:
                conn.execute("INSERT INTO knowledge_tags VALUES (?, ?)", [record.knowledge_id, tag])

            seen_hashes = existing_content_hashes(conn)
            seen_hashes.discard(record.content_hash)
            score = score_record(record, policy, seen_hashes)
            conn.execute("DELETE FROM knowledge_scores WHERE knowledge_id = ?", [record.knowledge_id])
            conn.execute(
                """
                INSERT INTO knowledge_scores
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    record.knowledge_id,
                    score["reliability_score"],
                    score["relevance_score"],
                    score["freshness_score"],
                    score["duplication_score"],
                    score["total_score"],
                    score["optimization_score"],
                    score["optimization_decision"],
                    now,
                ],
            )
    return {
        "status": "completed",
        "action": action,
        "knowledge_id": record.knowledge_id,
        "content_hash": record.content_hash,
        "db": str(db_path),
    }


def write_error_log(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def ingest_file(repo_root: Path, db_path: Path, file_path: Path, policy: dict[str, Any]) -> dict[str, Any]:
    payload = read_json(file_path)
    if not isinstance(payload, dict):
        raise ValueError(f"RAG record must be a JSON object: {file_path}")
    record = normalize_record(repo_root, file_path, payload)
    return register_record(db_path, record, policy)


def discover_json_files(source: Path) -> list[Path]:
    if not source.exists():
        raise FileNotFoundError(f"RAG source directory not found: {source}")
    return sorted(path for path in source.rglob("*.json") if path.is_file())


def existing_standard_sources(repo_root: Path) -> list[Path]:
    return [repo_root / source for source in LOCAL_STANDARD_SOURCE_DIRS if (repo_root / source).exists()]


def remove_generated_db(db_path: Path) -> bool:
    if db_path.exists():
        db_path.unlink()
        return True
    return False


def write_migration_history(db_path: Path, summary: dict[str, Any]) -> None:
    init_schema(db_path)
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO rag_migration_runs
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                summary["migration_run_id"],
                summary["source"],
                summary["status"],
                int(summary["target_file_count"]),
                int(summary["registered_count"]),
                int(summary["updated_count"]),
                int(summary["skipped_count"]),
                int(summary["failed_count"]),
                summary.get("error_log", ""),
                summary["started_at"],
                summary["completed_at"],
                json.dumps(summary, ensure_ascii=False, sort_keys=True),
            ],
        )


def migrate_directory(
    repo_root: Path,
    db_path: Path,
    source: Path,
    policy: dict[str, Any],
    error_log: Path,
) -> dict[str, Any]:
    return migrate_sources(repo_root, db_path, [source], policy, error_log)


def migrate_sources(
    repo_root: Path,
    db_path: Path,
    sources: list[Path],
    policy: dict[str, Any],
    error_log: Path,
) -> dict[str, Any]:
    started_at = utc_now_iso()
    migration_run_id = str(uuid.uuid4())
    files: list[Path] = []
    source_labels: list[str] = []
    missing_sources: list[str] = []
    for source in sources:
        if source.exists():
            source_labels.append(relative_to_repo(repo_root, source))
            files.extend(discover_json_files(source))
        else:
            missing_sources.append(relative_to_repo(repo_root, source))
    errors: list[dict[str, Any]] = []
    counts = {"registered": 0, "updated": 0, "skipped": 0, "failed": 0}
    for missing in missing_sources:
        errors.append(
            {
                "source_file": missing,
                "error": "RAG source directory not found",
                "error_type": "FileNotFoundError",
            }
        )
        counts["failed"] += 1
    for file_path in files:
        try:
            result = ingest_file(repo_root, db_path, file_path, policy)
            action = str(result.get("action", "failed"))
            if action in counts:
                counts[action] += 1
            else:
                counts["failed"] += 1
        except Exception as exc:
            counts["failed"] += 1
            errors.append(
                {
                    "source_file": relative_to_repo(repo_root, file_path),
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                }
            )
    write_error_log(error_log, errors)
    summary = {
        "status": "completed" if not errors else "completed_with_errors",
        "artifact_type": "rag-duckdb-migration-summary",
        "schema_version": SCHEMA_VERSION,
        "migration_run_id": migration_run_id,
        "db": str(db_path),
        "source": ", ".join(source_labels),
        "sources": source_labels,
        "missing_sources": missing_sources,
        "target_file_count": len(files),
        "registered_count": counts["registered"],
        "updated_count": counts["updated"],
        "skipped_count": counts["skipped"],
        "failed_count": counts["failed"],
        "error_log": relative_to_repo(repo_root, error_log) if errors else "",
        "started_at": started_at,
        "completed_at": utc_now_iso(),
        "errors": errors,
    }
    write_migration_history(db_path, summary)
    return summary


def rebuild_standard_sources(
    repo_root: Path,
    db_path: Path,
    sources: list[Path],
    policy: dict[str, Any],
    error_log: Path,
    reset: bool = False,
    source_repository: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reset_performed = remove_generated_db(db_path) if reset else False
    resolved_sources = sources or existing_standard_sources(repo_root)
    summary = migrate_sources(repo_root, db_path, resolved_sources, policy, error_log)
    summary["artifact_type"] = "rag-duckdb-rebuild-summary"
    summary["reset_performed"] = reset_performed
    summary["standard_sources"] = [str(path) for path in STANDARD_SOURCE_DIRS]
    if source_repository:
        summary["source_repository"] = source_repository
    return summary


def normalize_terms(value: str) -> list[str]:
    return [term.lower() for term in value.replace("　", " ").split() if term.strip()]


def text_match_score(query: str, *values: str) -> float:
    terms = normalize_terms(query)
    if not terms:
        return 0.0
    haystack = "\n".join(value or "" for value in values).lower()
    hits = sum(1 for term in terms if term in haystack)
    return round(hits / len(terms), 4)


def semantic_hint_score(query: str, semantic_hint: str, explicit_hint: str = "") -> float:
    score = max(
        text_match_score(query, semantic_hint),
        text_match_score(explicit_hint, semantic_hint),
    )
    return round(score, 4)


def search_filters_from_args(args: argparse.Namespace) -> SearchFilters:
    return SearchFilters(
        query=str(getattr(args, "query", "") or ""),
        semantic_hint=str(getattr(args, "semantic_hint", "") or ""),
        category=str(getattr(args, "category", "") or ""),
        tags=[tag for tag in getattr(args, "tags", []) if str(tag).strip()],
        source=str(getattr(args, "source", "") or ""),
        document_type=str(getattr(args, "document_type", "") or ""),
        environment=str(getattr(args, "environment", "") or ""),
        workflow=str(getattr(args, "workflow", "") or ""),
        min_reliability=getattr(args, "min_reliability", None),
        min_freshness=getattr(args, "min_freshness", None),
        limit=max(0, int(getattr(args, "limit", 10) or 0)),
    )


def add_optional_filter(clauses: list[str], params: list[Any], field: str, value: str) -> None:
    if value:
        clauses.append(f"lower(d.{field}) = lower(?)")
        params.append(value)


def add_optional_min_filter(clauses: list[str], params: list[Any], field: str, value: float | None) -> None:
    if value is not None:
        clauses.append(f"coalesce(s.{field}, 0) >= ?")
        params.append(float(value))


def passes_query_filter(row: dict[str, Any], filters: SearchFilters) -> bool:
    if not filters.query:
        return True
    return text_match_score(
        filters.query,
        row["title"],
        row["content"],
        row["summary"],
        row["semantic_hint"],
        row["source_path"],
        " ".join(row["tags"]),
    ) > 0


def json_scalar(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def json_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: json_scalar(value) for key, value in record.items()}


def fetch_tags(conn: Any, knowledge_ids: list[str]) -> dict[str, list[str]]:
    if not knowledge_ids:
        return {}
    placeholders = ", ".join("?" for _ in knowledge_ids)
    rows = conn.execute(
        f"SELECT knowledge_id, tag FROM knowledge_tags WHERE knowledge_id IN ({placeholders}) ORDER BY tag",
        knowledge_ids,
    ).fetchall()
    tags: dict[str, list[str]] = {knowledge_id: [] for knowledge_id in knowledge_ids}
    for knowledge_id, tag in rows:
        tags.setdefault(str(knowledge_id), []).append(str(tag))
    return tags


def search_knowledge(db_path: Path, filters: SearchFilters) -> dict[str, Any]:
    if not db_path.exists():
        init_schema(db_path)
    clauses = ["d.status != 'deleted'"]
    params: list[Any] = []
    add_optional_filter(clauses, params, "category", filters.category)
    add_optional_filter(clauses, params, "source", filters.source)
    add_optional_filter(clauses, params, "document_type", filters.document_type)
    add_optional_filter(clauses, params, "environment", filters.environment)
    add_optional_filter(clauses, params, "workflow", filters.workflow)
    add_optional_min_filter(clauses, params, "reliability_score", filters.min_reliability)
    add_optional_min_filter(clauses, params, "freshness_score", filters.min_freshness)
    for tag in filters.tags:
        clauses.append(
            "EXISTS (SELECT 1 FROM knowledge_tags t WHERE t.knowledge_id = d.knowledge_id AND lower(t.tag) = lower(?))"
        )
        params.append(tag)
    where_sql = " AND ".join(clauses)
    with connect(db_path, read_only=True) as conn:
        rows = conn.execute(
            f"""
            SELECT
                d.knowledge_id, d.title, d.content, d.summary, d.semantic_hint, d.category,
                d.document_type, d.source, d.source_path, d.environment, d.workflow,
                d.content_hash, d.status, d.metadata_json, d.source_file, d.source_kind,
                d.created_at, d.updated_at,
                coalesce(s.reliability_score, 0) AS reliability_score,
                coalesce(s.relevance_score, 0) AS relevance_score,
                coalesce(s.freshness_score, 0) AS freshness_score,
                coalesce(s.duplication_score, 0) AS duplication_score,
                coalesce(s.total_score, 0) AS total_score,
                coalesce(s.optimization_score, 0) AS optimization_score,
                coalesce(s.optimization_decision, '') AS optimization_decision
            FROM knowledge_documents d
            LEFT JOIN knowledge_scores s ON s.knowledge_id = d.knowledge_id
            WHERE {where_sql}
            """,
            params,
        ).fetchall()
        columns = [column[0] for column in conn.description]
        records = [dict(zip(columns, row)) for row in rows]
        tags_by_id = fetch_tags(conn, [str(record["knowledge_id"]) for record in records])

    results: list[dict[str, Any]] = []
    for record in records:
        record = json_record(record)
        knowledge_id = str(record["knowledge_id"])
        record["tags"] = tags_by_id.get(knowledge_id, [])
        if not passes_query_filter(record, filters):
            continue
        keyword_score = text_match_score(
            filters.query,
            str(record["title"] or ""),
            str(record["content"] or ""),
            str(record["summary"] or ""),
            str(record["source_path"] or ""),
            " ".join(record["tags"]),
        )
        hint_score = semantic_hint_score(filters.query, str(record["semantic_hint"] or ""), filters.semantic_hint)
        final_score = round(
            keyword_score
            + hint_score
            + float(record["relevance_score"])
            + float(record["reliability_score"])
            + float(record["freshness_score"]),
            4,
        )
        results.append(
            {
                **record,
                "keyword_match_score": keyword_score,
                "semantic_hint_score": hint_score,
                "final_score": final_score,
            }
        )
    results.sort(key=lambda item: (float(item["final_score"]), str(item["updated_at"] or "")), reverse=True)
    limited = results[: filters.limit] if filters.limit else []
    return {
        "status": "completed",
        "artifact_type": "rag-duckdb-search-result",
        "generated_at": utc_now_iso(),
        "db": str(db_path),
        "query": filters.query,
        "filters": {
            "semantic_hint": filters.semantic_hint,
            "category": filters.category,
            "tags": filters.tags,
            "source": filters.source,
            "document_type": filters.document_type,
            "environment": filters.environment,
            "workflow": filters.workflow,
            "min_reliability": filters.min_reliability,
            "min_freshness": filters.min_freshness,
            "limit": filters.limit,
        },
        "candidate_count": len(results),
        "result_count": len(limited),
        "results": limited,
    }


def context_result(row: dict[str, Any], max_chars: int) -> dict[str, Any]:
    content = str(row.get("content") or "")
    if max_chars >= 0:
        content = content[:max_chars]
    return {
        "knowledge_id": row.get("knowledge_id", ""),
        "title": row.get("title", ""),
        "content": content,
        "semantic_hint": row.get("semantic_hint", ""),
        "source": row.get("source", ""),
        "source_path": row.get("source_path", ""),
        "document_type": row.get("document_type", ""),
        "category": row.get("category", ""),
        "tags": row.get("tags", []),
        "score": row.get("final_score", 0.0),
        "scores": {
            "keyword_match": row.get("keyword_match_score", 0.0),
            "semantic_hint": row.get("semantic_hint_score", 0.0),
            "relevance": row.get("relevance_score", 0.0),
            "reliability": row.get("reliability_score", 0.0),
            "freshness": row.get("freshness_score", 0.0),
        },
    }


def export_context(repo_root: Path, db_path: Path, filters: SearchFilters, output: Path, max_chars: int) -> dict[str, Any]:
    search = search_knowledge(db_path, filters)
    context = {
        "schema_version": "1.0",
        "artifact_type": "rag-duckdb-context",
        "query": filters.query,
        "generated_at": utc_now_iso(),
        "db": str(db_path),
        "filters": search["filters"],
        "candidate_count": search["candidate_count"],
        "result_count": search["result_count"],
        "results": [context_result(row, max_chars) for row in search["results"]],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "status": "completed",
        "artifact_type": "rag-duckdb-context-export",
        "output": relative_to_repo(repo_root, output),
        "result_count": context["result_count"],
        "candidate_count": context["candidate_count"],
        "context": context,
    }


def reference_query_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "knowledge_id": row.get("knowledge_id", ""),
        "title": row.get("title", ""),
        "source_path": row.get("source_path", ""),
        "document_type": row.get("document_type", ""),
        "category": row.get("category", ""),
        "score": row.get("final_score", 0.0),
    }


def register_reference_check_context(
    repo_root: Path,
    work_dir: Path | None,
    *,
    work_id: str,
    evidence_path: Path,
    evidence: dict[str, Any],
) -> dict[str, Any] | None:
    if work_dir is None:
        return None
    manifest = register_context(
        repo_root,
        work_dir,
        work_id=work_id or work_dir.name,
        context_type="rag-duckdb-reference-check",
        path=evidence_path,
        required=False,
        generated_by="runtime-rag-duckdb",
        owner="workflow",
        schema=RAG_DUCKDB_REFERENCE_CHECK_SCHEMA,
        status="available" if evidence.get("status") == "completed" else "human-check-required",
    )
    return {
        "context_manifest": relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir)),
        "manifest_contexts": [item.get("type") for item in manifest.get("contexts", [])],
    }


def verify_references(
    repo_root: Path,
    db_path: Path,
    queries: list[str],
    output: Path,
    min_results: int = 1,
    limit: int = 5,
    work_dir: Path | None = None,
    work_id: str = "",
    source_repository: dict[str, Any] | None = None,
) -> dict[str, Any]:
    effective_queries = [query for query in queries if query.strip()] or DEFAULT_REFERENCE_QUERIES
    checks: list[dict[str, Any]] = []
    for query in effective_queries:
        filters = SearchFilters(
            query=query,
            semantic_hint="",
            category="",
            tags=[],
            source="",
            document_type="",
            environment="",
            workflow="",
            min_reliability=None,
            min_freshness=None,
            limit=limit,
        )
        search = search_knowledge(db_path, filters)
        result_count = int(search["result_count"])
        checks.append(
            {
                "query": query,
                "status": "passed" if result_count >= min_results else "failed",
                "candidate_count": search["candidate_count"],
                "result_count": result_count,
                "min_results": min_results,
                "top_results": [reference_query_summary(row) for row in search["results"]],
            }
        )
    failed = [check for check in checks if check["status"] != "passed"]
    evidence = {
        "schema_version": "1.0",
        "artifact_type": "rag-duckdb-reference-check",
        "status": "completed" if not failed else "human-check-required",
        "generated_at": utc_now_iso(),
        "db": str(db_path),
        "output": relative_to_repo(repo_root, output),
        "query_count": len(checks),
        "passed_count": len(checks) - len(failed),
        "failed_count": len(failed),
        "checks": checks,
    }
    if source_repository:
        evidence["source_repository"] = source_repository
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    registration = register_reference_check_context(
        repo_root,
        work_dir,
        work_id=work_id,
        evidence_path=output,
        evidence=evidence,
    )
    if registration:
        evidence.update(registration)
        output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    db_path = resolve_repo_path(repo_root, args.db).resolve()
    if args.command == "init":
        return init_schema(db_path)

    if args.command == "ingest":
        policy = ingestion_optimizer.load_policy(repo_root, args.policy)
        return ingest_file(repo_root, db_path, resolve_repo_path(repo_root, args.file).resolve(), policy)
    if args.command == "migrate":
        policy = ingestion_optimizer.load_policy(repo_root, args.policy)
        return migrate_directory(
            repo_root,
            db_path,
            resolve_repo_path(repo_root, args.source).resolve(),
            policy,
            resolve_repo_path(repo_root, args.error_log).resolve(),
        )
    if args.command == "source":
        source_repo = resolve_repo_path(repo_root, getattr(args, "path", str(DEFAULT_SOURCE_REPO_PATH))).resolve()
        url = str(getattr(args, "url", DEFAULT_SOURCE_REPO_URL) or DEFAULT_SOURCE_REPO_URL)
        source_command = getattr(args, "source_command", "")
        if source_command == "status":
            return {
                "status": "completed",
                "artifact_type": "rag-knowledge-source",
                "action": "status",
                "source_repository": source_repo_metadata(repo_root, source_repo, url),
            }
        if source_command == "clone":
            return clone_source_repo(
                repo_root,
                source_repo,
                url,
                pull_if_exists=bool(getattr(args, "pull_if_exists", False)),
            )
        if source_command == "pull":
            return pull_source_repo(repo_root, source_repo, url)
        if source_command == "import-local":
            return import_local_rag_sources(
                repo_root,
                source_repo,
                url,
                clean=bool(getattr(args, "clean", False)),
            )
        raise ValueError(f"Unsupported source command: {source_command}")
    if args.command == "rebuild":
        policy = ingestion_optimizer.load_policy(repo_root, args.policy)
        sources = [resolve_repo_path(repo_root, source).resolve() for source in getattr(args, "source", [])]
        source_repository: dict[str, Any] | None = None
        source_repo_value = str(getattr(args, "source_repo", "") or "")
        if source_repo_value:
            source_repo = resolve_repo_path(repo_root, source_repo_value).resolve()
            source_repository = source_repo_metadata(
                repo_root,
                source_repo,
                str(getattr(args, "source_repo_url", DEFAULT_SOURCE_REPO_URL) or DEFAULT_SOURCE_REPO_URL),
            )
            if not source_repository.get("is_git_repo"):
                raise RuntimeError(
                    "Knowledge source repository is not available. "
                    f"Run `aiwfctl knowledge source clone --path {source_repo_value}` first."
                )
            if not sources:
                sources = source_repo_standard_sources(repo_root, source_repo)
        return rebuild_standard_sources(
            repo_root,
            db_path,
            sources,
            policy,
            resolve_repo_path(repo_root, args.error_log).resolve(),
            reset=bool(getattr(args, "reset", False)),
            source_repository=source_repository,
        )
    if args.command == "search":
        return search_knowledge(db_path, search_filters_from_args(args))
    if args.command == "export-context":
        return export_context(
            repo_root,
            db_path,
            search_filters_from_args(args),
            resolve_repo_path(repo_root, args.output).resolve(),
            int(args.max_chars),
        )
    if args.command == "verify":
        work_id = str(getattr(args, "work_id", "") or "")
        work_dir_value = str(getattr(args, "work_dir", "") or "")
        if not work_id and not work_dir_value:
            work_id = DEFAULT_REFERENCE_CHECK_WORK_ID
            work_dir_value = str(DEFAULT_REFERENCE_CHECK_WORK_DIR)
        work_dir = resolve_work_dir(repo_root, work_id, work_dir_value)
        source_repository = None
        source_repo_value = str(getattr(args, "source_repo", "") or "")
        if source_repo_value:
            source_repo = resolve_repo_path(repo_root, source_repo_value).resolve()
            source_repository = source_repo_metadata(repo_root, source_repo, DEFAULT_SOURCE_REPO_URL)
        return verify_references(
            repo_root,
            db_path,
            list(getattr(args, "query", []) or []),
            resolve_repo_path(repo_root, args.output).resolve(),
            min_results=int(getattr(args, "min_results", 1)),
            limit=int(getattr(args, "limit", 5)),
            work_dir=work_dir,
            work_id=work_id,
            source_repository=source_repository,
        )
    raise ValueError(f"Unsupported command: {args.command}")


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
