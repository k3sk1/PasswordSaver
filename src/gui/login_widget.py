import base64
import os
from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QSizePolicy,
    QMenuBar,
    QAction,
)
from PySide2.QtCore import Qt, Signal
import styles
from data.query_functions import get_all_users
from data.models import User
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class LoginWidget(QWidget):
    login_success = Signal(dict)

    def __init__(self, session, db_path, existing=True, parent=None):
        super().__init__(parent)
        self.session = session
        self.db_path = db_path

        self.mode = "login" if existing else "register"

        # Set widget size
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Create labels and input fields
        self.username_label = QLabel("Brukernavn:")
        self.username_label.setAlignment(Qt.AlignCenter)
        self.username_label.setStyleSheet(styles.LABEL_STYLE)

        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.username_input.setPlaceholderText("Skriv inn ditt brukernavn")
        self.username_input.setMinimumWidth(200)

        self.password_label = QLabel("Passord:")
        self.password_label.setAlignment(Qt.AlignCenter)
        self.password_label.setStyleSheet(styles.LABEL_STYLE)

        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Skriv inn ditt passord")
        self.password_input.setMinimumWidth(200)

        # Confirm password field (only for registration)
        self.confirm_password_label = QLabel("Bekreft passord:")
        self.confirm_password_label.setAlignment(Qt.AlignCenter)
        self.confirm_password_label.setStyleSheet(styles.LABEL_STYLE)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Bekreft ditt passord")
        self.confirm_password_input.setMinimumWidth(200)

        # # Updated styles to make input fields have a white background
        self.username_input.setStyleSheet(styles.PASSWORD_STYLE)
        self.password_input.setStyleSheet(styles.PASSWORD_STYLE)
        self.confirm_password_input.setStyleSheet(styles.PASSWORD_STYLE)

        # Ok and Cancel buttons
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet(styles.BUTTON_STYLE)
        self.ok_button.clicked.connect(self.on_ok)

        self.cancel_button = QPushButton("Tøm felt")
        self.cancel_button.setStyleSheet(styles.BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.reject)

        # Switch mode button
        self.switch_mode_button = QPushButton(
            "Opprett ny bruker" if existing else "Tilbake til innlogging"
        )
        self.switch_mode_button.setStyleSheet(styles.BUTTON_STYLE)
        self.switch_mode_button.clicked.connect(self.switch_mode)

        # Button layout for ok and cancel buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()

        # Layout for switch mode button
        mode_switch_layout = QHBoxLayout()
        mode_switch_layout.addStretch()
        mode_switch_layout.addWidget(self.switch_mode_button)
        mode_switch_layout.addStretch()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # Add username and password fields with padding
        username_layout = QHBoxLayout()
        username_layout.addStretch()
        username_layout.addWidget(self.username_input)
        username_layout.addStretch()

        password_layout = QHBoxLayout()
        password_layout.addStretch()
        password_layout.addWidget(self.password_input)
        password_layout.addStretch()

        confirm_password_layout = QHBoxLayout()
        confirm_password_layout.addStretch()
        confirm_password_layout.addWidget(self.confirm_password_input)
        confirm_password_layout.addStretch()

        # Add username, password, and confirm password fields
        main_layout.addWidget(self.username_label)
        main_layout.addLayout(username_layout)
        main_layout.addWidget(self.password_label)
        main_layout.addLayout(password_layout)
        main_layout.addWidget(self.confirm_password_label)
        main_layout.addLayout(confirm_password_layout)

        # Hide confirm password fields in login mode
        if self.mode == "login":
            self.confirm_password_label.hide()
            self.confirm_password_input.hide()

        # Add buttons
        main_layout.addLayout(button_layout)
        main_layout.addLayout(mode_switch_layout)

        self.setLayout(main_layout)

        # Menu bar for switching user
        self.menu_bar = QMenuBar(self)
        self.layout().setMenuBar(self.menu_bar)

        # Add a "Switch User" menu
        self.switch_user_menu = self.menu_bar.addMenu("Bytt Bruker")
        self.populate_user_menu()

    def switch_mode(self):
        if self.mode == "login":
            self.mode = "register"
            self.setWindowTitle("Opprett Bruker")
            self.switch_mode_button.setText("Tilbake til innlogging")
            self.username_input.clear()
            self.password_input.clear()  # Tøm passordfeltet
            self.confirm_password_input.clear()  # Tøm bekreft passordfeltet
            self.confirm_password_label.show()
            self.confirm_password_input.show()
            self.switch_user_menu.menuAction().setVisible(False)

            # Legg til en tom "Bytt Bruker"-fane for å beholde plasseringen av menylinjen
            self.empty_menu = self.menu_bar.addMenu(" ")
        else:
            self.mode = "login"
            self.setWindowTitle("Innlogging")
            self.switch_mode_button.setText("Opprett ny bruker")
            self.confirm_password_label.hide()
            self.confirm_password_input.hide()

            # Tøm passordfeltene når vi bytter til innloggingsmodus, men la brukernavnet være
            self.password_input.clear()
            self.confirm_password_input.clear()

            self.switch_user_menu.menuAction().setVisible(True)

            # Fjern den tomme "Bytt Bruker"-fanen hvis den eksisterer
            if hasattr(self, "empty_menu"):
                self.menu_bar.removeAction(self.empty_menu.menuAction())
                del self.empty_menu

    def on_ok(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        print("Attempting to login/register with:", username, password)

        if self.mode == "login":
            if not username or not password:
                QMessageBox.warning(
                    self, "Feil", "Vennligst fyll ut både brukernavn og passord."
                )
                return
            self.login_success.emit(
                {"mode": self.mode, "username": username, "password": password}
            )
            # Nullstill feltene etter vellykket innlogging
            self.clear_inputs()
        else:  # Registreringsmodus
            if not username or not password or not confirm_password:
                QMessageBox.warning(
                    self, "Feil", "Vennligst fyll ut alle obligatoriske felt."
                )
                return
            if password != confirm_password:
                QMessageBox.warning(self, "Feil", "Passordene stemmer ikke overens.")
                return

            # Lagre ny bruker i databasen
            if self.register_user(username, password):
                QMessageBox.information(self, "Suksess", "Bruker opprettet!")
                self.switch_mode()  # Bytt tilbake til innloggingsmodus
                # Sett brukernavn input til det nye brukernavnet
                self.username_input.setText(username)
                self.password_input.setFocus()
                # Tøm passordfeltene etter registrering
                self.password_input.clear()
                self.confirm_password_input.clear()
            else:
                QMessageBox.critical(
                    self, "Feil", "Kunne ikke opprette bruker. Prøv igjen."
                )

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()

    def populate_user_menu(self):
        # Clear the menu first to avoid duplicates when refilling it
        self.switch_user_menu.clear()

        # Get all users from the database via a query function
        all_users = get_all_users(self.db_path, self.session)

        def create_user_action(user):
            return lambda checked: self.switch_to_user(user)

        for user in all_users:
            # Create an action for each user that can be selected
            user_action = QAction(user[0], self)  # Use username from tuple
            user_action.triggered.connect(create_user_action(user[0]))
            self.switch_user_menu.addAction(user_action)

    def switch_to_user(self, user):
        # Update the username input with the selected username
        self.username_input.setText(user)  # Use username from tuple
        # Focus on the password field for easier login
        self.password_input.setFocus()

    def reject(self):
        # Handle cancel action - this could close the widget or go back to the previous view
        self.clear_inputs()

    def register_user(self, username, password):
        # Sjekk om brukernavn allerede eksisterer
        existing_user = self.session.query(User).filter_by(username=username).first()
        if existing_user:
            QMessageBox.warning(self, "Feil", "Brukernavnet er allerede i bruk.")
            return False

        # Generer en salt-verdi og hashe passordet
        salt = os.urandom(16)
        hashed_password = self.hash_password(password, salt)

        # Opprett en ny bruker og legg til i databasen
        new_user = User(
            username=username,
            password_hash=hashed_password,
            salt=base64.b64encode(salt).decode(),
        )
        self.session.add(new_user)
        self.session.commit()
        return True

    def hash_password(self, password, salt, iterations=100000):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return base64.b64encode(kdf.derive(password.encode())).decode().strip()
