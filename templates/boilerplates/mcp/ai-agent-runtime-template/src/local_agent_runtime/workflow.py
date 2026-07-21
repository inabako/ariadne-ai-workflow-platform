from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .jobs import Job, JobState


@dataclass(frozen=True)
class WorkflowStep:
    name: str
    action: str
    required: bool = True
    requires_human_check: bool = False
    produces_artifact: str | None = None


@dataclass(frozen=True)
class Workflow:
    name: str
    steps: list[WorkflowStep]
    required_artifacts: list[str] = field(default_factory=list)


class StepRunner(Protocol):
    def run_step(self, job: Job, step: WorkflowStep) -> str:
        ...


class DefaultStepRunner:
    def run_step(self, job: Job, step: WorkflowStep) -> str:
        return f"step {step.name} executed for {job.job_id}"


class WorkflowEngine:
    def __init__(self, step_runner: StepRunner | None = None) -> None:
        self.step_runner = step_runner or DefaultStepRunner()

    def run_until_blocked_or_complete(self, job: Job, workflow: Workflow) -> Job:
        job.state = JobState.RUNNING
        for step in workflow.steps:
            if step.name in job.completed_steps:
                continue
            if step.requires_human_check:
                job.state = JobState.WAITING_HUMAN
                job.human_check_request = {
                    "step": step.name,
                    "question": "Approve this step before continuing?",
                    "reason": "Human check is required by workflow policy.",
                }
                job.events.append(f"human_check:{step.name}")
                return job
            observation = self.step_runner.run_step(job, step)
            job.events.append(observation)
            job.completed_steps.append(step.name)
            if step.produces_artifact:
                job.artifacts.append(step.produces_artifact)
        return job

