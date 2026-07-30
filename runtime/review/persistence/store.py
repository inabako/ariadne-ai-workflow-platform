from __future__ import annotations

from pathlib import Path
from typing import Any

from runtime.constants.runtime_values import SCHEMA_VERSION
from runtime.common import read_json, relative_to_repo, write_json
from runtime.constants.workspace import (
    context_dir_for_work_dir,
    process_report_dir_for_work_dir,
    resolve_work_dir,
)


REVIEW_DIR_NAME = "review-council"
INDEX_FILE_NAME = "index.json"


class ReviewStore:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def review_dir(self, work_id: str, work_dir: str | Path = "") -> Path:
        return context_dir_for_work_dir(resolve_work_dir(self.repo_root, work_id, work_dir)) / REVIEW_DIR_NAME

    def process_report_dir(self, work_id: str, work_dir: str | Path = "") -> Path:
        return process_report_dir_for_work_dir(resolve_work_dir(self.repo_root, work_id, work_dir))

    def session_path(self, work_id: str, review_id: str, work_dir: str | Path = "") -> Path:
        return self.review_dir(work_id, work_dir) / f"{review_id}.json"

    def index_path(self, work_id: str, work_dir: str | Path = "") -> Path:
        return self.review_dir(work_id, work_dir) / INDEX_FILE_NAME

    def save(self, session: dict[str, Any], work_dir: str | Path = "") -> dict[str, str]:
        work_id = str(session["work_id"])
        review_id = str(session["review_id"])
        session_path = self.session_path(work_id, review_id, work_dir)
        write_json(session_path, session)
        index = read_json(self.index_path(work_id, work_dir), default={})
        if not isinstance(index, dict):
            index = {}
        sessions = [item for item in index.get("sessions", []) if item.get("review_id") != review_id]
        sessions.append(
            {
                "review_id": review_id,
                "work_id": work_id,
                "status": session.get("status", ""),
                "updated_at": session.get("updated_at", ""),
                "path": relative_to_repo(self.repo_root, session_path),
            }
        )
        index.update(
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_type": "review-council-index",
                "work_id": work_id,
                "latest_review_id": review_id,
                "sessions": sessions,
            }
        )
        write_json(self.index_path(work_id, work_dir), index)
        return {
            "session": relative_to_repo(self.repo_root, session_path),
            "index": relative_to_repo(self.repo_root, self.index_path(work_id, work_dir)),
        }

    def load(self, *, review_id: str = "", work_id: str = "", work_dir: str | Path = "") -> dict[str, Any]:
        if review_id and work_id:
            path = self.session_path(work_id, review_id, work_dir)
            data = read_json(path)
            if not isinstance(data, dict):
                raise FileNotFoundError(f"Review session does not exist: {path}")
            return data
        if work_id:
            index = read_json(self.index_path(work_id, work_dir), default={})
            if not isinstance(index, dict) or not index.get("latest_review_id"):
                raise FileNotFoundError(f"Review session index does not exist for work_id: {work_id}")
            return self.load(review_id=str(index["latest_review_id"]), work_id=work_id, work_dir=work_dir)
        if review_id:
            matches = list((self.repo_root / "work").glob(f"**/{REVIEW_DIR_NAME}/{review_id}.json"))
            if len(matches) != 1:
                raise FileNotFoundError(f"Review session does not resolve uniquely: {review_id}")
            data = read_json(matches[0])
            if not isinstance(data, dict):
                raise FileNotFoundError(f"Review session does not exist: {matches[0]}")
            return data
        raise ValueError("--review-id or --work-id is required.")
