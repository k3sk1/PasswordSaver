from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QAction,
    QMenu,
)
from PySide2.QtCore import Qt, Signal
from utils.login_manager import LoginManager


class LoginWidget(QWidget):
    login_success = Signal(dict)

    def __init__(self, db_path, style_manager, existing=True, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.login_manager = LoginManager(db_path)
        self.style_manager = style_manager

        self.mode = "login" if existing else "register"

        # Create a button that will show the menu when clicked
        self.user_menu_button = QPushButton("Bytt Bruker")

        # Create a dropdown menu (QMenu)
        self.user_menu = QMenu(self)

        # Populate the menu with some example actions (replace with actual users)
        self.populate_user_menu()

        # Assign the menu to the button
        self.user_menu_button.setMenu(self.user_menu)

        # Create labels and input fields
        self.log_in_title = QLabel("Logg inn")
        self.log_in_title.setStyleSheet("font-weight: bold;")
        self.log_in_title.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Brukernavn")
        self.username_input.setMinimumWidth(200)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Passord")
        self.password_input.setMinimumWidth(200)

        # Confirm password field (only for registration)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Bekreft passord")
        self.confirm_password_input.setMinimumWidth(200)

        # Ok and Cancel buttons
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.on_ok)

        self.cancel_button = QPushButton("Tøm felt")
        self.cancel_button.clicked.connect(self.clear_inputs)

        # Switch mode button
        self.switch_mode_button = QPushButton(
            "Opprett ny bruker" if existing else "Tilbake til innlogging"
        )
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
        mode_switch_layout.addWidget(self.user_menu_button)
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
        main_layout.addWidget(self.log_in_title)
        main_layout.addLayout(username_layout)
        main_layout.addLayout(password_layout)
        main_layout.addLayout(confirm_password_layout)

        # Hide confirm password fields in login mode
        if self.mode == "login":
            self.confirm_password_input.hide()

        # Add buttons
        main_layout.addLayout(button_layout)
        main_layout.addLayout(mode_switch_layout)

        self.setLayout(main_layout)

        self.init_ui_login()

    def init_ui_login(self):
        # Bruk style_manager til å sette stiler på widgets
        self.style_manager.apply_password_input_style(self.username_input)
        self.style_manager.apply_password_input_style(self.password_input)
        self.style_manager.apply_password_input_style(self.confirm_password_input)
        self.style_manager.apply_button_style(self.user_menu_button)
        self.style_manager.apply_button_style_1(self.ok_button)
        self.style_manager.apply_button_style_1(self.switch_mode_button)
        self.style_manager.apply_button_style_2(self.cancel_button)

    def switch_mode(self):
        if self.mode == "login":
            self.mode = "register"
            self.setWindowTitle("Opprett Bruker")
            self.log_in_title.setText("Registrer Bruker")
            self.switch_mode_button.setText("Tilbake til innlogging")
            self.clear_inputs()
            self.confirm_password_input.show()
            self.user_menu_button.setVisible(False)  # Skjul "Bytt Bruker"-knappen
        else:
            self.mode = "login"
            self.setWindowTitle("Innlogging")
            self.log_in_title.setText("Logg inn")
            self.switch_mode_button.setText("Opprett ny bruker")
            self.confirm_password_input.hide()

            # Tøm passordfeltene når vi bytter til innloggingsmodus, men la brukernavnet være
            self.password_input.clear()
            self.confirm_password_input.clear()

            self.user_menu_button.setVisible(True)  # Vis "Bytt Bruker"-knappen igjen)

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
        # Clear the menu first to avoid duplicates
        self.user_menu.clear()

        # Get all users from the database via a query function
        all_users = self.login_manager.get_all_users()

        def create_user_action(user):
            return lambda checked: self.switch_to_user(user)

        for user in all_users:
            # Create an action for each user that can be selected
            user_action = QAction(user, self)
            user_action.triggered.connect(create_user_action(user))
            self.user_menu.addAction(user_action)

    def switch_to_user(self, user):
        # Update the username input with the selected username
        self.username_input.setText(user)
        # Focus on the password field for easier login
        self.password_input.setFocus()
