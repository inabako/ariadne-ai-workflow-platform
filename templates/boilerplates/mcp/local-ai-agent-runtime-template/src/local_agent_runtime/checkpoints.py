from __future__ import annotations

import json
from pathlib import Path

from .jobs import Job


class CheckpointStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, job: Job) -> Path:
        path = self.root / f"{job.job_id}.json"
        payload = {
            "job_id": job.job_id,
            "goal": job.goal,
            "workflow_name": job.workflow_name,
            "state": job.state.value,
            "completed_steps": job.completed_steps,
            "artifacts": job.artifacts,
            "events": job.events,
            "human_check_request": job.human_check_request,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

