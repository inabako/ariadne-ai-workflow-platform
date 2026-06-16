from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication

from config.settings import Settings
from gui.viewmodels.main_viewmodel import MainViewModel
from gui.windows.main_window import MainWindow
from lifecycle.app_lifecycle import AppLifecycle
from logger.app_logger import configure_logging
from mocks.mock_robot_controller import MockRobotController
from mocks.mock_telemetry_service import MockTelemetryService
from mocks.mock_video_service import MockVideoService


def main() -> int:
    settings = Settings.from_env()
    configure_logging(settings.log_level)

    qt_app = QApplication(sys.argv)
    lifecycle = AppLifecycle()
    viewmodel = MainViewModel(
        robot_controller=MockRobotController(),
        telemetry_service=MockTelemetryService(),
        video_service=MockVideoService(),
    )
    window = MainWindow(viewmodel=viewmodel, lifecycle=lifecycle)
    window.show()

    lifecycle.start()
    exit_code = qt_app.exec()
    lifecycle.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
