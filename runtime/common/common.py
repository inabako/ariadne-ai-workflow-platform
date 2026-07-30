from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.constants.workspace import (
    CONTEXT_DIR_NAME,
    DESIGN_DOCUMENT_DIR_NAME,
    PROCESS_REPORT_DIR_NAME,
    SOURCE_DIR_NAME,
    TEST_EVIDENCE_DIR_NAME,
    context_file,
    work_dir_for_id,
)

WORK_DIRECTORIES = [
    DESIGN_DOCUMENT_DIR_NAME,
    PROCESS_REPORT_DIR_NAME,
    TEST_EVIDENCE_DIR_NAME,
    "test-specifications",
    SOURCE_DIR_NAME,
    CONTEXT_DIR_NAME,
]


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path(__file__)).resolve()
    for path in [current, *current.parents]:
        if (path / ".git").exists() and (path / "work").exists():
            return path
    return Path(__file__).resolve().parents[2]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def local_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return slug or "workflow"


def make_receipt_id(prefix: str = "WF") -> str:
    return f"{slugify(prefix).upper()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def ensure_work_tree(repo_root: Path, receipt_id: str) -> Path:
    work_dir = work_dir_for_id(repo_root, receipt_id)
    for name in WORK_DIRECTORIES:
        (work_dir / name).mkdir(parents=True, exist_ok=True)
    return work_dir


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def relative_to_repo(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def load_artifact_index(work_dir: Path, project_name: str, workflow_name: str) -> dict[str, Any]:
    path = context_file(work_dir, "artifact-index.json")
    data = read_json(path)
    if isinstance(data, dict):
        data.setdefault("schema_version", SCHEMA_VERSION)
        data.setdefault("project", project_name)
        data.setdefault("workflow", workflow_name)
        data.setdefault("artifacts", [])
        return data
    return {
        "schema_version": SCHEMA_VERSION,
        "project": project_name,
        "workflow": workflow_name,
        "artifacts": [],
    }


def upsert_artifact(index: dict[str, Any], artifact: dict[str, Any]) -> None:
    artifacts = index.setdefault("artifacts", [])
    artifact_id = artifact["id"]
    for idx, existing in enumerate(artifacts):
        if existing.get("id") == artifact_id:
            artifacts[idx] = {**existing, **artifact}
            return
    artifacts.append(artifact)


def write_markdown_bom(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8-sig")


def write_markdown(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
