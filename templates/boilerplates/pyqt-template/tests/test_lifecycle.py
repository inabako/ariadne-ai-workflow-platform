from __future__ import annotations

from lifecycle.app_lifecycle import AppLifecycle


class FakeService:
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def start(self) -> None:
        self.calls.append(f"start:{self.name}")

    def stop(self) -> None:
        self.calls.append(f"stop:{self.name}")


def test_lifecycle_starts_and_stops_in_order() -> None:
    calls: list[str] = []
    lifecycle = AppLifecycle([FakeService("a", calls), FakeService("b", calls)])
    lifecycle.start()
    lifecycle.stop()
    assert calls == ["start:a", "start:b", "stop:b", "stop:a"]
