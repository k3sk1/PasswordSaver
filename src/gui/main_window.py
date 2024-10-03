from PySide2.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QStackedWidget,
    QAction,
    QApplication,
    QInputDialog,
    QLineEdit,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QHeaderView,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from gui.add_password_widget import AddPasswordWidget
from gui.create_database_widget import CreateDatabaseWidget
from gui.placeholder_widget import PlaceholderWidget
from gui.settings_widget import SettingsWidget
from gui.show_password_widget import ShowPasswordWidget
import styles

from data.encryption import derive_key, encrypt_password, decrypt_password
from data.database import get_engine, create_tables, get_session
from data.models import PasswordEntry

import os
import json
import base64
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Saver")
        # Sett en fast størrelse på vinduet
        self.resize(1000, 800)

        # Initialize key and session
        self.key = None
        self.session = None

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
        self.placeholder_widget = PlaceholderWidget()
        self.add_password_widget = AddPasswordWidget()
        self.create_database_widget = CreateDatabaseWidget()
        self.settings_widget = SettingsWidget(
            current_font_family=self.font().family(),
            current_font_size=self.font().pointSize(),
        )

        # Kobler signaler
        self.settings_widget.settings_changed.connect(self.apply_font_and_switch)
        self.settings_widget.settings_cancelled.connect(self.switch_back)
        self.create_database_widget.database_created.connect(self.on_database_created)
        self.add_password_widget.password_saved.connect(self.save_password)

        # Legg widgets til stacken
        self.stack.addWidget(self.placeholder_widget)  # Indeks 0
        self.stack.addWidget(self.add_password_widget)  # Indeks 1
        self.stack.addWidget(self.create_database_widget)  # Indeks 2
        self.stack.addWidget(self.settings_widget)  # Indeks 3

        # Skjul alle widgets ved oppstart
        self.stack.setCurrentWidget(self.placeholder_widget)

        # Sett global font
        self.apply_font((self.font().family(), self.font().pointSize()))

        # Forsøk å laste eksisterende database
        if self.load_existing_database():
            pass

        # Vis vinduet
        self.show()

    def create_side_panel(self, main_layout):
        # Sidepanel for knappene
        side_panel = QWidget()
        side_panel.setStyleSheet("background-color: #a6c4be;")
        side_layout = QVBoxLayout()
        side_panel.setLayout(side_layout)

        # Juster layouten
        side_layout.setContentsMargins(10, 10, 10, 10)
        side_layout.setSpacing(20)
        side_layout.setAlignment(Qt.AlignTop)

        # Opprett knapper
        add_password_button = QPushButton("Legg til passord")
        view_password_button = QPushButton("Vis passord")
        settings_button = QPushButton("Innstillinger")

        # Koble knappene til funksjoner
        add_password_button.clicked.connect(self.show_add_password_widget)
        view_password_button.clicked.connect(self.show_show_password_widget)
        settings_button.clicked.connect(self.open_settings)

        # Legg knappene til i layouten
        side_layout.addWidget(add_password_button)
        side_layout.addWidget(view_password_button)
        side_layout.addWidget(settings_button)

        # Sett maksimal bredde på sidepanelet
        side_panel.setMaximumWidth(300)

        # Legg til sidepanelet i hovedlayouten
        main_layout.addWidget(side_panel)

    def load_existing_database(self):
        # Få den absolutte stien til 'data' mappen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "..", "data")
        salt_file = os.path.join(data_dir, "salt.json")
        db_path = os.path.join(data_dir, "passwords.db")

        if os.path.exists(salt_file) and os.path.exists(db_path):
            try:
                with open(salt_file, "r") as f:
                    data = json.load(f)
                    salt = base64.b64decode(data["salt"])
                    key = data["key"].encode()

                # Sett opp databasen
                engine = get_engine(db_path)
                create_tables(engine)
                session = get_session(engine)

                # Sett key og session
                self.key = key
                self.session = session

                return True
            except Exception as e:
                QMessageBox.critical(
                    self, "Feil", f"Kunne ikke laste eksisterende database: {str(e)}"
                )
                return False
        else:
            return False

    def show_add_password_widget(self):
        if self.is_database_setup():
            # Database er satt opp, vis AddPasswordWidget
            self.stack.setCurrentWidget(self.add_password_widget)
        else:
            # Database er ikke satt opp, vis CreateDatabaseWidget
            self.stack.setCurrentWidget(self.create_database_widget)

    def show_show_password_widget(self):
        if self.is_database_setup():
            # Sjekk om ShowPasswordWidget allerede er instansiert
            if not hasattr(self, "show_password_widget"):
                # Instansier ShowPasswordWidget hvis den ikke allerede er instansiert
                self.show_password_widget = ShowPasswordWidget(self.session, self.key)
                self.stack.addWidget(self.show_password_widget)
            # Last inn passordene når widgeten skal vises
            self.show_password_widget.load_passwords()
            self.stack.setCurrentWidget(self.show_password_widget)
        else:
            self.stack.setCurrentWidget(self.create_database_widget)

    def save_password(self, data):
        # Krypter passordet
        encrypted_password = encrypt_password(data["password"], self.key)

        # Opprett PasswordEntry objekt
        entry = PasswordEntry(
            service=data["website"],
            email=data["email"],
            username=data["username"] if data["username"] else "",
            encrypted_password=encrypted_password,
            website=data["website"],
            link=data["link"] if data["link"] else "",
            tag=data["tag"] if data["tag"] else "",
        )

        # Legg til i databasen
        self.session.add(entry)
        self.session.commit()

    def is_database_setup(self):
        """
        Sjekk om databasen er satt opp ved å sjekke om session og key er satt.
        """
        return self.session is not None and self.key is not None

    def on_database_created(self):
        """
        Kalles når databasen er opprettet fra CreateDatabaseWidget.
        """
        # Sett key og session fra CreateDatabaseWidget
        self.key = self.create_database_widget.key
        self.session = self.create_database_widget.session

        # Instansier ShowPasswordWidget nå som session og key er satt
        self.show_password_widget = ShowPasswordWidget(self.session, self.key)
        self.stack.addWidget(self.show_password_widget)

        # Bytt til AddPasswordWidget
        self.stack.setCurrentWidget(self.add_password_widget)

    def view_passwords(self):
        pass

    def open_settings(self):
        # Bytt til settings_widget i stacken
        self.stack.setCurrentWidget(self.settings_widget)

    def apply_font_and_switch(self, font_settings):
        font_family, font_size = font_settings
        new_font = QFont(font_family, font_size)
        QApplication.instance().setFont(new_font)

        # Rekursivt sette font på alle widgets, inkludert statuslinjen
        self.set_font_recursively(self, new_font)

        # Oppdater kolonnebredder
        self.show_password_widget.update_column_widths()

    def switch_back(self):
        # Bytt tilbake til placeholder uten å endre font
        self.stack.setCurrentWidget(self.placeholder_widget)

    def apply_font(self, font_settings):
        font_family, font_size = font_settings
        new_font = QFont(font_family, font_size)
        QApplication.instance().setFont(new_font)
        self.set_font_recursively(self, new_font)

    def set_font_recursively(self, widget, font):
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            self.set_font_recursively(child, font)

    def update_column_widths(self):
        header = self.table.horizontalHeader()

        # Oppdater minimumsbredde for Brukernavn basert på header
        font_metrics = self.table.fontMetrics()
        header_text = "Brukernavn"
        min_width = font_metrics.horizontalAdvance(header_text) + 20
        self.table.setColumnWidth(2, max(150, min_width))

        # Passord (Kolonne 3) og Tag (Kolonne 5) har faste bredder
        self.table.setColumnWidth(3, 100)  # Passord
        self.table.setColumnWidth(5, 150)  # Tag

        # Oppdater kolonnebredder basert på innhold
        self.table.resizeColumnsToContents()

        # Juster kolonnene igjen for å sikre at Stretch fungerer som forventet
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
