from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class WorkerLease:
    worker_id: str
    job_id: str
    expires_at: datetime

    def expired(self, now: datetime | None = None) -> bool:
        return (now or datetime.now(timezone.utc)) >= self.expires_at


class WorkerLeaseManager:
    def __init__(self, lease_seconds: int = 120) -> None:
        self.lease_seconds = lease_seconds
        self._leases: dict[str, WorkerLease] = {}

    def acquire(self, worker_id: str, job_id: str) -> WorkerLease:
        lease = WorkerLease(
            worker_id=worker_id,
            job_id=job_id,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.lease_seconds),
        )
        self._leases[job_id] = lease
        return lease

    def heartbeat(self, job_id: str) -> WorkerLease:
        lease = self._leases[job_id]
        lease.expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.lease_seconds)
        return lease

