from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, relative_to_repo, utc_now_iso, write_json  # noqa: E402
from runtime.constants.paths import GENERATED_JSONIZED, GENERATED_RETRIEVAL, LEGACY_RETRIEVAL_PREFIX  # noqa: E402


CURRENT_RETRIEVAL_PREFIX = GENERATED_RETRIEVAL.as_posix() + "/"


UUID_JSON_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.json$")
UUID_PREFIX_RE = re.compile(r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})_")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Migrate retrieval artifacts to UUID-named JSON files and remove duplicate Markdown."
    )
    parser.add_argument("--retrieval-dir", default=str(GENERATED_RETRIEVAL))
    parser.add_argument("--jsonized-dir", default=str(GENERATED_JSONIZED))
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--delete-source", action="store_true")
    parser.add_argument("--delete-duplicate-markdown", action="store_true")
    parser.add_argument("--repair-from-jsonized", action="store_true")
    parser.add_argument("--prune-legacy-migrations", action="store_true")
    return parser


def artifact_type_from_name(path: Path) -> str:
    name = path.name
    if name.endswith("_context-pack.json"):
        return "rag-context-pack"
    if name.endswith("_retrieval-result.json"):
        return "rag-retrieval-result"
    if name.endswith("_rag-load-dispatch.json"):
        return "rag-load-dispatch"
    return "rag-retrieval-artifact"


def artifact_id_for(repo_root: Path, path: Path, payload: dict[str, Any], artifact_type: str) -> str:
    rel_path = relative_to_repo(repo_root, path)
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-retrieval:{artifact_type}:{rel_path}"))


