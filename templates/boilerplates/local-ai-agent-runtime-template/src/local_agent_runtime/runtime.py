from __future__ import annotations

from pathlib import Path

from .artifacts import ArtifactRegistry
from .checkpoints import CheckpointStore
from .completion import CompletionEvaluator, CompletionResult
from .evidence import EvidenceWriter
from .jobs import Job, JobManager, JobState
from .notifications import EventBus
from .storage import SQLiteJobStore
from .workflow import Workflow, WorkflowEngine


class AgentRuntime:
    def __init__(self, checkpoint_root: Path) -> None:
        self.jobs = JobManager()
        self.engine = WorkflowEngine()
        self.completion = CompletionEvaluator()
        self.checkpoints = CheckpointStore(checkpoint_root)
        self.evidence = EvidenceWriter(checkpoint_root.parent / "evidence")
        self.artifacts = ArtifactRegistry()
        self.events = EventBus()
        self.job_store = SQLiteJobStore(checkpoint_root.parent / "runtime.db")

    def submit_and_run(self, goal: str, workflow: Workflow) -> tuple[Job, CompletionResult]:
        job = self.jobs.submit(goal, workflow.name)
        self.engine.run_until_blocked_or_complete(job, workflow)
        result = self.completion.evaluate(job, workflow)
        if result.complete:
            self.jobs.update_state(job, JobState.COMPLETED)
        for artifact in job.artifacts:
            self.artifacts.register(job.job_id, artifact)
        self.checkpoints.save(job)
        self.job_store.save(job)
        evidence_path = self.evidence.write_completion_evidence(job, result)
        self.events.publish("job.finished", {"job_id": job.job_id, "complete": result.complete, "evidence": str(evidence_path)})
        return job, result
