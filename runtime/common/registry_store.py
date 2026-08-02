from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso  # noqa: E402
from runtime.constants.runtime_values import FILE_HASH_CHUNK_BYTES, REGISTRY_VERSION  # noqa: E402
from runtime.constants.paths import (  # noqa: E402
    CTL_HELP_USAGE_REGISTRY_FILE,
    HUMAN_GATES_REGISTRY_FILE,
    KNOWLEDGE_SOURCE_REGISTRIES,
    REGISTRY_DB_PATH,
    RUNTIME_HELP_CAPABILITIES_REGISTRY_FILE,
    SEARCH_TERMS_REGISTRY_FILE,
    TEMPLATE_REGISTRIES,
    TOOL_CANDIDATES_REGISTRY_FILE,
    WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE,
    WORKFLOW_HELP_REGISTRY_FILE,
)


DEFAULT_LEGACY_JSON_SOURCE_DIR = KNOWLEDGE_SOURCE_REGISTRIES
DEFAULT_TEMPLATE_JSON_SOURCE_DIR = TEMPLATE_REGISTRIES
REQUIRED_REGISTRY_SOURCE_FILES = (
    WORKFLOW_HELP_REGISTRY_FILE,
    TOOL_CANDIDATES_REGISTRY_FILE,
    HUMAN_GATES_REGISTRY_FILE,
    WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE,
    CTL_HELP_USAGE_REGISTRY_FILE,
    RUNTIME_HELP_CAPABILITIES_REGISTRY_FILE,
)

DOCUMENT_REGISTRY_FILES = {
    "ctl_help_usage": CTL_HELP_USAGE_REGISTRY_FILE,
    "runtime_help_capabilities": RUNTIME_HELP_CAPABILITIES_REGISTRY_FILE,
}


def registry_db_path(repo_root: Path) -> Path:
    return repo_root / REGISTRY_DB_PATH


def legacy_registry_dir(repo_root: Path) -> Path:
    return repo_root / "runtime" / "registries"


def default_source_dir(repo_root: Path) -> Path:
    template_source = repo_root / DEFAULT_TEMPLATE_JSON_SOURCE_DIR
    if source_registry_available(template_source):
        return template_source
    return repo_root / DEFAULT_LEGACY_JSON_SOURCE_DIR


def missing_source_files(source_dir: Path) -> list[str]:
    return [name for name in REQUIRED_REGISTRY_SOURCE_FILES if not (source_dir / name).is_file()]


def source_registry_available(source_dir: Path) -> bool:
    return not missing_source_files(source_dir)


def connect(db_path: Path, read_only: bool = False):
    try:
        import duckdb
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency boundary
        raise RuntimeError("DuckDB is not installed. Run runtime via uv so pyproject dependencies are available.") from exc
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path), read_only=read_only)


