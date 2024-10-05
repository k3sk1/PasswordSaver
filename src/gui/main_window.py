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
from gui.placeholder_widget import PlaceholderWidget
from gui.settings_widget import SettingsWidget
from gui.show_password_widget import ShowPasswordWidget
from gui.backup_widget import BackupWidget
import styles

from data.encryption import derive_key, encrypt_password, decrypt_password
from data.database import get_engine, create_tables, get_session
from data.models import PasswordEntry

import os
import json
import base64
import sys


class MainWindow(QMainWindow):
    def __init__(self, key, session):
        super().__init__()

        self.setWindowTitle("Password Saver")
        # Sett en fast størrelse på vinduet
        self.resize(1100, 800)

        # Få den absolutte stien til 'data' mappen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "..", "data")
        salt_file = os.path.join(data_dir, "salt.json")
        self.db_path = os.path.join(data_dir, "passwords.db")

        # Initialize key and session
        self.key = key
        self.session = session

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
        self.show_password_widget = ShowPasswordWidget(self.session, self.key)
        self.backup_widget = BackupWidget(self.db_path, self.key, self.session)
        self.settings_widget = SettingsWidget(
            current_font_family=self.font().family(),
            current_font_size=self.font().pointSize(),
        )

        # Kobler signaler
        self.settings_widget.settings_changed.connect(self.apply_font_and_switch)
        self.settings_widget.settings_cancelled.connect(self.switch_back)
        self.add_password_widget.password_saved.connect(self.save_password)
        self.backup_widget.sync_completed.connect(self.update_button_states)
        self.show_password_widget.row_deleted.connect(self.update_button_states)

        # Legg widgets til stacken
        self.stack.addWidget(self.placeholder_widget)  # Indeks 0
        self.stack.addWidget(self.add_password_widget)  # Indeks 1
        self.stack.addWidget(self.show_password_widget)  # Indeks 2
        self.stack.addWidget(self.backup_widget)  # Indeks 3
        self.stack.addWidget(self.settings_widget)  # Indeks 4

        # Skjul alle widgets ved oppstart
        self.stack.setCurrentWidget(self.placeholder_widget)

        # Sett global font
        self.apply_font((self.font().family(), self.font().pointSize()))

        # Sjekk antall passord og oppdater knappene
        self.update_button_states()

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
        backup_button = QPushButton("Sikkerhetskopiering")
        settings_button = QPushButton("Innstillinger")

        # Koble knappene til funksjoner
        add_password_button.clicked.connect(self.show_add_password_widget)
        view_password_button.clicked.connect(self.show_show_password_widget)
        backup_button.clicked.connect(self.show_backup_widget)
        settings_button.clicked.connect(self.open_settings)

        # Lagre referansene som instansvariabler
        self.view_password_button = view_password_button
        self.backup_button = backup_button

        # Legg knappene til i layouten
        side_layout.addWidget(add_password_button)
        side_layout.addWidget(view_password_button)
        side_layout.addWidget(backup_button)
        side_layout.addWidget(settings_button)

        # Legg til sidepanelet i hovedlayouten
        main_layout.addWidget(side_panel)

    def update_button_states(self):
        try:
            password_count = self.session.query(PasswordEntry).count()
            if password_count > 0:
                self.view_password_button.setEnabled(True)
                self.backup_button.setEnabled(True)
            else:
                self.view_password_button.setEnabled(False)
                # self.backup_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Feil",
                f"Kunne ikke sjekke passordene: {str(e)}",
                QMessageBox.Ok,
            )
            self.view_password_button.setEnabled(False)
            # self.backup_button.setEnabled(False)

    def show_add_password_widget(self):
        self.stack.setCurrentWidget(self.add_password_widget)

    def show_show_password_widget(self):
        # Last inn passordene når widgeten skal vises
        self.show_password_widget.load_passwords()
        self.stack.setCurrentWidget(self.show_password_widget)

    def show_backup_widget(self):
        if not hasattr(self, "backup_widget"):
            # Instansier ShowPasswordWidget hvis den ikke allerede er instansiert
            self.backup_widget = BackupWidget(self.db_path, self.key)
            self.stack.addWidget(self.backup_widget)
        else:
            self.stack.setCurrentWidget(self.backup_widget)

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

        # Oppdater knappene
        self.update_button_states()

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
