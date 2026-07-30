from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .contracts import generate_trace_id
from .jobs import Job, JobState


class SQLiteJobStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                create table if not exists jobs (
                  job_id text primary key,
                  trace_id text not null,
                  goal text not null,
                  workflow_name text not null,
                  state text not null,
                  payload text not null
                )
                """
            )
            columns = {row[1] for row in connection.execute("pragma table_info(jobs)").fetchall()}
            if "trace_id" not in columns:
                connection.execute("alter table jobs add column trace_id text not null default ''")
            rows = connection.execute("select job_id from jobs where trace_id = ''").fetchall()
            for (job_id,) in rows:
                connection.execute("update jobs set trace_id = ? where job_id = ?", (generate_trace_id(), job_id))

    def save(self, job: Job) -> None:
        payload = json.dumps(
            {
                "completed_steps": job.completed_steps,
                "artifacts": job.artifacts,
                "events": job.events,
                "human_check_request": job.human_check_request,
                "model_claimed_done": job.model_claimed_done,
            },
            ensure_ascii=False,
        )
        with self._connect() as connection:
            connection.execute(
                """
                insert into jobs(job_id, trace_id, goal, workflow_name, state, payload)
                values (?, ?, ?, ?, ?, ?)
                on conflict(job_id) do update set
                  trace_id=excluded.trace_id,
                  goal=excluded.goal,
                  workflow_name=excluded.workflow_name,
                  state=excluded.state,
                  payload=excluded.payload
                """,
                (job.job_id, job.trace_id, job.goal, job.workflow_name, job.state.value, payload),
            )

    def load(self, job_id: str) -> Job:
        with self._connect() as connection:
            row = connection.execute(
                "select trace_id, goal, workflow_name, state, payload from jobs where job_id = ?",
                (job_id,),
            ).fetchone()
        if row is None:
            raise KeyError(job_id)
        trace_id, goal, workflow_name, state, payload_text = row
        payload = json.loads(payload_text)
        return Job(
            goal=goal,
            workflow_name=workflow_name,
            job_id=job_id,
            trace_id=trace_id,
            state=JobState(state),
            completed_steps=list(payload["completed_steps"]),
            artifacts=list(payload["artifacts"]),
            events=list(payload["events"]),
            human_check_request=payload["human_check_request"],
            model_claimed_done=bool(payload["model_claimed_done"]),
        )

