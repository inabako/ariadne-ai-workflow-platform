from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter
from typing import Iterator

from runtime.constants.runtime_values import MILLISECONDS_PER_SECOND, NON_NEGATIVE_INT_DEFAULT


@contextmanager
def duration_timer() -> Iterator[dict[str, int]]:
    state = {"duration_ms": NON_NEGATIVE_INT_DEFAULT}
    started = perf_counter()
    try:
        yield state
    finally:
        state["duration_ms"] = max(int((perf_counter() - started) * MILLISECONDS_PER_SECOND), NON_NEGATIVE_INT_DEFAULT)
