from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide2.QtCore import Qt

import styles


class PlaceholderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #fcd4a0;")
        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Velkommen til Password Saver!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(styles.LABEL_STYLE)

        layout.addWidget(label)
