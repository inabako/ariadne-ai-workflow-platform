from __future__ import annotations

from services.interfaces import StartStopService


class AppLifecycle:
    def __init__(self, services: list[StartStopService] | None = None) -> None:
        self._services = services or []
        self.started = False

    def add(self, service: StartStopService) -> None:
        if self.started:
            raise RuntimeError("cannot add service after lifecycle start")
        self._services.append(service)

    def start(self) -> None:
        for service in self._services:
            service.start()
        self.started = True

    def stop(self) -> None:
        for service in reversed(self._services):
            service.stop()
        self.started = False
