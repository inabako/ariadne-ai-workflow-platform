from __future__ import annotations

from PyQt6.QtWidgets import QListWidget, QVBoxLayout, QWidget


class LogPanelWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.items = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.items)
        self.setLayout(layout)

    def append(self, text: str) -> None:
        self.items.addItem(text)
