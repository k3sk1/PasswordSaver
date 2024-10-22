from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
    QHBoxLayout,
)
from PySide2.QtCore import Signal, Qt


class SettingsWidget(QWidget):
    settings_changed = Signal(tuple)  # Signal for tema og font-størrelse
    settings_cancelled = Signal()

    def __init__(
        self,
        main_window,
        current_theme="default",
        current_font_size=16,
        parent=None,
    ):
        super().__init__(parent)

        self.main_window = main_window

        self.setWindowTitle("Innstillinger")

        # Hovedlayout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Topp-sentrert
        main_layout.setContentsMargins(50, 30, 50, 30)  # Juster marger etter behov
        main_layout.setSpacing(20)  # Juster avstand mellom elementer

        # Layout for temavalg
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(10)
        self.theme_label = QLabel("Velg tema")
        self.theme_combo = QComboBox()
        # theme_combo.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.theme_combo.addItems(["default", "vintage"])
        self.theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_combo)

        # Layout for font-størrelse valg
        font_size_layout = QHBoxLayout()
        font_size_layout.setSpacing(10)
        self.font_size_label = QLabel("Velg font-størrelse")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 48)
        self.font_size_spin.setValue(current_font_size)
        font_size_layout.addWidget(self.font_size_label)
        font_size_layout.addWidget(self.font_size_spin)

        # Legg til innstillingslayouts i hovedlayouten
        main_layout.addLayout(theme_layout)
        main_layout.addLayout(font_size_layout)

        # Knapper (Lagre og Avbryt)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.addStretch()

        self.save_button = QPushButton("Lagre")
        self.cancel_button = QPushButton("Avbryt")

        self.main_window.theme_changed.connect(self.init_ui_settings)
        self.init_ui_settings()

        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.cancel_settings)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()

        # Legg til knappene i hovedlayouten
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def init_ui_settings(self):
        self.main_window.style_manager.apply_label_style(self.theme_label)
        self.main_window.style_manager.apply_label_style(self.font_size_label)
        self.main_window.style_manager.apply_line_edit_style(self.theme_combo)
        self.main_window.style_manager.apply_line_edit_style(self.font_size_spin)
        self.main_window.style_manager.apply_button_style_1(self.save_button)
        self.main_window.style_manager.apply_button_style_2(self.cancel_button)

    def save_settings(self):
        theme = self.theme_combo.currentText()
        font_size = self.font_size_spin.value()
        self.init_ui_settings()
        self.settings_changed.emit((theme, font_size))

    def cancel_settings(self):
        self.settings_cancelled.emit()
        self.close()
