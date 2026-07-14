from __future__ import annotations

from dataclasses import dataclass

from .jobs import Job, JobState


@dataclass(frozen=True)
class CommandResult:
    status: str
    job_id: str
    message: str = ""


class CommandAPI:
    def pause(self, job: Job) -> CommandResult:
        if job.state == JobState.RUNNING:
            job.state = JobState.WAITING_HUMAN
            job.events.append("paused")
        return CommandResult("ok", job.job_id, "pause requested")

    def resume(self, job: Job) -> CommandResult:
        if job.state == JobState.WAITING_HUMAN:
            job.state = JobState.ACCEPTED
            job.human_check_request = None
            job.events.append("resumed")
        return CommandResult("ok", job.job_id, "resume requested")

    def cancel(self, job: Job) -> CommandResult:
        job.state = JobState.CANCELLED
        job.events.append("cancelled")
        return CommandResult("ok", job.job_id, "cancelled")