def init_schema(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS registry_metadata")
        conn.execute("DROP TABLE IF EXISTS workflow_help_commands")
        conn.execute("DROP TABLE IF EXISTS workflow_help_extensions")
        conn.execute("DROP TABLE IF EXISTS search_terms")
        conn.execute("DROP TABLE IF EXISTS tool_candidates")
        conn.execute("DROP TABLE IF EXISTS human_gates")
        conn.execute("DROP TABLE IF EXISTS workflow_environments")
        conn.execute("DROP TABLE IF EXISTS environment_profiles")
        conn.execute("DROP TABLE IF EXISTS environment_mappings")
        conn.execute("DROP TABLE IF EXISTS registry_documents")
        conn.execute(
            """
            CREATE TABLE registry_metadata (
                registry_name VARCHAR PRIMARY KEY,
                metadata_json TEXT NOT NULL,
                source_path VARCHAR NOT NULL,
                source_sha256 VARCHAR NOT NULL,
                built_at VARCHAR NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE workflow_help_commands (
                sort_order INTEGER NOT NULL,
                id VARCHAR NOT NULL,
                command VARCHAR NOT NULL,
                workflow VARCHAR,
                skill VARCHAR,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE workflow_help_extensions (
                sort_order INTEGER NOT NULL,
                id VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE search_terms (
                sort_order INTEGER NOT NULL,
                id VARCHAR NOT NULL,
                owner_registry VARCHAR NOT NULL,
                owner_type VARCHAR NOT NULL,
                owner_id VARCHAR NOT NULL,
                term VARCHAR NOT NULL,
                locale VARCHAR,
                kind VARCHAR,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE tool_candidates (
                sort_order INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                default_mode VARCHAR,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (name)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE human_gates (
                sort_order INTEGER NOT NULL,
                id VARCHAR NOT NULL,
                requires_human_check BOOLEAN,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE workflow_environments (
                sort_order INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                backend VARCHAR,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (name)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE environment_profiles (
                sort_order INTEGER NOT NULL,
                id VARCHAR NOT NULL,
                environment VARCHAR,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE environment_mappings (
                sort_order INTEGER NOT NULL,
                subject_type VARCHAR,
                subject VARCHAR,
                payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE registry_documents (
                registry_name VARCHAR PRIMARY KEY,
                payload_json TEXT NOT NULL
            )
            """
        )


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def file_sha256(path: Path) -> str:
    import hashlib

    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(FILE_HASH_CHUNK_BYTES), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_source_json(source_dir: Path, name: str) -> dict[str, Any]:
    data = read_json(source_dir / name, default={})
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be a JSON object.")
    return data


def metadata_for(payload: dict[str, Any], excluded_keys: set[str]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key not in excluded_keys}


def snake_id(value: str) -> str:
    normalized = value.strip().lower().lstrip("/")
    chars = [char if char.isalnum() else "_" for char in normalized]
    slug = "_".join(part for part in "".join(chars).split("_") if part)
    return slug or "unknown"


def is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
    except ValueError:
        return False
    return True


def search_term_uuid(owner_id: str, term: str, locale: str, kind: str, index: int) -> str:
    seed = f"ariadne:search_terms:{owner_id}:{term}:{locale}:{kind}:{index}"
    return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))


def workflow_help_id(item_type: str, item: dict[str, Any]) -> str:
    explicit_id = str(item.get("id", "")).strip()
    if explicit_id and ":" not in explicit_id and "-" not in explicit_id:
        return explicit_id
    if item_type == "command":
        return snake_id(str(item.get("command", "")))
    return snake_id(str(item.get("name", "")))


def normalize_search_term(raw: Any, *, fallback_id: str = "", owner_id: str = "", index: int = 0) -> dict[str, str] | None:
    if isinstance(raw, str):
        term = raw.strip()
        if not term:
            return None
        return {
            "id": fallback_id if is_uuid(fallback_id) else search_term_uuid(owner_id, term, "", "keyword", index),
            "owner_registry": "workflow_help",
            "owner_id": owner_id,
            "term": term,
            "locale": "",
            "kind": "keyword",
        }
    if not isinstance(raw, dict):
        return None
    term = str(raw.get("term", "")).strip()
    if not term:
        return None
    locale = str(raw.get("locale", "")).strip()
    kind = str(raw.get("kind", "keyword")).strip() or "keyword"
    raw_id = str(raw.get("id", "")).strip()
    fallback = fallback_id if is_uuid(fallback_id) else ""
    term_id = raw_id if is_uuid(raw_id) else fallback or search_term_uuid(owner_id, term, locale, kind, index)
    return {
        "id": term_id,
        "owner_registry": str(raw.get("owner_registry", "workflow_help")).strip() or "workflow_help",
        "owner_id": str(raw.get("owner_id", owner_id)).strip() or owner_id,
        "term": term,
        "locale": locale,
        "kind": kind,
    }


def inline_workflow_search_terms(item: dict[str, Any], *, owner_id: str) -> list[dict[str, str]]:
    terms: list[dict[str, str]] = []
    raw_terms = item.get("search_terms", [])
    if not isinstance(raw_terms, list):
        return terms
    for index, raw in enumerate(raw_terms):
        term = normalize_search_term(raw, owner_id=owner_id, index=index)
        if term:
            terms.append(term)
    return terms


def read_search_terms_source(source_dir: Path) -> dict[str, Any]:
    path = source_dir / SEARCH_TERMS_REGISTRY_FILE
    data = read_json(path, default={})
    if data in ({}, None):
        return {"registry_version": REGISTRY_VERSION, "terms": []}
    if not isinstance(data, dict):
        raise ValueError(f"{SEARCH_TERMS_REGISTRY_FILE} must be a JSON object.")
    data.setdefault("terms", [])
    if not isinstance(data["terms"], list):
        raise ValueError(f"{SEARCH_TERMS_REGISTRY_FILE} terms must be a JSON array.")
    return data


