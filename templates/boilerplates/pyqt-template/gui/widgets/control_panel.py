from __future__ import annotations

from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget


class ControlPanelWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.stop_button = QPushButton("STOP")
        self.ping_button = QPushButton("PING")
        layout = QHBoxLayout()
        layout.addWidget(self.stop_button)
        layout.addWidget(self.ping_button)
        self.setLayout(layout)
