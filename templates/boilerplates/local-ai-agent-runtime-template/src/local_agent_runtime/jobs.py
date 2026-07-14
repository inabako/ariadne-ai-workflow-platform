from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class JobState(StrEnum):
    ACCEPTED = "accepted"
    RUNNING = "running"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Job:
    goal: str
    workflow_name: str
    job_id: str = field(default_factory=lambda: f"job-{uuid4().hex[:12]}")
    state: JobState = JobState.ACCEPTED
    completed_steps: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)
    human_check_request: dict[str, str] | None = None
    model_claimed_done: bool = False


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def submit(self, goal: str, workflow_name: str) -> Job:
        job = Job(goal=goal, workflow_name=workflow_name)
        job.events.append("accepted")
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> Job:
        return self._jobs[job_id]

    def update_state(self, job: Job, state: JobState) -> None:
        job.state = state
        job.events.append(state.value)

