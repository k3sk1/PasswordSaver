# gui/login_dialog.py
from PySide2.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
import styles


class LoginDialog(QDialog):
    def __init__(self, existing=False, parent=None):
        super().__init__(parent)

        self.existing = existing  # Lagre parameteren

        self.setWindowTitle("Innlogging" if existing else "Opprett Masterpassord")
        self.setFixedSize(500, 300)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Opprett etiketter og inngangsfelt
        if existing:
            self.label = QLabel("Skriv inn ditt hovedpassord")
        else:
            self.label = QLabel("Opprett et nytt hovedpassord")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(styles.LABEL_STYLE)

        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Skriv inn ditt hovedpassord")
        self.password_input.setMinimumWidth(200)

        if not existing:
            self.confirm_label = QLabel("Bekreft hovedpassord")
            self.confirm_label.setAlignment(Qt.AlignCenter)
            self.confirm_label.setStyleSheet(styles.LABEL_STYLE)

            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setStyleSheet(styles.LINE_EDIT_STYLE)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setPlaceholderText("Bekreft ditt hovedpassord")
            self.confirm_password_input.setMinimumWidth(200)

        # Ok og Avbryt knapper
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Avbryt")

        ok_button.setStyleSheet(styles.BUTTON_STYLE)
        cancel_button.setStyleSheet(styles.BUTTON_STYLE)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        # Layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.password_input)

        if not existing:
            main_layout.addWidget(self.confirm_label)
            main_layout.addWidget(self.confirm_password_input)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_password(self):
        return self.password_input.text()

    def get_confirm_password(self):
        if not self.existing:
            return self.confirm_password_input.text()
        return None
