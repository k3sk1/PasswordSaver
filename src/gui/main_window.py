from PySide2.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QStackedWidget,
    QApplication,
)
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QFont

from gui.add_password_widget import AddPasswordWidget
from gui.placeholder_widget import PlaceholderWidget
from gui.settings_widget import SettingsWidget
from gui.show_password_widget import ShowPasswordWidget
from gui.backup_widget import BackupWidget
from gui.login_widget import LoginWidget
from data.models import PasswordEntry, Settings


class MainWindow(QMainWindow):
    logged_out = Signal()  # Dette signalet sender vi når brukeren logger ut

    def __init__(self, key, session, user, db_path):
        super().__init__()

        self.setWindowTitle("Password Saver")
        # Sett en fast størrelse på vinduet
        self.resize(1100, 800)

        # Initialize key, session og user
        self.key = key
        self.session = session
        self.user = user
        self.db_path = db_path

        # Opprett hovedwidget og layout
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #b4a19e;")
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()
        self.central_widget.setLayout(main_layout)

        # Opprett sidepanelet med knappene
        self.create_side_panel(main_layout)

        # Opprett QStackedWidget for å holde forskjellige skjermer
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #fcd4a0;")
        main_layout.addWidget(self.stack)

        # Opprett widgets uten å sette forelder
        self.login_widget = LoginWidget(db_path=self.db_path, existing=True)
        self.placeholder_widget = PlaceholderWidget()

        # Kobler signaler
        self.login_widget.login_success.connect(self.handle_login)

        # Legg widgets til stacken
        self.stack.addWidget(self.login_widget)  # Indeks 0
        self.stack.addWidget(self.placeholder_widget)  # Indeks 1

        # Sett til å vise hovedvinduet
        self.stack.setCurrentWidget(self.login_widget)

        # Vis vinduet
        self.show()

    def create_side_panel(self, main_layout):
        # Sidepanel for knappene
        self.side_panel = QWidget()
        self.side_panel.setStyleSheet("background-color: #a6c4be;")
        side_layout = QVBoxLayout()
        self.side_panel.setLayout(side_layout)

        # Juster layouten
        side_layout.setContentsMargins(10, 10, 10, 10)
        side_layout.setSpacing(20)
        side_layout.setAlignment(Qt.AlignTop)

        # Opprett knapper
        add_password_button = QPushButton("Legg til passord")
        view_password_button = QPushButton("Vis passord")
        backup_button = QPushButton("Sikkerhetskopiering")
        settings_button = QPushButton("Innstillinger")
        log_out_button = QPushButton("Logg ut og bytt bruker")
        log_out_quit_button = QPushButton("Logg ut og avslutt")

        # Koble knappene til funksjoner
        add_password_button.clicked.connect(self.show_add_password_widget)
        view_password_button.clicked.connect(self.show_show_password_widget)
        backup_button.clicked.connect(self.show_backup_widget)
        settings_button.clicked.connect(self.open_settings)
        log_out_button.clicked.connect(self.log_out)
        log_out_quit_button.clicked.connect(self.log_out_quit)

        # Lagre referansene som instansvariabler
        self.view_password_button = view_password_button
        self.backup_button = backup_button

        # Legg knappene til i layouten
        side_layout.addWidget(add_password_button)
        side_layout.addWidget(view_password_button)
        side_layout.addWidget(backup_button)
        side_layout.addWidget(settings_button)
        # Legg til et strekk-element for å skyve logg ut-knappene til bunnen
        side_layout.addStretch()

        # Legg logg ut-knappene nederst
        side_layout.addWidget(log_out_button)
        side_layout.addWidget(log_out_quit_button)

        # Start med å skjule sidepanelet
        self.side_panel.setVisible(False)

        # Legg til sidepanelet i hovedlayouten
        main_layout.addWidget(self.side_panel)

    def update_button_states(self):
        try:
            # Filtrere passordene til den innloggede brukeren
            password_count = (
                self.session.query(PasswordEntry)
                .filter_by(user_id=self.user.id)
                .count()
            )
            if password_count > 0:
                self.view_password_button.setEnabled(True)
                self.backup_button.setEnabled(True)
            else:
                self.view_password_button.setEnabled(False)
                self.backup_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Feil",
                f"Kunne ikke sjekke passordene: {str(e)}",
                QMessageBox.Ok,
            )
            self.view_password_button.setEnabled(False)
            self.backup_button.setEnabled(False)

    def show_add_password_widget(self, password_data=None):
        # Bytt til AddPasswordWidget i stacken
        self.stack.setCurrentWidget(self.add_password_widget)

        # Hvis det er passorddata som skal redigeres, fyll inn feltene
        if password_data:
            self.add_password_widget.fill_fields(password_data)
        else:
            # Hvis ingen data er gitt, tøm feltene for å legge til nytt passord
            self.add_password_widget.clear_fields()

    def show_show_password_widget(self):
        # Last inn passordene når widgeten skal vises
        self.show_password_widget.load_passwords()
        self.stack.setCurrentWidget(self.show_password_widget)

    def show_backup_widget(self):
        self.stack.setCurrentWidget(self.backup_widget)

    def open_settings(self):
        # Bytt til settings_widget i stacken
        self.stack.setCurrentWidget(self.settings_widget)

    def switch_back(self):
        # Bytt tilbake til placeholder uten å endre innstillinger
        self.stack.setCurrentWidget(self.placeholder_widget)

    def apply_settings_and_save(self, settings):
        theme, font_size = settings
        self.save_user_settings(theme, font_size)
        self.apply_settings()

    def save_user_settings(self, theme, font_size):
        # Oppdater brukerinnstillingene i databasen
        if self.user.settings:
            self.user.settings.theme = theme
            self.user.settings.font_size = font_size
        else:
            # Opprett standardinnstillinger hvis de ikke finnes
            self.user.settings = Settings(theme=theme, font_size=font_size)
            self.session.add(self.user.settings)
        self.session.commit()

    def get_user_settings(self):
        return {
            "theme": self.user.settings.theme if self.user.settings else "default",
            "font_size": self.user.settings.font_size if self.user.settings else 16,
        }

    def apply_settings(self):
        settings = self.get_user_settings()
        self.apply_theme(settings["theme"])
        self.apply_font_size(settings["font_size"])

    def apply_theme(self, theme):
        theme_colors = {"vintage": "#f0e68c", "default": "#b4a19e"}
        self.setStyleSheet(f"background-color: {theme_colors.get(theme, '#b4a19e')};")

    def apply_font_size(self, font_size):
        new_font = QFont()
        new_font.setPointSize(font_size)
        QApplication.instance().setFont(new_font)
        self.set_font_recursively(self, new_font)

    def set_font_recursively(self, widget, font):
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            self.set_font_recursively(child, font)

    def log_out(self):
        # Skjul sidepanelet når brukeren logger ut
        self.side_panel.setVisible(False)
        self.logged_out.emit()
        self.stack.setCurrentWidget(self.login_widget)

    def log_out_quit(self):
        # Lukk applikasjonen helt
        QApplication.quit()

    def handle_login(self, credentials):
        username = credentials["username"]
        password = credentials["password"]

        # Her bruker du login_manager for å autentisere brukeren
        user, key, message = self.login_manager.authenticate_user(username, password)
        if user:
            print("Login successful, switching to main view.")
            # Sett `user` og `key` etter vellykket login
            self.user = user
            self.key = key

            # Oppdater widgets som trenger nøkkelen
            self.add_password_widget = AddPasswordWidget(
                self.user, self.session, self.key, self
            )
            self.show_password_widget = ShowPasswordWidget(
                self.session, self.key, self.user, self
            )
            self.backup_widget = BackupWidget(
                self.user, self.db_path, self.key, self.session
            )
            self.settings_widget = SettingsWidget(
                user=self.user,
                session=self.session,
                key=self.key,
                current_theme=(
                    self.user.settings.theme if self.user.settings else "default"
                ),
                current_font_size=(
                    self.user.settings.font_size if self.user.settings else 16
                ),
            )

            # Koble signalene fra de nye widgetene til de riktige funksjonene
            self.add_password_widget.password_saved.connect(self.update_button_states)
            self.backup_widget.sync_completed.connect(self.update_button_states)
            self.show_password_widget.row_deleted.connect(self.update_button_states)
            self.settings_widget.settings_changed.connect(self.apply_settings_and_save)
            self.settings_widget.settings_cancelled.connect(self.switch_back)

            # Legg de oppdaterte widgets til stacken
            self.stack.addWidget(self.add_password_widget)  # Indeks 2
            self.stack.addWidget(self.show_password_widget)  # Indeks 3
            self.stack.addWidget(self.backup_widget)  # Indeks 4
            self.stack.addWidget(self.settings_widget)  # Indeks 5

            # Oppdater innstillingene etter at brukeren er logget inn
            self.apply_settings()

            # Vis sidepanelet etter vellykket innlogging
            self.side_panel.setVisible(True)

            # Sjekk antall passord og oppdater knappene (initialiser status)
            self.update_button_states()

            # Bytt til placeholder widget eller hovedvisningen etter login
            self.stack.setCurrentWidget(self.placeholder_widget)
        else:
            QMessageBox.critical(self, "Feil", message, QMessageBox.Ok)
            print("Authentication failed.")

    def switch_to_widget(self, widget):
        self.stack.setCurrentWidget(widget)
