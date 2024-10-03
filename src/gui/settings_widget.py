from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide2.QtGui import QFontDatabase
from PySide2.QtCore import Signal, Qt


class SettingsWidget(QWidget):
    # Definer en signal som emitteres når innstillinger endres
    settings_changed = Signal(tuple)  # Signal med (font_family, font_size)
    settings_cancelled = Signal()  # Signal for avbryt

    def __init__(self, current_font_family, current_font_size, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Innstillinger")

        # Font familie
        font_label = QLabel("Font familie:")
        self.font_combo = QComboBox()
        self.font_combo.addItems(QFontDatabase().families())
        self.font_combo.setCurrentText(current_font_family)
        self.font_combo.setMaximumWidth(300)

        # Font størrelse
        size_label = QLabel("Font størrelse:")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(current_font_size)
        self.size_spin.setMaximumWidth(60)

        # ok og Avbryt knapper
        apply_button = QPushButton("Ok")
        cancel_button = QPushButton("Avbryt")

        apply_button.clicked.connect(self.accept_settings)
        cancel_button.clicked.connect(self.reject_settings)

        # Layout
        font_layout = QHBoxLayout()
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_combo)

        size_layout = QHBoxLayout()
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(font_layout)
        main_layout.addLayout(size_layout)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def accept_settings(self):
        font_family = self.font_combo.currentText()
        font_size = self.size_spin.value()
        self.settings_changed.emit((font_family, font_size))
        # Emit signal og la MainWindow håndtere byttet tilbake

    def reject_settings(self):
        self.settings_cancelled.emit()
        # Emit signal og la MainWindow håndtere byttet tilbake