def artifact_id_for_rel_path(rel_path: str, artifact_type: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-retrieval:{artifact_type}:{rel_path}"))


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def replace_refs(value: Any, path_map: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old_path, new_path in path_map.items():
            value = value.replace(old_path, new_path)
        return value
    if isinstance(value, list):
        return [replace_refs(item, path_map) for item in value]
    if isinstance(value, dict):
        return {key: replace_refs(item, path_map) for key, item in value.items()}
    return value


def is_retrieval_artifact_ref(source_path: str) -> bool:
    return source_path.startswith((LEGACY_RETRIEVAL_PREFIX, CURRENT_RETRIEVAL_PREFIX))


def companion_json_for_markdown(path: Path) -> Path | None:
    if path.name.endswith("_context-pack.md"):
        return path.with_name(path.name.removesuffix(".md") + ".json")
    if path.name.endswith("_rag-load-dispatch.md"):
        return path.with_name(path.name.removesuffix(".md") + ".json")
    return None


def markdown_artifact(repo_root: Path, path: Path) -> dict[str, Any]:
    artifact_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"rag-retrieval-markdown:{relative_to_repo(repo_root, path)}"))
    return {
        "schema_version": "1.0",
        "artifact_type": "rag-retrieval-markdown-source",
        "artifact_id": artifact_id,
        "created_at": utc_now_iso(),
        "source_path": relative_to_repo(repo_root, path),
        "source_extension": path.suffix.lower(),
        "content": path.read_text(encoding="utf-8-sig", errors="replace"),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    retrieval_dir = (
        repo_root / args.retrieval_dir if not Path(args.retrieval_dir).is_absolute() else Path(args.retrieval_dir)
    ).resolve()
    jsonized_dir = (
        repo_root / args.jsonized_dir if not Path(args.jsonized_dir).is_absolute() else Path(args.jsonized_dir)
    ).resolve()
    if not retrieval_dir.exists():
        raise FileNotFoundError(f"RAG retrieval directory not found: {retrieval_dir}")

    migrations: list[dict[str, Any]] = []
    path_map: dict[str, str] = {}
    desired_targets: set[Path] = set()
    json_sources = sorted(path for path in retrieval_dir.glob("*.json") if not UUID_JSON_RE.match(path.name.lower()))

    for source in json_sources:
        payload = read_json(source)
        artifact_type = str(payload.get("artifact_type") or artifact_type_from_name(source))
        artifact_id = artifact_id_for(repo_root, source, payload, artifact_type)
        target = retrieval_dir / f"{artifact_id}.json"
        old_rel = relative_to_repo(repo_root, source)
        new_rel = relative_to_repo(repo_root, target)
        path_map[old_rel] = new_rel
        desired_targets.add(target.resolve())
        migrations.append(
            {
                "source": source,
                "target": target,
                "payload": payload,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "old_rel": old_rel,
                "new_rel": new_rel,
            }
        )

    if args.repair_from_jsonized and jsonized_dir.exists():
        for wrapper_path in sorted(jsonized_dir.glob("*.json")):
            wrapper = read_json(wrapper_path)
            source_path = str(wrapper.get("source_path", ""))
            source_name = Path(source_path).name
            if not is_retrieval_artifact_ref(source_path):
                continue
            if wrapper.get("source_format") != "json":
                continue
            if UUID_JSON_RE.match(source_name.lower()):
                continue
            payload = wrapper.get("payload")
            if not isinstance(payload, dict):
                continue
            artifact_type = str(payload.get("artifact_type") or artifact_type_from_name(Path(source_name)))
            artifact_id = artifact_id_for_rel_path(source_path, artifact_type)
            target = retrieval_dir / f"{artifact_id}.json"
            path_map[source_path] = relative_to_repo(repo_root, target)
            desired_targets.add(target.resolve())
            migrations.append(
                {
                    "source": repo_root / source_path,
                    "target": target,
                    "payload": payload,
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "old_rel": source_path,
                    "new_rel": relative_to_repo(repo_root, target),
                    "from_jsonized": relative_to_repo(repo_root, wrapper_path),
                }
            )

    written: list[dict[str, str]] = []
    deleted: list[str] = []
    for migration in migrations:
        payload = replace_refs(migration["payload"], path_map)
        payload.setdefault("schema_version", "1.0")
        payload["artifact_type"] = migration["artifact_type"]
        if migration["artifact_type"] == "rag-load-dispatch":
            payload["dispatch_id"] = migration["artifact_id"]
        elif migration["artifact_type"] == "rag-context-pack":
            payload["context_pack_id"] = migration["artifact_id"]
        elif migration["artifact_type"] == "rag-retrieval-result":
            payload["retrieval_id"] = migration["artifact_id"]
        else:
            payload["artifact_id"] = migration["artifact_id"]
        payload.setdefault("legacy_artifact_paths", [])
        if migration["old_rel"] not in payload["legacy_artifact_paths"]:
            payload["legacy_artifact_paths"].append(migration["old_rel"])
        write_json(migration["target"], payload)
        written.append({"source": migration["old_rel"], "target": migration["new_rel"]})
        if args.delete_source and migration["source"].exists() and migration["source"].resolve() != migration["target"].resolve():
            migration["source"].unlink()
            deleted.append(migration["old_rel"])

    updated_refs: list[str] = []
    for artifact_path in sorted(retrieval_dir.glob("*.json")):
        payload = read_json(artifact_path)
        updated = replace_refs(payload, path_map)
        if isinstance(payload.get("legacy_artifact_paths"), list):
            updated["legacy_artifact_paths"] = payload["legacy_artifact_paths"]
        if updated != payload:
            write_json(artifact_path, updated)
            updated_refs.append(relative_to_repo(repo_root, artifact_path))

    pruned: list[str] = []
    if args.prune_legacy_migrations:
        for artifact_path in sorted(retrieval_dir.glob("*.json")):
            if artifact_path.resolve() in desired_targets:
                continue
            payload = read_json(artifact_path)
            legacy_paths = payload.get("legacy_artifact_paths", [])
            if isinstance(legacy_paths, list) and any(
                isinstance(item, str)
                and is_retrieval_artifact_ref(item)
                and not UUID_JSON_RE.match(Path(item).name.lower())
                for item in legacy_paths
            ):
                rel_artifact = relative_to_repo(repo_root, artifact_path)
                artifact_path.unlink()
                pruned.append(rel_artifact)

    markdown_written: list[dict[str, str]] = []
    for markdown in sorted(path for path in retrieval_dir.glob("*.md") if path.name.lower() != "readme.md"):
        companion = companion_json_for_markdown(markdown)
        companion_was_migrated = companion is not None and relative_to_repo(repo_root, companion) in path_map
        if companion_was_migrated and args.delete_duplicate_markdown:
            rel_markdown = relative_to_repo(repo_root, markdown)
            markdown.unlink()
            deleted.append(rel_markdown)
            continue
        artifact = markdown_artifact(repo_root, markdown)
        target = retrieval_dir / f"{artifact['artifact_id']}.json"
        write_json(target, artifact)
        markdown_written.append({"source": artifact["source_path"], "target": relative_to_repo(repo_root, target)})
        if args.delete_source:
            rel_markdown = relative_to_repo(repo_root, markdown)
            markdown.unlink()
            deleted.append(rel_markdown)

    return {
        "retrieval_dir": relative_to_repo(repo_root, retrieval_dir),
        "json_migrated_count": len(written),
        "markdown_jsonized_count": len(markdown_written),
        "deleted_count": len(deleted),
        "updated_reference_count": len(updated_refs),
        "pruned_count": len(pruned),
        "written": written,
        "markdown_written": markdown_written,
        "updated_refs": updated_refs,
        "pruned": pruned,
        "deleted": deleted,
    }


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
