from __future__ import annotations

import json
from pathlib import Path

from .completion import CompletionResult
from .jobs import Job


class EvidenceWriter:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_completion_evidence(self, job: Job, result: CompletionResult) -> Path:
        path = self.root / f"{job.job_id}-completion.json"
        payload = {
            "job_id": job.job_id,
            "state": job.state.value,
            "complete": result.complete,
            "reason": result.reason,
            "missing_steps": result.missing_steps,
            "missing_artifacts": result.missing_artifacts,
            "artifacts": job.artifacts,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

