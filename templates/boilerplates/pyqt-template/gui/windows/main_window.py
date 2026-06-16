from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gui.viewmodels.main_viewmodel import MainViewModel
from gui.widgets.connection_status_widget import ConnectionStatusWidget
from gui.widgets.control_panel import ControlPanelWidget
from gui.widgets.log_panel import LogPanelWidget
from gui.widgets.telemetry_widget import TelemetryWidget
from gui.widgets.video_widget import VideoWidget
from lifecycle.app_lifecycle import AppLifecycle


class MainWindow(QMainWindow):
    def __init__(self, viewmodel: MainViewModel, lifecycle: AppLifecycle) -> None:
        super().__init__()
        self.viewmodel = viewmodel
        self.lifecycle = lifecycle
        self.setWindowTitle("PyQt Template")

        self.control_panel = ControlPanelWidget()
        self.telemetry_widget = TelemetryWidget()
        self.video_widget = VideoWidget()
        self.connection_status = ConnectionStatusWidget()
        self.log_panel = LogPanelWidget()

        root = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.connection_status)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.telemetry_widget)
        layout.addWidget(self.control_panel)
        layout.addWidget(self.log_panel)
        root.setLayout(layout)
        self.setCentralWidget(root)

        self.control_panel.stop_button.clicked.connect(self._on_stop_clicked)
        self.control_panel.ping_button.clicked.connect(self._on_ping_clicked)
        self.refresh_view()

    def refresh_view(self) -> None:
        telemetry = self.viewmodel.telemetry()
        self.telemetry_widget.update_telemetry(telemetry)
        self.connection_status.set_connected(telemetry.connected)
        self.video_widget.set_frame_label(self.viewmodel.video_label())

    def _on_stop_clicked(self) -> None:
        self.viewmodel.stop_robot()
        self.log_panel.append("STOP command requested")

    def _on_ping_clicked(self) -> None:
        self.viewmodel.ping_robot()
        self.log_panel.append("PING command requested")
