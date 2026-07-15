from __future__ import annotations

from pathlib import Path

from runtime.common import relative_to_repo


DEFAULT_DUCKDB_PATH = Path("db/rag/ariadne-knowledge.duckdb")
PROTECTED_RAG_CLEANUP_DIRS = (
    Path("db/rag"),
)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def protects_duckdb_read_model(repo_root: Path, target: Path) -> bool:
    resolved_repo = repo_root.resolve()
    resolved_target = target.resolve()
    resolved_db = (resolved_repo / DEFAULT_DUCKDB_PATH).resolve()
    protected_dirs = [(resolved_repo / item).resolve() for item in PROTECTED_RAG_CLEANUP_DIRS]
    if resolved_target in protected_dirs:
        return True
    return resolved_target == resolved_db or _is_relative_to(resolved_db, resolved_target)


def assert_safe_clean_output_target(repo_root: Path, target: Path) -> None:
    if protects_duckdb_read_model(repo_root, target):
        rel_target = relative_to_repo(repo_root, target)
        rel_db = DEFAULT_DUCKDB_PATH.as_posix()
        raise ValueError(
            "Refusing to clean protected RAG path "
            f"'{rel_target}' because it may remove the generated DuckDB read model '{rel_db}'. "
            "Use a narrower generated output directory, or rebuild the DuckDB read model explicitly "
            "with `aiwfctl knowledge rebuild --source-repo work/db/ariadne-knowledge-platform --reset`."
        )
