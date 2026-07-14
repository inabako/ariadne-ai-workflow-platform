from __future__ import annotations

import os

import pytest

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QApplication

from gui.viewmodels.main_viewmodel import MainViewModel
from gui.windows.main_window import MainWindow
from lifecycle.app_lifecycle import AppLifecycle
from mocks.mock_robot_controller import MockRobotController
from mocks.mock_telemetry_service import MockTelemetryService
from mocks.mock_video_service import MockVideoService


def test_main_window_smoke_does_not_start_external_io() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    robot = MockRobotController()
    telemetry = MockTelemetryService()
    video = MockVideoService()
    lifecycle = AppLifecycle([robot, telemetry, video])
    viewmodel = MainViewModel(robot, telemetry, video)

    window = MainWindow(viewmodel=viewmodel, lifecycle=lifecycle)
    assert window.windowTitle() == "PyQt Template"
    assert not lifecycle.started
    assert not robot.started
    assert not telemetry.started
    assert not video.started
    window.close()
    app.processEvents()
