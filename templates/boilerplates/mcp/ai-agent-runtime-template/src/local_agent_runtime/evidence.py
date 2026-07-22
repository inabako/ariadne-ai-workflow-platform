from __future__ import annotations

import json
from pathlib import Path

from .completion import CompletionResult
from .contracts import EvidenceRecord
from .jobs import Job


class EvidenceWriter:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def write_completion_evidence(self, job: Job, result: CompletionResult) -> Path:
        path = self.root / f"{job.job_id}-completion.json"
        evidence = EvidenceRecord(
            evidence_id=f"{job.job_id}-completion",
            workflow_id=job.job_id,
            trace_id=job.trace_id,
            source="completion-evaluator",
            type="completion",
            path=str(path),
        ).to_contract()
        payload = {
            "schema_version": "1.0",
            "job_id": job.job_id,
            "trace_id": job.trace_id,
            "state": job.state.value,
            "complete": result.complete,
            "reason": result.reason,
            "missing_steps": result.missing_steps,
            "missing_artifacts": result.missing_artifacts,
            "artifacts": job.artifacts,
            "evidence": evidence,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