def search_terms_by_owner(search_terms_payload: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for index, raw in enumerate(search_terms_payload.get("terms", [])):
        term = normalize_search_term(raw, index=index)
        if not term:
            continue
        owner_id = term["owner_id"]
        if owner_id:
            grouped.setdefault(owner_id, []).append(term)
    return grouped


def insert_search_terms(
    conn: Any,
    terms: list[dict[str, str]],
    *,
    start_index: int,
) -> int:
    next_index = start_index
    for term in terms:
        conn.execute(
            "INSERT INTO search_terms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                next_index,
                term["id"],
                term.get("owner_registry", "workflow_help"),
                term.get("owner_type", "workflow_help"),
                term["owner_id"],
                term["term"],
                term.get("locale", ""),
                term.get("kind", ""),
                json_dumps(term),
            ],
        )
        next_index += 1
    return next_index


def insert_metadata(conn: Any, registry_name: str, metadata: dict[str, Any], source_path: Path, repo_root: Path) -> None:
    conn.execute(
        "INSERT INTO registry_metadata VALUES (?, ?, ?, ?, ?)",
        [
            registry_name,
            json_dumps(metadata),
            relative_to_repo(repo_root, source_path),
            file_sha256(source_path),
            utc_now_iso(),
        ],
    )


def insert_registry_document(conn: Any, registry_name: str, payload: dict[str, Any], source_path: Path, repo_root: Path) -> None:
    insert_metadata(conn, registry_name, metadata_for(payload, set()), source_path, repo_root)
    conn.execute("INSERT INTO registry_documents VALUES (?, ?)", [registry_name, json_dumps(payload)])


