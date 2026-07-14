from __future__ import annotations

from lifecycle.app_lifecycle import AppLifecycle
from mocks.mock_robot_controller import MockRobotController
from mocks.mock_telemetry_service import MockTelemetryService
from mocks.mock_video_service import MockVideoService


def test_mock_services_are_start_stop_compatible() -> None:
    robot = MockRobotController()
    telemetry = MockTelemetryService()
    video = MockVideoService()
    lifecycle = AppLifecycle([robot, telemetry, video])
    lifecycle.start()
    assert robot.started
    assert telemetry.started
    assert video.started
    lifecycle.stop()
    assert not robot.started
    assert not telemetry.started
    assert not video.started
