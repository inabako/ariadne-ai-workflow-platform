from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any

from runtime.common import load_artifact_index, read_json, relative_to_repo, upsert_artifact, utc_now_iso, write_json
from runtime.constants.workspace import context_file


APPROVED_KNOWLEDGE_STATUSES = {"approved", "published", "verified", "ready"}


def cleanup_scope_for_work_id(work_id: str) -> tuple[str, bool]:
    parts = Path(work_id).parts
    if len(parts) >= 3 and parts[0] == "github":
        return "/".join(parts[:2]), True
    return work_id, False


def check_command(work_id: str) -> str:
    cleanup_work_id, recursive = cleanup_scope_for_work_id(work_id)
    command = f"aiwfctl work cleanup-check --work-id {shlex.quote(cleanup_work_id)}"
    return command + (" --recursive" if recursive else "")


def apply_command(work_id: str) -> str:
    cleanup_work_id, recursive = cleanup_scope_for_work_id(work_id)
    command = f"aiwfctl work cleanup-apply --work-id {shlex.quote(cleanup_work_id)}"
    if recursive:
        command += " --recursive"
    return command + " --human-check approved"


def artifact_index_evidence(repo_root: Path, work_dir: Path) -> list[str]:
    index = read_json(context_file(work_dir, "artifact-index.json"), default={}) or {}
    evidence: list[str] = []
    for item in index.get("artifacts", []) or []:
        if not isinstance(item, dict):
            continue
        if item.get("cleanup_ready", True) is False:
            continue
        artifact_path = str(item.get("path", "")).strip()
        if artifact_path.startswith("work/db/") and (repo_root / artifact_path).exists():
            evidence.append(artifact_path)
    return sorted(set(evidence))


def record(repo_root: Path, work_dir: Path, work_id: str) -> dict[str, Any]:
    evidence = artifact_index_evidence(repo_root, work_dir)
    return {
        "ready_for_check": bool(evidence),
        "absorption_evidence": evidence,
        "check_command": check_command(work_id),
        "apply_command": apply_command(work_id) if evidence else "",
    }


def next_action(record: dict[str, Any], *, reason: str) -> dict[str, Any]:
    if not record.get("ready_for_check"):
        return {}
    return {
        "state": "knowledge-absorbed-cleanup-check-ready",
        "action": "check-work-cleanup",
        "reason": reason,
        "command": record.get("check_command", ""),
        "cleanup_command": record.get("apply_command", ""),
        "absorption_evidence": record.get("absorption_evidence", []),
    }


def register_long_lived_artifact(
    repo_root: Path,
    work_dir: Path,
    *,
    work_id: str,
    workflow_name: str,
    artifact_id: str,
    title: str,
    path: Path,
    artifact_type: str,
    status: str,
    owner_agent: str,
    summary: str = "",
) -> dict[str, Any]:
    index = load_artifact_index(work_dir, work_id, workflow_name)
    now = utc_now_iso()
    upsert_artifact(
        index,
        {
            "id": artifact_id,
            "title": title,
            "path": relative_to_repo(repo_root, path),
            "type": artifact_type,
            "status": status,
            "owner_agent": owner_agent,
            "created_at": now,
            "updated_at": now,
            "depends_on": [],
            "consumed_by": ["rag-build", "knowledge-retrieval"],
            "summary": summary or title,
            "cleanup_ready": status in APPROVED_KNOWLEDGE_STATUSES,
            "unresolved_items": [],
        },
    )
    write_json(context_file(work_dir, "artifact-index.json"), index)
    return index
