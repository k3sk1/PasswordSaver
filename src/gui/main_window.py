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
from utils.style_manager import StyleManager


class MainWindow(QMainWindow):
    logged_out = Signal()  # Dette signalet sender vi når brukeren logger ut
    theme_changed = Signal()  # Signal som sendes når temaet endres

    def __init__(self, key, session, user, db_path):
        super().__init__()

        self.style_manager = StyleManager()

        self.setWindowTitle("Passordskapet")
        # Sett en fast størrelse på vinduet

        # Initialize key, session og user
        self.key = key
        self.session = session
        self.user = user
        self.db_path = db_path

        # Opprett hovedwidget og layout
        self.central_widget = QWidget()
        self.style_manager.apply_central_widget_style(self.central_widget)
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.central_widget.setLayout(main_layout)

        # Opprett sidepanelet med knappene
        self.create_side_panel(main_layout)

        # Opprett QStackedWidget for å holde forskjellige skjermer
        self.stack = QStackedWidget()
        self.style_manager.apply_stack_style(self.stack)
        main_layout.addWidget(self.stack)

        # Opprett widgets uten å sette forelder
        self.login_widget = LoginWidget(
            db_path=self.db_path, style_manager=self.style_manager, existing=True
        )
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
        # Apply dynamic style using the StyleManager
        self.style_manager.apply_side_panel_style(self.side_panel)
        side_layout = QVBoxLayout()
        self.side_panel.setLayout(side_layout)

        # Juster layouten
        side_layout.setSpacing(20)
        side_layout.setAlignment(Qt.AlignTop)

        # Add buttons
        self.add_password_button = QPushButton("Legg til passord")
        self.view_password_button = QPushButton("Vis passord")
        self.backup_button = QPushButton("Sikkerhetskopiering")
        self.settings_button = QPushButton("Innstillinger")
        self.log_out_button = QPushButton("Logg ut og bytt bruker")
        self.log_out_quit_button = QPushButton("Logg ut og avslutt")

        # Apply button styles
        self.init_ui()

        # Koble knappene til funksjoner
        self.add_password_button.clicked.connect(self.show_add_password_widget)
        self.view_password_button.clicked.connect(self.show_show_password_widget)
        self.backup_button.clicked.connect(self.show_backup_widget)
        self.settings_button.clicked.connect(self.open_settings)
        self.log_out_button.clicked.connect(self.log_out)
        self.log_out_quit_button.clicked.connect(self.log_out_quit)

        # Legg knappene til i layouten
        side_layout.addWidget(self.add_password_button)
        side_layout.addWidget(self.view_password_button)
        side_layout.addWidget(self.backup_button)
        side_layout.addWidget(self.settings_button)
        # Legg til et strekk-element for å skyve logg ut-knappene til bunnen
        side_layout.addStretch()

        # Legg logg ut-knappene nederst
        side_layout.addWidget(self.log_out_button)
        side_layout.addWidget(self.log_out_quit_button)

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
                self.view_password_button.setVisible(True)
                self.backup_button.setVisible(True)
            else:
                self.view_password_button.setVisible(False)
                self.backup_button.setVisible(False)
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

    def switch_to_widget(self, widget):
        self.stack.setCurrentWidget(widget)

    def open_settings(self):
        # Bytt til settings_widget i stacken
        self.stack.setCurrentWidget(self.settings_widget)

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
        settings = {
            "theme": self.user.settings.theme if self.user.settings else "default",
            "font_size": self.user.settings.font_size if self.user.settings else 16,
        }
        return settings

    def apply_settings(self):
        settings = self.get_user_settings()

        # Sjekk om temaet faktisk har endret seg før vi bruker stiler på nytt
        current_theme = self.style_manager.theme
        current_font_size = QApplication.instance().font().pointSize()

        if (
            settings["theme"] != current_theme
            or settings["font_size"] != current_font_size
        ):
            self.apply_theme(settings["theme"])
            self.apply_font_size(settings["font_size"])

    def apply_theme(self, theme):
        # Kun oppdater stil hvis temaet faktisk er nytt
        if self.style_manager.theme != theme:
            self.style_manager = StyleManager(theme)
            self.init_ui()

            # Apply central widget style directly here to ensure it's updated
            self.style_manager.apply_central_widget_style(self.central_widget)

            # Apply stack background color again to ensure it's updated with the new theme
            self.style_manager.apply_stack_style(self.stack)

            # Emit signalet etter at temaet har blitt brukt
            self.theme_changed.emit()

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
            self.backup_widget = BackupWidget(self)
            self.settings_widget = SettingsWidget(
                main_window=self,
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
            self.settings_widget.settings_cancelled.connect(
                lambda: self.switch_to_widget(self.placeholder_widget)
            )

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

            self.setMinimumSize(0, 0)
            self.showMaximized()

            # Bytt til placeholder widget eller hovedvisningen etter login
            self.stack.setCurrentWidget(self.placeholder_widget)
        else:
            QMessageBox.critical(self, "Feil", message, QMessageBox.Ok)

    def init_ui(self):
        # Apply updated styles
        self.style_manager.apply_button_style_1(self.add_password_button)
        self.style_manager.apply_button_style(self.view_password_button)
        self.style_manager.apply_button_style(self.backup_button)
        self.style_manager.apply_button_style(self.settings_button)
        self.style_manager.apply_button_style_2(self.log_out_button)
        self.style_manager.apply_button_style_2(self.log_out_quit_button)
