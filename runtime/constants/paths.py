from __future__ import annotations

import os
import re
from pathlib import Path


DEFAULT_KNOWLEDGE_SOURCE_REPO_NAME = "ariadne-knowledge-platform"
DEFAULT_KNOWLEDGE_SOURCE_REPO_OWNER = "inabako"
KNOWLEDGE_SOURCE_REPO_NAME_ENV_KEYS = (
    "ARIADNE_KNOWLEDGE_REPOSITORY",
    "ARIADNE_KNOWLEDGE_REPOSITORY_NAME",
    "AIWF_KNOWLEDGE_REPOSITORY",
    "AIWF_KNOWLEDGE_REPOSITORY_NAME",
)
KNOWLEDGE_SOURCE_REPO_OWNER_ENV_KEYS = (
    "ARIADNE_KNOWLEDGE_REPOSITORY_OWNER",
    "AIWF_KNOWLEDGE_REPOSITORY_OWNER",
    "GITHUB_OWNER",
)
KNOWLEDGE_SOURCE_REPO_URL_ENV_KEYS = (
    "ARIADNE_KNOWLEDGE_REPOSITORY_URL",
    "AIWF_KNOWLEDGE_REPOSITORY_URL",
)


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    settings: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key:
            settings[key] = value
    return settings


def _repo_root_env() -> dict[str, str]:
    repo_root = Path(__file__).resolve().parents[2]
    settings = {key: value for key, value in os.environ.items() if isinstance(value, str)}
    settings.update(_parse_env_file(repo_root / ".env"))
    return settings


def _first_env_value(settings: dict[str, str], keys: tuple[str, ...], default: str = "") -> str:
    for key in keys:
        value = settings.get(key, "").strip()
        if value:
            return value
    return default


def normalize_repository_name(value: str, default: str = DEFAULT_KNOWLEDGE_SOURCE_REPO_NAME) -> str:
    normalized = value.strip().replace("\\", "/").rstrip("/")
    if not normalized:
        return default
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    if "/" in normalized:
        normalized = normalized.rsplit("/", 1)[-1]
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "-", normalized).strip("-")
    return normalized or default


def knowledge_source_repo_name_from_settings(settings: dict[str, str]) -> str:
    return normalize_repository_name(
        _first_env_value(settings, KNOWLEDGE_SOURCE_REPO_NAME_ENV_KEYS, DEFAULT_KNOWLEDGE_SOURCE_REPO_NAME)
    )


def knowledge_source_repo_path_from_settings(settings: dict[str, str]) -> Path:
    return Path("work") / "db" / knowledge_source_repo_name_from_settings(settings)


def knowledge_source_repo_url_from_settings(settings: dict[str, str]) -> str:
    explicit = _first_env_value(settings, KNOWLEDGE_SOURCE_REPO_URL_ENV_KEYS)
    if explicit:
        return explicit
    owner = _first_env_value(settings, KNOWLEDGE_SOURCE_REPO_OWNER_ENV_KEYS, DEFAULT_KNOWLEDGE_SOURCE_REPO_OWNER)
    return f"https://github.com/{owner}/{knowledge_source_repo_name_from_settings(settings)}.git"


_ENV_SETTINGS = _repo_root_env()
KNOWLEDGE_SOURCE_REPO_NAME = knowledge_source_repo_name_from_settings(_ENV_SETTINGS)
KNOWLEDGE_SOURCE_REPO = knowledge_source_repo_path_from_settings(_ENV_SETTINGS)
KNOWLEDGE_SOURCE_REPO_URL = knowledge_source_repo_url_from_settings(_ENV_SETTINGS)
WORK_DB_ROOT = Path("work") / "db"
RAG_DIR_NAME = "rag"
REGISTRIES_DIR_NAME = "registries"
OPTIMIZED_CHUNKS_DIR_NAME = "optimized-chunks"
CHUNKS_DIR_NAME = "chunks"
JSONIZED_DIR_NAME = "jsonized"
NORMALIZED_DIR_NAME = "normalized"
INDEXES_DIR_NAME = "indexes"
EMBEDDINGS_DIR_NAME = "embeddings"
RETRIEVAL_DIR_NAME = "retrieval"

KNOWLEDGE_SOURCE_RAG = KNOWLEDGE_SOURCE_REPO / RAG_DIR_NAME
KNOWLEDGE_SOURCE_REGISTRIES = KNOWLEDGE_SOURCE_REPO / REGISTRIES_DIR_NAME
LEGACY_RETRIEVAL_PREFIX = f"{RAG_DIR_NAME}/{RETRIEVAL_DIR_NAME}/"

RUNTIME_RAG_ROOT = Path("runtime/rag")
RAG_INGESTION_POLICY_PATH = RUNTIME_RAG_ROOT / "policies" / "knowledge-ingestion-policy.json"
RAG_NORMALIZE_SCRIPT = RUNTIME_RAG_ROOT / "normalize_documents.py"
RAG_CHUNK_SCRIPT = RUNTIME_RAG_ROOT / "chunk_documents.py"
RAG_BUILD_INDEX_SCRIPT = RUNTIME_RAG_ROOT / "build_index.py"
RAG_EMBED_SCRIPT = RUNTIME_RAG_ROOT / "embed_chunks.py"
RAG_RETRIEVE_CONTEXT_SCRIPT = RUNTIME_RAG_ROOT / "retrieve_context.py"

# RAG JSON/JSONL artifacts are knowledge-source files; DuckDB and evidence stay under db/rag.
GENERATED_RAG = KNOWLEDGE_SOURCE_RAG

