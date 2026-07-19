from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ConnectionStatusWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.status_label = QLabel("Disconnected")
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def set_connected(self, connected: bool) -> None:
        self.status_label.setText("Connected" if connected else "Disconnected")
