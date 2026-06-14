from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from models.telemetry import Telemetry


class TelemetryWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.battery_label = QLabel("Battery: --")
        self.signal_label = QLabel("Signal: --")
        layout = QVBoxLayout()
        layout.addWidget(self.battery_label)
        layout.addWidget(self.signal_label)
        self.setLayout(layout)

    def update_telemetry(self, telemetry: Telemetry) -> None:
        self.battery_label.setText(f"Battery: {telemetry.battery_percent:.0f}%")
        self.signal_label.setText(f"Signal: {telemetry.signal_quality:.2f}")