SOURCE_CORRECTIVE_ACTION_REPORTS = KNOWLEDGE_SOURCE_RAG / "corrective-action-report"
SOURCE_GITHUB_KNOWLEDGE = KNOWLEDGE_SOURCE_RAG / "github-knowledge"
SOURCE_REVIEW_COUNCIL = KNOWLEDGE_SOURCE_RAG / "review-council"
SOURCE_WORKSPACE_ENVIRONMENT = KNOWLEDGE_SOURCE_RAG / "workspace-environment"

GENERATED_NORMALIZED = GENERATED_RAG / NORMALIZED_DIR_NAME
GENERATED_CHUNKS = GENERATED_RAG / CHUNKS_DIR_NAME
GENERATED_OPTIMIZED_CHUNKS = GENERATED_RAG / OPTIMIZED_CHUNKS_DIR_NAME
GENERATED_JSONIZED = GENERATED_RAG / JSONIZED_DIR_NAME
GENERATED_INDEXES = GENERATED_RAG / INDEXES_DIR_NAME
GENERATED_EMBEDDINGS = GENERATED_RAG / EMBEDDINGS_DIR_NAME
GENERATED_RETRIEVAL = GENERATED_RAG / RETRIEVAL_DIR_NAME

KNOWLEDGE_SOURCE_LOCAL_BACKUP_DIRS = (
    KNOWLEDGE_SOURCE_REPO,
    KNOWLEDGE_SOURCE_RAG,
    KNOWLEDGE_SOURCE_REGISTRIES,
    SOURCE_CORRECTIVE_ACTION_REPORTS,
    SOURCE_GITHUB_KNOWLEDGE,
    SOURCE_REVIEW_COUNCIL,
    SOURCE_WORKSPACE_ENVIRONMENT,
    GENERATED_NORMALIZED,
    GENERATED_CHUNKS,
    GENERATED_OPTIMIZED_CHUNKS,
    GENERATED_JSONIZED,
    GENERATED_INDEXES,
    GENERATED_EMBEDDINGS,
    GENERATED_RETRIEVAL,
)

CHUNKS_INDEX = GENERATED_INDEXES / "chunks.jsonl"
EMBEDDINGS_INDEX = GENERATED_EMBEDDINGS / "chunks-embeddings.jsonl"
RAG_BUILD_RUN_LATEST = GENERATED_RETRIEVAL / "rag-build-run-latest.json"

DUCKDB_RAG_ROOT = Path("db/rag")
DUCKDB_DEFAULT_PATH = DUCKDB_RAG_ROOT / "ariadne-knowledge.duckdb"
DUCKDB_ERROR_LOG = DUCKDB_RAG_ROOT / "migration-errors.jsonl"
DUCKDB_EVIDENCE_DIR = DUCKDB_RAG_ROOT / "evidence"
DUCKDB_MIGRATION_EVIDENCE = DUCKDB_EVIDENCE_DIR / "migration-summary.json"
DUCKDB_REFERENCE_CHECK_OUTPUT = DUCKDB_EVIDENCE_DIR / "reference-check.json"
DUCKDB_REFERENCE_CHECK_WORK_DIR = DUCKDB_EVIDENCE_DIR
DUCKDB_INGESTION_EVIDENCE_DIR = DUCKDB_EVIDENCE_DIR / "ingestion"
DUCKDB_CONTEXT_MANIFEST = DUCKDB_EVIDENCE_DIR / "context" / "context-manifest.json"

REGISTRY_DB_PATH = Path("db/registries/registry.duckdb")
WORKFLOW_HELP_REGISTRY_FILE = "workflow_help.json"
SEARCH_TERMS_REGISTRY_FILE = "search_terms.json"
TOOL_CANDIDATES_REGISTRY_FILE = "tool_candidates.json"
HUMAN_GATES_REGISTRY_FILE = "human_gates.json"
WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE = "workflow_environment_profiles.json"

LEGACY_ROOT_RAG_PREFIX = "legacy-root-rag-"

WINDOWS_FLUTTER_BIN = Path(r"C:\flutter\bin")
WINDOWS_FLUTTER_EXECUTABLES = (
    WINDOWS_FLUTTER_BIN / "flutter.bat",
    WINDOWS_FLUTTER_BIN / "flutter.cmd",
    WINDOWS_FLUTTER_BIN / "flutter.exe",
)
WINDOWS_DART_EXECUTABLES = (
    WINDOWS_FLUTTER_BIN / "dart.bat",
    WINDOWS_FLUTTER_BIN / "dart.cmd",
    WINDOWS_FLUTTER_BIN / "dart.exe",
)
WINDOWS_DEFAULT_MSYS2_ROOT = Path(r"C:\msys64")
WINDOWS_MSYS2_BASH = WINDOWS_DEFAULT_MSYS2_ROOT / "usr" / "bin" / "bash.exe"
WINDOWS_GO_EXE = Path(r"C:\Program Files\Go\bin\go.exe")

SOURCE_REPO_STANDARD_DIRS = [
    Path(RAG_DIR_NAME) / OPTIMIZED_CHUNKS_DIR_NAME,
    Path(RAG_DIR_NAME) / CHUNKS_DIR_NAME,
    Path(RAG_DIR_NAME) / JSONIZED_DIR_NAME,
    Path(RAG_DIR_NAME) / NORMALIZED_DIR_NAME,
]

LOCAL_GENERATED_STANDARD_DIRS = [
    GENERATED_OPTIMIZED_CHUNKS,
    GENERATED_CHUNKS,
    GENERATED_JSONIZED,
    GENERATED_NORMALIZED,
]
