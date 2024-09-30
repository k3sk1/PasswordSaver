from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PySide2.QtCore import Qt


class PlaceholderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #ffad8d;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        message_label = QLabel("Velkommen til Password Saver")
        message_label.setAlignment(Qt.AlignCenter)
        font = message_label.font()
        font.setPointSize(18)
        message_label.setFont(font)

        layout.addWidget(message_label)
        self.setLayout(layout)
