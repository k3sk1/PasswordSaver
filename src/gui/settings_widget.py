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
import styles


class SettingsWidget(QWidget):
    settings_changed = Signal(tuple)  # Signal for tema og font-størrelse
    settings_cancelled = Signal()

    def __init__(
        self,
        user,
        session,
        key,
        current_theme="default",
        current_font_size=12,
        parent=None,
    ):
        super().__init__(parent)

        self.user = user
        self.session = session
        self.key = key

        self.setWindowTitle("Innstillinger")
        self.setStyleSheet(
            "background-color: #f0f0f0;"
        )  # Valgfritt: Sett bakgrunnsfarge

        # Hovedlayout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Topp-sentrert
        main_layout.setContentsMargins(50, 30, 50, 30)  # Juster marger etter behov
        main_layout.setSpacing(20)  # Juster avstand mellom elementer

        # Layout for temavalg
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(10)
        theme_label = QLabel("Velg tema:")
        theme_label.setStyleSheet(styles.LABEL_STYLE)
        theme_combo = QComboBox()
        theme_combo.setStyleSheet(styles.LINE_EDIT_STYLE)
        theme_combo.addItems(["default", "vintage"])
        theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(theme_combo)

        # Layout for font-størrelse valg
        font_size_layout = QHBoxLayout()
        font_size_layout.setSpacing(10)
        font_size_label = QLabel("Velg font-størrelse:")
        font_size_label.setStyleSheet(styles.LABEL_STYLE)
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 48)
        font_size_spin.setValue(current_font_size)
        font_size_spin.setStyleSheet(styles.LINE_EDIT_STYLE)
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(font_size_spin)

        # Legg til innstillingslayouts i hovedlayouten
        main_layout.addLayout(theme_layout)
        main_layout.addLayout(font_size_layout)

        # Knapper (Lagre og Avbryt)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        buttons_layout.addStretch()

        save_button = QPushButton("Lagre")
        save_button.setStyleSheet(styles.BUTTON_STYLE)
        save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("Avbryt")
        cancel_button.setStyleSheet(styles.BUTTON_STYLE)
        cancel_button.clicked.connect(self.cancel_settings)

        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()

        # Legg til knappene i hovedlayouten
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Lagre referanser til widgets for senere bruk
        self.theme_combo = theme_combo
        self.font_size_spin = font_size_spin

    def save_settings(self):
        theme = self.theme_combo.currentText()
        font_size = self.font_size_spin.value()
        self.settings_changed.emit((theme, font_size))

    def cancel_settings(self):
        self.settings_cancelled.emit()
        self.close()
