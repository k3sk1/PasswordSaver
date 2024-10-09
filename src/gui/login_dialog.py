from PySide2.QtWidgets import (
    QDialog,
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
from PySide2.QtCore import Qt
import styles
from data.query_functions import get_all_users


class LoginDialog(QDialog):
    def __init__(self, db_path, session, existing=True, parent=None):
        super().__init__(parent)

        self.session = session
        self.db_path = db_path

        self.setWindowTitle("Innlogging" if existing else "Opprett Bruker")
        self.setFixedSize(500, 400)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.mode = "login" if existing else "register"

        # Opprett etiketter og inngangsfelt
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

        # Bekreft passordfelt (bare for registrering)
        self.confirm_password_label = QLabel("Bekreft passord:")
        self.confirm_password_label.setAlignment(Qt.AlignCenter)
        self.confirm_password_label.setStyleSheet(styles.LABEL_STYLE)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Bekreft ditt passord")
        self.confirm_password_input.setMinimumWidth(200)

        # Ok og Avbryt knapper
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet(styles.BUTTON_STYLE)
        self.ok_button.clicked.connect(self.on_ok)

        self.cancel_button = QPushButton("Avbryt")
        self.cancel_button.setStyleSheet(styles.BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.reject)

        # Knapper for å bytte modus
        self.switch_mode_button = QPushButton(
            "Opprett ny bruker" if existing else "Tilbake til innlogging"
        )
        self.switch_mode_button.setStyleSheet(styles.BUTTON_STYLE)
        self.switch_mode_button.clicked.connect(self.switch_mode)

        # Layout for ok og avbryt knapper
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()

        # Layout for bytte modus knappen
        mode_switch_layout = QHBoxLayout()
        mode_switch_layout.addStretch()
        mode_switch_layout.addWidget(self.switch_mode_button)
        mode_switch_layout.addStretch()

        # Hovedlayout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Legg til brukernavn og passordfelt
        main_layout.addWidget(self.username_label)
        main_layout.addWidget(self.username_input)
        main_layout.addWidget(self.password_label)
        main_layout.addWidget(self.password_input)

        # Legg til bekreft passordfelt alltid, men skjul det hvis i login mode
        main_layout.addWidget(self.confirm_password_label)
        main_layout.addWidget(self.confirm_password_input)
        if self.mode == "login":
            self.confirm_password_label.hide()
            self.confirm_password_input.hide()

        # Legg til knappene
        main_layout.addLayout(button_layout)
        main_layout.addLayout(mode_switch_layout)

        self.setLayout(main_layout)

        # Opprett menylinjen
        self.menu_bar = QMenuBar(self)
        self.layout().setMenuBar(self.menu_bar)

        # Legg til en "Bytt bruker"-meny
        self.switch_user_menu = self.menu_bar.addMenu("Bytt Bruker")
        self.populate_user_menu()

    def switch_mode(self):
        if self.mode == "login":
            self.mode = "register"
            self.setWindowTitle("Opprett Bruker")
            self.switch_mode_button.setText("Tilbake til innlogging")
            self.username_input.clear()
            self.confirm_password_label.show()
            self.confirm_password_input.show()
            self.switch_user_menu.menuAction().setVisible(False)
        else:
            self.mode = "login"
            self.setWindowTitle("Innlogging")
            self.switch_mode_button.setText("Opprett ny bruker")
            self.confirm_password_label.hide()
            self.confirm_password_input.hide()
            self.username_input.clear()
            self.password_input.clear()
            self.switch_user_menu.menuAction().setVisible(True)

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
            self.accept()
        else:
            if not username or not password or not confirm_password:
                QMessageBox.warning(
                    self, "Feil", "Vennligst fyll ut alle obligatoriske felt."
                )
                return
            if password != confirm_password:
                QMessageBox.warning(self, "Feil", "Passordene stemmer ikke overens.")
                return
            self.accept()

    def get_credentials(self):
        return {
            "mode": self.mode,
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "confirm_password": (
                self.confirm_password_input.text() if self.mode == "register" else None
            ),
        }

    def populate_user_menu(self):
        # Tøm menyen først (for å unngå duplikater når menyen fylles på nytt)
        self.switch_user_menu.clear()

        # Hent alle brukerne fra databasen via query-funksjon
        all_users = get_all_users(self.db_path, self.session)

        def create_user_action(user):
            return lambda checked: self.switch_to_user(user)

        for user in all_users:
            # Opprett en handling for hver bruker som kan velges
            user_action = QAction(user[0], self)  # bruker username fra tuple
            user_action.triggered.connect(create_user_action(user[0]))
            self.switch_user_menu.addAction(user_action)

    def switch_to_user(self, user):
        # Oppdater brukernavnsfeltet med det valgte brukernavnet
        self.username_input.setText(user)  # bruker username fra tuple
        # Fokus på passordfeltet for å gjøre det enklere å skrive inn passord
        self.password_input.setFocus()
