from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator


@contextmanager
def duration_timer() -> Iterator[dict[str, int]]:
    state = {"duration_ms": 0}
    started = perf_counter()
    try:
        yield state
    finally:
        state["duration_ms"] = max(int((perf_counter() - started) * 1000), 0)
