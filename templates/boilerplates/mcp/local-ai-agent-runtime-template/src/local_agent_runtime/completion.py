from __future__ import annotations

from dataclasses import dataclass

from .jobs import Job, JobState
from .workflow import Workflow


@dataclass(frozen=True)
class CompletionResult:
    complete: bool
    reason: str
    missing_steps: list[str]
    missing_artifacts: list[str]


class CompletionEvaluator:
    def evaluate(self, job: Job, workflow: Workflow) -> CompletionResult:
        required_steps = [step.name for step in workflow.steps if step.required]
        missing_steps = [name for name in required_steps if name not in job.completed_steps]
        missing_artifacts = [artifact for artifact in workflow.required_artifacts if artifact not in job.artifacts]
        complete = not missing_steps and not missing_artifacts and job.state != JobState.WAITING_HUMAN
        if complete:
            return CompletionResult(True, "required steps and evidence are present", [], [])
        return CompletionResult(False, "completion criteria are not satisfied", missing_steps, missing_artifacts)

