from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QMenuBar,
    QAction,
)
from PySide2.QtCore import Qt, Signal
import styles
from utils.login_manager import LoginManager


class LoginWidget(QWidget):
    login_success = Signal(dict)

    def __init__(self, db_path, existing=True, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.login_manager = LoginManager(db_path)

        self.mode = "login" if existing else "register"

        # Create labels and input fields
        self.username_label = QLabel("Brukernavn:")
        self.username_label.setAlignment(Qt.AlignCenter)
        self.username_label.setStyleSheet(styles.LABEL_STYLE)

        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(styles.PASSWORD_STYLE)
        self.username_input.setPlaceholderText("Skriv inn ditt brukernavn")
        self.username_input.setMinimumWidth(200)

        self.password_label = QLabel("Passord:")
        self.password_label.setAlignment(Qt.AlignCenter)
        self.password_label.setStyleSheet(styles.LABEL_STYLE)

        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(styles.PASSWORD_STYLE)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Skriv inn ditt passord")
        self.password_input.setMinimumWidth(200)

        # Confirm password field (only for registration)
        self.confirm_password_label = QLabel("Bekreft passord:")
        self.confirm_password_label.setAlignment(Qt.AlignCenter)
        self.confirm_password_label.setStyleSheet(styles.LABEL_STYLE)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setStyleSheet(styles.PASSWORD_STYLE)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Bekreft ditt passord")
        self.confirm_password_input.setMinimumWidth(200)

        # Ok and Cancel buttons
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet(styles.BUTTON_STYLE)
        self.ok_button.clicked.connect(self.on_ok)

        self.cancel_button = QPushButton("Tøm felt")
        self.cancel_button.setStyleSheet(styles.BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.clear_inputs)

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
            self.clear_inputs()
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

            # Fjern den tomme "Bytt Bruker"-fanen
            self.menu_bar.removeAction(self.empty_menu.menuAction())
            del self.empty_menu

    def on_ok(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        print("Attempting to login/register with:", username, password)

        if not self.validate_inputs(username, password, confirm_password):
            return

        if self.mode == "login":
            # Vellykket innlogging
            self.login_success.emit(
                {"mode": self.mode, "username": username, "password": password}
            )
            self.clear_inputs()
        else:  # Registreringsmodus
            if self.try_register_user(username, password):
                QMessageBox.information(self, "Suksess", "Bruker opprettet!")
                self.switch_mode()  # Bytt tilbake til innloggingsmodus
                self.username_input.setText(username)
                self.password_input.setFocus()
                self.clear_inputs()
            else:
                QMessageBox.critical(
                    self, "Feil", "Kunne ikke opprette bruker. Prøv igjen."
                )

    def validate_inputs(self, username, password, confirm_password):
        """Validerer input-feltene for både innlogging og registrering."""
        if not username or not password:
            QMessageBox.warning(
                self, "Feil", "Vennligst fyll ut både brukernavn og passord."
            )
            return False

        if self.mode == "register" and not confirm_password:
            QMessageBox.warning(
                self, "Feil", "Vennligst fyll ut alle obligatoriske felt."
            )
            return False

        if self.mode == "register" and password != confirm_password:
            QMessageBox.warning(self, "Feil", "Passordene stemmer ikke overens.")
            return False

        return True

    def try_register_user(self, username, password):
        """Prøv å registrere brukeren og returner True/False avhengig av suksess."""
        return self.login_manager.register_user(username, password)

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()

    def populate_user_menu(self):
        # Clear the menu first to avoid duplicates when refilling it
        self.switch_user_menu.clear()

        # Get all users from the database via a query function
        all_users = self.login_manager.get_all_users()

        def create_user_action(user):
            return lambda checked: self.switch_to_user(user)

        for user in all_users:
            # Create an action for each user that can be selected
            user_action = QAction(user, self)
            user_action.triggered.connect(create_user_action(user))
            self.switch_user_menu.addAction(user_action)

    def switch_to_user(self, user):
        # Update the username input with the selected username
        self.username_input.setText(user)
        # Focus on the password field for easier login
        self.password_input.setFocus()
