from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from runtime.common import find_repo_root, read_json, relative_to_repo, utc_now_iso, write_json  # noqa: E402


MANIFEST_FILE_NAME = "context-manifest.json"
DISPATCHER_CONTEXT_TYPES = {
    "environment-selection",
    "workflow-selection",
    "tool-selection",
    "runtime-context",
    "execution-plan",
}


def context_dir_for_work_dir(work_dir: Path) -> Path:
    return work_dir / "context"


def manifest_path_for_work_dir(work_dir: Path) -> Path:
    return context_dir_for_work_dir(work_dir) / MANIFEST_FILE_NAME


def default_manifest(work_id: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "artifact_type": "context-manifest",
        "architecture": "context-first",
        "adoption_phase": "phase-1",
        "work_id": work_id,
        "updated_at": utc_now_iso(),
        "contexts": [],
        "rules": {
            "dispatcher_contexts_are_authoritative": True,
            "workflows_may_update_execution_contexts": True,
            "missing_required_dispatcher_context_requires_human_check": True,
        },
    }


def load_manifest(work_dir: Path, work_id: str = "") -> dict[str, Any]:
    path = manifest_path_for_work_dir(work_dir)
    data = read_json(path, default=None)
    if isinstance(data, dict):
        data.setdefault("schema_version", "1.0")
        data.setdefault("artifact_type", "context-manifest")
        data.setdefault("architecture", "context-first")
        data.setdefault("adoption_phase", "phase-1")
        data.setdefault("work_id", work_id or work_dir.name)
        data.setdefault("updated_at", utc_now_iso())
        data.setdefault("contexts", [])
        data.setdefault(
            "rules",
            {
                "dispatcher_contexts_are_authoritative": True,
                "workflows_may_update_execution_contexts": True,
                "missing_required_dispatcher_context_requires_human_check": True,
            },
        )
        return data
    return default_manifest(work_id or work_dir.name)


def upsert_context(manifest: dict[str, Any], context_entry: dict[str, Any]) -> None:
    contexts = manifest.setdefault("contexts", [])
    context_type = context_entry["type"]
    for index, existing in enumerate(contexts):
        if existing.get("type") == context_type:
            contexts[index] = {**existing, **context_entry}
            return
    contexts.append(context_entry)


def register_context(
    repo_root: Path,
    work_dir: Path,
    *,
    work_id: str,
    context_type: str,
    path: Path,
    required: bool,
    generated_by: str,
    owner: str,
    schema: str,
    status: str = "available",
) -> dict[str, Any]:
    manifest = load_manifest(work_dir, work_id=work_id)
    relative_path = relative_to_repo(repo_root, path)
    upsert_context(
        manifest,
        {
            "type": context_type,
            "path": relative_path,
            "required": required,
            "generated_by": generated_by,
            "owner": owner,
            "schema": schema,
            "status": status,
            "updated_at": utc_now_iso(),
        },
    )
    manifest["updated_at"] = utc_now_iso()
    write_json(manifest_path_for_work_dir(work_dir), manifest)
    return manifest


def dispatcher_context_status(manifest: dict[str, Any], required_types: list[str]) -> dict[str, Any]:
    contexts = {item.get("type"): item for item in manifest.get("contexts", []) if isinstance(item, dict)}
    missing = [context_type for context_type in required_types if context_type not in contexts]
    return {
        "status": "ready" if not missing else "human-check-required",
        "missing": missing,
        "available": sorted(contexts),
        "human_check_required": bool(missing),
        "human_check_reason": "必須Dispatcher Contextが不足しています。" if missing else "",
    }


def context_entry(manifest: dict[str, Any], context_type: str) -> dict[str, Any] | None:
    for item in manifest.get("contexts", []):
        if isinstance(item, dict) and item.get("type") == context_type:
            return item
    return None


def context_path(repo_root: Path, entry: dict[str, Any]) -> Path:
    raw_path = Path(str(entry.get("path", "")))
    return raw_path if raw_path.is_absolute() else repo_root / raw_path


def require_environment_selection(
    repo_root: Path,
    work_dir: Path,
    *,
    expected_environment: str,
) -> dict[str, Any]:
    manifest = load_manifest(work_dir)
    status = dispatcher_context_status(manifest, ["environment-selection"])
    if status["human_check_required"]:
        raise RuntimeError(
            "Context First gate: environment-selection context is required. "
            f"Run `aiwfctl env select {expected_environment} --work-id {work_dir.name}` first."
        )

    entry = context_entry(manifest, "environment-selection")
    if entry is None:
        raise RuntimeError("Context First gate: environment-selection context entry was not found.")
    selection_path = context_path(repo_root, entry)
    selection = read_json(selection_path, default=None)
    if not isinstance(selection, dict):
        raise RuntimeError(f"Context First gate: invalid environment-selection context: {selection_path}")
    actual_environment = selection.get("environment")
    if actual_environment != expected_environment:
        raise RuntimeError(
            "Context First gate: environment mismatch. "
            f"expected={expected_environment}, actual={actual_environment or '(missing)'}."
        )
    return {
        "status": "ready",
        "environment": actual_environment,
        "context_path": relative_to_repo(repo_root, selection_path),
        "manifest_path": relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect Context First manifest.")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--work-dir", required=True)
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show")
    show.set_defaults(handler=run_show)

    require = sub.add_parser("require")
    require.add_argument("--context", action="append", required=True, choices=sorted(DISPATCHER_CONTEXT_TYPES))
    require.set_defaults(handler=run_require)

    require_environment = sub.add_parser("require-environment")
    require_environment.add_argument("--environment", required=True)
    require_environment.set_defaults(handler=run_require_environment)
    return parser


def resolve_work_dir(args: argparse.Namespace) -> tuple[Path, Path]:
    repo_root = Path(args.repo_root).resolve() if args.repo_root else find_repo_root()
    raw = Path(args.work_dir)
    work_dir = raw if raw.is_absolute() else repo_root / raw
    return repo_root, work_dir


def run_show(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, work_dir = resolve_work_dir(args)
    manifest = load_manifest(work_dir)
    return {
        "status": "ok" if manifest_path_for_work_dir(work_dir).exists() else "missing",
        "manifest_path": relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir)),
        "manifest": manifest,
    }


def run_require(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, work_dir = resolve_work_dir(args)
    manifest = load_manifest(work_dir)
    status = dispatcher_context_status(manifest, list(args.context))
    return {
        **status,
        "manifest_path": relative_to_repo(repo_root, manifest_path_for_work_dir(work_dir)),
    }


def run_require_environment(args: argparse.Namespace) -> dict[str, Any]:
    repo_root, work_dir = resolve_work_dir(args)
    return require_environment_selection(
        repo_root,
        work_dir,
        expected_environment=args.environment,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.handler(args)
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") not in {"human-check-required", "failed"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
