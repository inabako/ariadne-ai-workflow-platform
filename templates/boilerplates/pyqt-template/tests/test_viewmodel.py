from __future__ import annotations

from gui.viewmodels.main_viewmodel import MainViewModel
from mocks.mock_robot_controller import MockRobotController
from mocks.mock_telemetry_service import MockTelemetryService
from mocks.mock_video_service import MockVideoService


def test_viewmodel_sends_stop_to_injected_mock() -> None:
    robot = MockRobotController()
    viewmodel = MainViewModel(robot, MockTelemetryService(), MockVideoService())
    viewmodel.stop_robot()
    assert robot.commands == [("STOP", {})]
    assert viewmodel.last_status == "stop sent"
