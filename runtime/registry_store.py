from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso  # noqa: E402


REGISTRY_DB_PATH = Path("db/registries/registry.duckdb")
DEFAULT_LEGACY_JSON_SOURCE_DIR = Path(
    "work/db/ariadne-knowledge-platform/registries"
)


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
        conn.execute("DROP TABLE IF EXISTS workflow_help_search_terms")
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
                command VARCHAR NOT NULL,
                workflow VARCHAR,
                skill VARCHAR,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (command)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE workflow_help_extensions (
                sort_order INTEGER NOT NULL,
                name VARCHAR NOT NULL,
                payload_json TEXT NOT NULL,
                PRIMARY KEY (name)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE workflow_help_search_terms (
                sort_order INTEGER NOT NULL,
                item_type VARCHAR NOT NULL,
                item_key VARCHAR NOT NULL,
                term VARCHAR NOT NULL,
                locale VARCHAR,
                kind VARCHAR,
                payload_json TEXT NOT NULL
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


def workflow_search_terms(item: dict[str, Any]) -> list[dict[str, str]]:
    terms: list[dict[str, str]] = []
    raw_terms = item.get("search_terms", [])
    if not isinstance(raw_terms, list):
        return terms
    for raw in raw_terms:
        if isinstance(raw, str):
            term = raw.strip()
            if term:
                terms.append({"term": term, "locale": "", "kind": "keyword"})
            continue
        if not isinstance(raw, dict):
            continue
        term = str(raw.get("term", "")).strip()
        if not term:
            continue
        terms.append(
            {
                "term": term,
                "locale": str(raw.get("locale", "")).strip(),
                "kind": str(raw.get("kind", "keyword")).strip() or "keyword",
            }
        )
    return terms


def insert_workflow_search_terms(
    conn: Any,
    item_type: str,
    item_key: str,
    terms: list[dict[str, str]],
    *,
    start_index: int,
) -> int:
    next_index = start_index
    for term in terms:
        conn.execute(
            "INSERT INTO workflow_help_search_terms VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                next_index,
                item_type,
                item_key,
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

    workflow_help = read_source_json(source_dir, "workflow_help.json")
    tool_candidates_payload = read_source_json(source_dir, "tool_candidates.json")
    human_gates_payload = read_source_json(source_dir, "human_gates.json")
    environments_payload = read_source_json(source_dir, "workflow_environment_profiles.json")

    with connect(db_path) as conn:
        insert_metadata(
            conn,
            "workflow_help",
            metadata_for(workflow_help, {"commands", "extensions"}),
            source_dir / "workflow_help.json",
            repo_root,
        )
        search_term_count = 0
        for index, item in enumerate(workflow_help.get("commands", [])):
            conn.execute(
                "INSERT INTO workflow_help_commands VALUES (?, ?, ?, ?, ?)",
                [
                    index,
                    str(item.get("command", "")),
                    str(item.get("workflow", "")),
                    str(item.get("skill", "")),
                    json_dumps(item),
                ],
            )
            search_term_count = insert_workflow_search_terms(
                conn,
                "command",
                str(item.get("command", "")),
                workflow_search_terms(item),
                start_index=search_term_count,
            )
        for index, item in enumerate(workflow_help.get("extensions", [])):
            conn.execute(
                "INSERT INTO workflow_help_extensions VALUES (?, ?, ?)",
                [index, str(item.get("name", "")), json_dumps(item)],
            )
            search_term_count = insert_workflow_search_terms(
                conn,
                "extension",
                str(item.get("name", "")),
                workflow_search_terms(item),
                start_index=search_term_count,
            )

        insert_metadata(
            conn,
            "tool_candidates",
            metadata_for(tool_candidates_payload, {"tools"}),
            source_dir / "tool_candidates.json",
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
            source_dir / "human_gates.json",
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
            source_dir / "workflow_environment_profiles.json",
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
            "workflow_help_search_terms",
            "tool_candidates",
            "human_gates",
            "workflow_environments",
            "environment_profiles",
            "environment_mappings",
        ],
        "counts": {
            "workflow_help_commands": len(workflow_help.get("commands", [])),
            "workflow_help_extensions": len(workflow_help.get("extensions", [])),
            "workflow_help_search_terms": search_term_count,
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
        SELECT item_type, item_key, payload_json
        FROM workflow_help_search_terms
        ORDER BY sort_order
        """
    ).fetchall()
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item_type, item_key, payload_json in rows:
        value = json.loads(payload_json)
        if isinstance(value, dict):
            grouped.setdefault((str(item_type), str(item_key)), []).append(value)
    for command in data.get("commands", []):
        key = ("command", str(command.get("command", "")))
        if key in grouped:
            command["_search_terms"] = grouped[key]
    for extension in data.get("extensions", []):
        key = ("extension", str(extension.get("name", "")))
        if key in grouped:
            extension["_search_terms"] = grouped[key]


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
        "workflow_help": "workflow_help.json",
        "tool_candidates": "tool_candidates.json",
        "human_gates": "human_gates.json",
        "workflow_environment_profiles": "workflow_environment_profiles.json",
    }[registry_name]


def load_registry(repo_root: Path, registry_name: str, default: dict[str, Any] | None = None) -> Any:
    try:
        return load_from_duckdb(repo_root, registry_name)
    except FileNotFoundError:
        sentinel = object()
        data = read_json(legacy_registry_dir(repo_root) / legacy_file_for(registry_name), default=sentinel)
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
                "workflow_help_search_terms",
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
