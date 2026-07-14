# Worker Lease

Worker leases keep long-running jobs tied to a worker for a bounded time. Heartbeats extend the lease while the worker is healthy.

Do not resume an expired lease without checking checkpoint state and mutation safety.

