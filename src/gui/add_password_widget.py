# gui/add_password_widget.py

from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QMessageBox,
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont
import styles


class AddPasswordWidget(QWidget):
    # Definer en signal som emitteres når passordet er lagret
    password_saved = Signal(dict)

    def __init__(self, user, session, key, parent=None):
        super().__init__(parent)

        self.user = user
        self.session = session
        self.key = key

        self.setStyleSheet("background-color: #ffad8d;")
        self.setWindowTitle("Legg til passord")

        # Opprett etiketter og inngangsfelt
        self.email_label = QLabel("E-mail brukt:")
        self.email_label.setStyleSheet(styles.LABEL_STYLE)
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.email_input.setTextMargins(5, 0, 0, 0)
        self.email_input.setPlaceholderText("eksempel@domene.com")

        self.username_label = QLabel("Brukernavn (valgfri):")
        self.username_label.setStyleSheet(styles.LABEL_STYLE)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.username_input.setTextMargins(5, 0, 0, 0)
        self.username_input.setPlaceholderText("Ditt brukernavn")

        self.password_label = QLabel("Passord:")
        self.password_label.setStyleSheet(styles.LABEL_STYLE)
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setTextMargins(5, 0, 0, 0)
        self.password_input.setPlaceholderText("Ditt passord")

        self.service_label = QLabel("Tjeneste:")
        self.service_label.setStyleSheet(styles.LABEL_STYLE)
        self.service_input = QLineEdit()
        self.service_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.service_input.setTextMargins(5, 0, 0, 0)
        self.service_input.setPlaceholderText("Google")

        self.link_label = QLabel("Link til nettside:")
        self.link_label.setStyleSheet(styles.LABEL_STYLE)
        self.link_input = QLineEdit()
        self.link_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.link_input.setTextMargins(5, 0, 0, 0)
        self.link_input.setPlaceholderText("https://www.eksempel.com")

        self.tag_label = QLabel("Emneknagg (valgfri):")
        self.tag_label.setStyleSheet(styles.LABEL_STYLE)
        self.tag_input = QLineEdit()
        self.tag_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.tag_input.setTextMargins(5, 0, 0, 0)
        self.tag_input.setPlaceholderText("Arbeid")

        # Lagre-knapp
        self.save_button = QPushButton("Lagre")
        self.save_button.setStyleSheet(styles.BUTTON_STYLE)
        self.save_button.setFixedWidth(150)
        self.save_button.clicked.connect(self.save_password)

        # Opprett en QFormLayout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setSpacing(20)
        form_layout.setHorizontalSpacing(30)

        # Legg til feltene i form_layout
        form_layout.addRow(self.email_label, self.email_input)
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow(self.service_label, self.service_input)
        form_layout.addRow(self.link_label, self.link_input)
        form_layout.addRow(self.tag_label, self.tag_input)

        # Opprett hovedlayouten
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(30)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def save_password(self):
        # Hent data fra feltene
        data = self.get_data()

        # Validering av nødvendige felt
        if not data["service"] or not data["email"] or not data["password"]:
            QMessageBox.warning(
                self, "Feil", "Vennligst fyll ut alle obligatoriske felt."
            )
            return

        # Emit signal med data inkludert bruker_id
        data["user_id"] = self.user.id
        self.password_saved.emit(data)

        # Tøm feltene etter lagring
        self.clear_fields()

    def get_data(self):
        return {
            "service": self.service_input.text(),
            "email": self.email_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "link": self.link_input.text(),
            "tag": self.tag_input.text(),
        }

    def clear_fields(self):
        self.service_input.clear()
        self.email_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.link_input.clear()
        self.tag_input.clear()