def build_registry_read_model(repo_root: Path, source_dir: Path, db_path: Path) -> dict[str, Any]:
    source_dir = source_dir.resolve()
    db_path = db_path.resolve()
    init_schema(db_path)

    workflow_help = read_source_json(source_dir, WORKFLOW_HELP_REGISTRY_FILE)
    search_terms_source_path = source_dir / SEARCH_TERMS_REGISTRY_FILE
    search_terms_payload = read_search_terms_source(source_dir)
    search_terms = search_terms_by_owner(search_terms_payload)
    tool_candidates_payload = read_source_json(source_dir, TOOL_CANDIDATES_REGISTRY_FILE)
    human_gates_payload = read_source_json(source_dir, HUMAN_GATES_REGISTRY_FILE)
    environments_payload = read_source_json(source_dir, WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE)
    document_payloads = {
        registry_name: read_source_json(source_dir, file_name)
        for registry_name, file_name in DOCUMENT_REGISTRY_FILES.items()
    }

    with connect(db_path) as conn:
        for registry_name, payload in document_payloads.items():
            insert_registry_document(conn, registry_name, payload, source_dir / DOCUMENT_REGISTRY_FILES[registry_name], repo_root)

        insert_metadata(
            conn,
            "workflow_help",
            metadata_for(workflow_help, {"commands", "extensions"}),
            source_dir / WORKFLOW_HELP_REGISTRY_FILE,
            repo_root,
        )
        if search_terms_source_path.exists():
            insert_metadata(
                conn,
                "search_terms",
                metadata_for(search_terms_payload, {"terms"}),
                search_terms_source_path,
                repo_root,
            )
        search_term_count = 0
        for index, item in enumerate(workflow_help.get("commands", [])):
            owner_id = workflow_help_id("command", item)
            conn.execute(
                "INSERT INTO workflow_help_commands VALUES (?, ?, ?, ?, ?, ?)",
                [
                    index,
                    owner_id,
                    str(item.get("command", "")),
                    str(item.get("workflow", "")),
                    str(item.get("skill", "")),
                    json_dumps(item),
                ],
            )
            terms = [*search_terms.get(owner_id, []), *inline_workflow_search_terms(item, owner_id=owner_id)]
            for term in terms:
                term["owner_type"] = "command"
            search_term_count = insert_search_terms(
                conn,
                terms,
                start_index=search_term_count,
            )
        for index, item in enumerate(workflow_help.get("extensions", [])):
            owner_id = workflow_help_id("extension", item)
            conn.execute(
                "INSERT INTO workflow_help_extensions VALUES (?, ?, ?, ?)",
                [index, owner_id, str(item.get("name", "")), json_dumps(item)],
            )
            terms = [*search_terms.get(owner_id, []), *inline_workflow_search_terms(item, owner_id=owner_id)]
            for term in terms:
                term["owner_type"] = "extension"
            search_term_count = insert_search_terms(
                conn,
                terms,
                start_index=search_term_count,
            )

        insert_metadata(
            conn,
            "tool_candidates",
            metadata_for(tool_candidates_payload, {"tools"}),
            source_dir / TOOL_CANDIDATES_REGISTRY_FILE,
            repo_root,
        )
        for index, item in enumerate(tool_candidates_payload.get("tools", [])):
            conn.execute(
                "INSERT INTO tool_candidates VALUES (?, ?, ?, ?)",
                [index, str(item.get("name", "")), str(item.get("default_mode", "")), json_dumps(item)],
            )

        insert_metadata(
            conn,
            "human_gates",
            metadata_for(human_gates_payload, {"gates"}),
            source_dir / HUMAN_GATES_REGISTRY_FILE,
            repo_root,
        )
        for index, item in enumerate(human_gates_payload.get("gates", [])):
            conn.execute(
                "INSERT INTO human_gates VALUES (?, ?, ?, ?)",
                [index, str(item.get("id", "")), bool(item.get("requires_human_check", True)), json_dumps(item)],
            )

        insert_metadata(
            conn,
            "workflow_environment_profiles",
            metadata_for(environments_payload, {"environments", "profiles", "mappings"}),
            source_dir / WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE,
            repo_root,
        )
        for index, item in enumerate(environments_payload.get("environments", [])):
            conn.execute(
                "INSERT INTO workflow_environments VALUES (?, ?, ?, ?)",
                [index, str(item.get("name", "")), str(item.get("backend", "")), json_dumps(item)],
            )
        for index, item in enumerate(environments_payload.get("profiles", [])):
            conn.execute(
                "INSERT INTO environment_profiles VALUES (?, ?, ?, ?)",
                [index, str(item.get("id", "")), str(item.get("environment", "")), json_dumps(item)],
            )
        for index, item in enumerate(environments_payload.get("mappings", [])):
            conn.execute(
                "INSERT INTO environment_mappings VALUES (?, ?, ?, ?)",
                [index, str(item.get("subject_type", "")), str(item.get("subject", "")), json_dumps(item)],
            )

    return {
        "status": "completed",
        "artifact_type": "runtime-registry-duckdb-read-model",
        "db": relative_to_repo(repo_root, db_path),
        "source_dir": relative_to_repo(repo_root, source_dir),
        "tables": [
            "workflow_help_commands",
            "workflow_help_extensions",
            "search_terms",
            "tool_candidates",
            "human_gates",
            "workflow_environments",
            "environment_profiles",
            "environment_mappings",
            "registry_documents",
        ],
        "counts": {
            "workflow_help_commands": len(workflow_help.get("commands", [])),
            "workflow_help_extensions": len(workflow_help.get("extensions", [])),
            "search_terms": search_term_count,
            "tool_candidates": len(tool_candidates_payload.get("tools", [])),
            "human_gates": len(human_gates_payload.get("gates", [])),
            "workflow_environments": len(environments_payload.get("environments", [])),
            "environment_profiles": len(environments_payload.get("profiles", [])),
            "environment_mappings": len(environments_payload.get("mappings", [])),
            "registry_documents": len(document_payloads),
        },
    }


def registry_table_counts(db_path: Path) -> dict[str, int]:
    with connect(db_path, read_only=True) as conn:
        return {
            table: conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            for table in [
                "workflow_help_commands",
                "workflow_help_extensions",
                "search_terms",
                "tool_candidates",
                "human_gates",
                "workflow_environments",
                "environment_profiles",
                "environment_mappings",
                "registry_documents",
            ]
        }


