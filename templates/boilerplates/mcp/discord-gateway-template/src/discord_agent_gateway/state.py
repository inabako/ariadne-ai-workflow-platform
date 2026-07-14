from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteGatewayStateStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("create table if not exists seen_events(event_id text primary key)")
            connection.execute(
                "create table if not exists message_refs(job_id text primary key, channel_id text not null, message_id text not null)"
            )

    def mark_event_seen(self, event_id: str) -> bool:
        with self._connect() as connection:
            try:
                connection.execute("insert into seen_events(event_id) values (?)", (event_id,))
                return True
            except sqlite3.IntegrityError:
                return False

    def save_message_reference(self, job_id: str, channel_id: str, message_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                insert into message_refs(job_id, channel_id, message_id)
                values (?, ?, ?)
                on conflict(job_id) do update set
                  channel_id=excluded.channel_id,
                  message_id=excluded.message_id
                """,
                (job_id, channel_id, message_id),
            )

    def get_message_reference(self, job_id: str) -> tuple[str, str] | None:
        with self._connect() as connection:
            row = connection.execute("select channel_id, message_id from message_refs where job_id = ?", (job_id,)).fetchone()
        return None if row is None else (row[0], row[1])

