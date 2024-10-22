from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide2.QtCore import Qt


class PlaceholderWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Velkommen til Passordskapet!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold;")

        layout.addWidget(label)