def ensure_or_rebuild_registry_read_model(
    repo_root: Path,
    source_dir: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    try:
        return ensure_registry_read_model(repo_root, source_dir, db_path)
    except Exception:
        return ensure_registry_read_model(repo_root, source_dir, db_path, rebuild=True)


def ensure_registry_read_model(
    repo_root: Path,
    source_dir: Path | None = None,
    db_path: Path | None = None,
    *,
    rebuild: bool = False,
) -> dict[str, Any]:
    source = (source_dir or default_source_dir(repo_root)).resolve()
    target = (db_path or registry_db_path(repo_root)).resolve()
    if target.exists() and not rebuild:
        try:
            counts = registry_table_counts(target)
        except Exception:
            return ensure_registry_read_model(repo_root, source_dir, db_path, rebuild=True)
        return {
            "status": "completed",
            "artifact_type": "runtime-registry-duckdb-read-model",
            "action": "existing",
            "db": relative_to_repo(repo_root, target),
            "source_dir": relative_to_repo(repo_root, source),
            "counts": counts,
        }

    missing = missing_source_files(source)
    if missing:
        return {
            "status": "skipped",
            "artifact_type": "runtime-registry-duckdb-read-model",
            "action": "missing-source",
            "db": relative_to_repo(repo_root, target),
            "source_dir": relative_to_repo(repo_root, source),
            "missing_sources": [relative_to_repo(repo_root, source / name) for name in missing],
        }

    existed = target.exists()
    result = build_registry_read_model(repo_root, source, target)
    result["action"] = "rebuilt" if existed else "built"
    return result


def load_metadata(conn: Any, registry_name: str) -> dict[str, Any]:
    row = conn.execute("SELECT metadata_json FROM registry_metadata WHERE registry_name = ?", [registry_name]).fetchone()
    if not row:
        return {}
    data = json.loads(row[0])
    return data if isinstance(data, dict) else {}


def load_payloads(conn: Any, table: str) -> list[dict[str, Any]]:
    rows = conn.execute(f"SELECT payload_json FROM {table} ORDER BY sort_order").fetchall()
    return [json.loads(row[0]) for row in rows]


def attach_workflow_search_terms(conn: Any, data: dict[str, Any]) -> None:
    rows = conn.execute(
        """
        SELECT owner_type, owner_id, payload_json
        FROM search_terms
        WHERE owner_registry = 'workflow_help'
        ORDER BY sort_order
        """
    ).fetchall()
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for owner_type, owner_id, payload_json in rows:
        value = json.loads(payload_json)
        if isinstance(value, dict):
            grouped.setdefault((str(owner_type), str(owner_id)), []).append(value)
    for command in data.get("commands", []):
        key = ("command", workflow_help_id("command", command))
        if key in grouped:
            command["_search_terms"] = grouped[key]
    for extension in data.get("extensions", []):
        key = ("extension", workflow_help_id("extension", extension))
        if key in grouped:
            extension["_search_terms"] = grouped[key]


def attach_workflow_search_terms_from_json(data: dict[str, Any], search_terms_payload: dict[str, Any]) -> None:
    grouped = search_terms_by_owner(search_terms_payload)
    for command in data.get("commands", []):
        owner_id = workflow_help_id("command", command)
        if owner_id in grouped:
            command["_search_terms"] = grouped[owner_id]
    for extension in data.get("extensions", []):
        owner_id = workflow_help_id("extension", extension)
        if owner_id in grouped:
            extension["_search_terms"] = grouped[owner_id]


def load_from_duckdb(repo_root: Path, registry_name: str) -> dict[str, Any]:
    db_path = registry_db_path(repo_root)
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    with connect(db_path, read_only=True) as conn:
        if registry_name == "workflow_help":
            data = load_metadata(conn, registry_name)
            data["commands"] = load_payloads(conn, "workflow_help_commands")
            data["extensions"] = load_payloads(conn, "workflow_help_extensions")
            attach_workflow_search_terms(conn, data)
            return data
        if registry_name == "tool_candidates":
            data = load_metadata(conn, registry_name)
            data["tools"] = load_payloads(conn, "tool_candidates")
            return data
        if registry_name == "human_gates":
            data = load_metadata(conn, registry_name)
            data["gates"] = load_payloads(conn, "human_gates")
            return data
        if registry_name == "workflow_environment_profiles":
            data = load_metadata(conn, registry_name)
            data["environments"] = load_payloads(conn, "workflow_environments")
            data["profiles"] = load_payloads(conn, "environment_profiles")
            data["mappings"] = load_payloads(conn, "environment_mappings")
            return data
        if registry_name in DOCUMENT_REGISTRY_FILES:
            row = conn.execute("SELECT payload_json FROM registry_documents WHERE registry_name = ?", [registry_name]).fetchone()
            if not row:
                return {}
            data = json.loads(row[0])
            return data if isinstance(data, dict) else {}
    raise ValueError(f"Unsupported registry: {registry_name}")


def legacy_file_for(registry_name: str) -> str:
    return {
        "workflow_help": WORKFLOW_HELP_REGISTRY_FILE,
        "tool_candidates": TOOL_CANDIDATES_REGISTRY_FILE,
        "human_gates": HUMAN_GATES_REGISTRY_FILE,
        "workflow_environment_profiles": WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE,
        "ctl_help_usage": CTL_HELP_USAGE_REGISTRY_FILE,
        "runtime_help_capabilities": RUNTIME_HELP_CAPABILITIES_REGISTRY_FILE,
    }[registry_name]


def load_registry(repo_root: Path, registry_name: str, default: dict[str, Any] | None = None) -> Any:
    try:
        return load_from_duckdb(repo_root, registry_name)
    except Exception:
        ensure_result = ensure_or_rebuild_registry_read_model(repo_root)
        if ensure_result.get("action") in {"built", "rebuilt"}:
            return load_from_duckdb(repo_root, registry_name)
        sentinel = object()
        registry_dir = legacy_registry_dir(repo_root)
        data = read_json(registry_dir / legacy_file_for(registry_name), default=sentinel)
        if registry_name == "workflow_help" and isinstance(data, dict):
            attach_workflow_search_terms_from_json(data, read_search_terms_source(registry_dir))
        return (default or {}) if data is sentinel else data


def load_workflow_help(repo_root: Path) -> dict[str, Any]:
    data = load_registry(repo_root, "workflow_help", {"commands": [], "extensions": []})
    if isinstance(data, dict):
        data.setdefault("commands", [])
        data.setdefault("extensions", [])
    return data


def load_ctl_help_usage(repo_root: Path) -> dict[str, Any]:
    data = load_registry(repo_root, "ctl_help_usage", {})
    if not isinstance(data, dict):
        data = {}
    return data


def load_runtime_help_capabilities(repo_root: Path) -> dict[str, Any]:
    data = load_registry(repo_root, "runtime_help_capabilities", {})
    if not isinstance(data, dict):
        data = {}
    return data


def load_tool_candidates(repo_root: Path) -> dict[str, Any]:
    data = load_registry(repo_root, "tool_candidates", {"tools": []})
    if isinstance(data, dict):
        data.setdefault("tools", [])
    return data


def load_human_gates(repo_root: Path) -> dict[str, Any]:
    data = load_registry(repo_root, "human_gates", {"registry_version": REGISTRY_VERSION, "gates": []})
    if isinstance(data, dict):
        data.setdefault("registry_version", REGISTRY_VERSION)
        data.setdefault("gates", [])
    return data


def load_environment_profiles(repo_root: Path) -> dict[str, Any]:
    data = load_registry(
        repo_root,
        "workflow_environment_profiles",
        {"environments": [], "profiles": [], "mappings": []},
    )
    if isinstance(data, dict):
        data.setdefault("environments", [])
        data.setdefault("profiles", [])
        data.setdefault("mappings", [])
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build or inspect the runtime registry DuckDB read model.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--db", default=str(REGISTRY_DB_PATH))
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--source-dir", default="")
    build.set_defaults(handler=run_build)
    ensure = sub.add_parser("ensure")
    ensure.add_argument("--source-dir", default="")
    ensure.add_argument("--rebuild", action="store_true")
    ensure.set_defaults(handler=run_ensure)
    sub.add_parser("summary").set_defaults(handler=run_summary)
    return parser


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def run_build(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    source_dir = resolve_repo_path(repo_root, args.source_dir) if args.source_dir else default_source_dir(repo_root)
    return build_registry_read_model(
        repo_root,
        source_dir,
        resolve_repo_path(repo_root, args.db),
    )


def run_ensure(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    source_dir = resolve_repo_path(repo_root, args.source_dir) if args.source_dir else None
    return ensure_registry_read_model(
        repo_root,
        source_dir,
        resolve_repo_path(repo_root, args.db),
        rebuild=bool(args.rebuild),
    )


def run_summary(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    db_path = resolve_repo_path(repo_root, args.db)
    ensure_or_rebuild_registry_read_model(repo_root, db_path=db_path)
    return {
        "status": "completed",
        "artifact_type": "runtime-registry-duckdb-summary",
        "db": relative_to_repo(repo_root, db_path),
        "counts": registry_table_counts(db_path),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
