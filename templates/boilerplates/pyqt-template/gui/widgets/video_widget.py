from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class VideoWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.frame_label = QLabel("video not started")
        layout = QVBoxLayout()
        layout.addWidget(self.frame_label)
        self.setLayout(layout)

    def set_frame_label(self, text: str) -> None:
        self.frame_label.setText(text)
