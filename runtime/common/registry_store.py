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
from runtime.constants.paths import (  # noqa: E402
    HUMAN_GATES_REGISTRY_FILE,
    KNOWLEDGE_SOURCE_REGISTRIES,
    REGISTRY_DB_PATH,
    SEARCH_TERMS_REGISTRY_FILE,
    TOOL_CANDIDATES_REGISTRY_FILE,
    WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE,
    WORKFLOW_HELP_REGISTRY_FILE,
)


DEFAULT_LEGACY_JSON_SOURCE_DIR = KNOWLEDGE_SOURCE_REGISTRIES


def registry_db_path(repo_root: Path) -> Path:
    return repo_root / REGISTRY_DB_PATH


def legacy_registry_dir(repo_root: Path) -> Path:
    return repo_root / "runtime" / "registries"


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


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def file_sha256(path: Path) -> str:
    import hashlib

    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
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
        return {"registry_version": "1.0", "terms": []}
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

    with connect(db_path) as conn:
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
        },
    }


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
    raise ValueError(f"Unsupported registry: {registry_name}")


def legacy_file_for(registry_name: str) -> str:
    return {
        "workflow_help": WORKFLOW_HELP_REGISTRY_FILE,
        "tool_candidates": TOOL_CANDIDATES_REGISTRY_FILE,
        "human_gates": HUMAN_GATES_REGISTRY_FILE,
        "workflow_environment_profiles": WORKFLOW_ENVIRONMENT_PROFILES_REGISTRY_FILE,
    }[registry_name]


def load_registry(repo_root: Path, registry_name: str, default: dict[str, Any] | None = None) -> Any:
    try:
        return load_from_duckdb(repo_root, registry_name)
    except FileNotFoundError:
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


def load_tool_candidates(repo_root: Path) -> dict[str, Any]:
    data = load_registry(repo_root, "tool_candidates", {"tools": []})
    if isinstance(data, dict):
        data.setdefault("tools", [])
    return data


def load_human_gates(repo_root: Path) -> dict[str, Any]:
    data = load_registry(repo_root, "human_gates", {"registry_version": "1.0", "gates": []})
    if isinstance(data, dict):
        data.setdefault("registry_version", "1.0")
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
    build.add_argument("--source-dir", default=str(DEFAULT_LEGACY_JSON_SOURCE_DIR))
    build.set_defaults(handler=run_build)
    sub.add_parser("summary").set_defaults(handler=run_summary)
    return parser


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def run_build(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    return build_registry_read_model(
        repo_root,
        resolve_repo_path(repo_root, args.source_dir),
        resolve_repo_path(repo_root, args.db),
    )


def run_summary(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    db_path = resolve_repo_path(repo_root, args.db)
    with connect(db_path, read_only=True) as conn:
        counts = {
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
            ]
        }
    return {
        "status": "completed",
        "artifact_type": "runtime-registry-duckdb-summary",
        "db": relative_to_repo(repo_root, db_path),
        "counts": counts,
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
