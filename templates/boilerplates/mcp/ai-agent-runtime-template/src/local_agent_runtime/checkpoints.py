from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from .contracts import SCHEMA_VERSION, utc_timestamp
from .jobs import Job


class CheckpointStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, job: Job) -> Path:
        path = self.root / f"{job.job_id}.json"
        payload = {
            "schema_version": SCHEMA_VERSION,
            "checkpoint_id": f"checkpoint-{uuid4().hex[:12]}",
            "job_id": job.job_id,
            "trace_id": job.trace_id,
            "goal": job.goal,
            "workflow_name": job.workflow_name,
            "workflow_id": job.job_id,
            "state": job.state.value,
            "completed_steps": job.completed_steps,
            "artifacts": job.artifacts,
            "framework_metadata": {},
            "events": job.events,
            "human_check_request": job.human_check_request,
            "saved_at": utc_timestamp(),
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

