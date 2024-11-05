import random
from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QToolButton,
    QButtonGroup,
    QMessageBox,
    QFormLayout,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide2.QtCore import Qt, Signal

from data.encryption import encrypt_password
from data.models import PasswordEntry


class AddPasswordWidget(QWidget):
    # Definer en signal som emitteres når passordet er lagret
    password_saved = Signal(dict)

    def __init__(self, user, session, key, main_window, parent=None):
        super().__init__(parent)

        self.user = user
        self.session = session
        self.key = key
        self.main_window = main_window
        self.entry_id = None

        self.setWindowTitle("Legg til passord")

        # Opprett etiketter og inngangsfelt
        self.email_label = QLabel("E-mail")
        self.email_input = QLineEdit()
        self.email_input.setTextMargins(5, 0, 0, 0)
        self.email_input.setPlaceholderText("ola_nordmann@gmail.com")

        self.username_label = QLabel("Brukernavn (valgfri)")
        self.username_input = QLineEdit()
        self.username_input.setTextMargins(5, 0, 0, 0)
        self.username_input.setPlaceholderText("Brukernavn")

        self.password_label = QLabel("Passord")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setTextMargins(5, 0, 0, 0)
        self.password_input.setPlaceholderText("Passord")

        # Vis/skjul passord knapp
        self.toggle_password_button = QToolButton()
        self.toggle_password_button.setText("\U0001F576")  # solbrille symbol
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)

        # Juster høyden til vis/skjul passord knappen dynamisk etter passord input feltet
        self.toggle_password_button.setFixedSize(
            self.password_input.height(), self.password_input.height()
        )

        # Lag en horisontal layout for passordfeltet og sjekkboksen
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)

        self.service_label = QLabel("Tjeneste")
        self.service_input = QLineEdit()
        self.service_input.setTextMargins(5, 0, 0, 0)
        self.service_input.setPlaceholderText("Google")

        self.link_label = QLabel("Link til nettside")
        self.link_input = QLineEdit()
        self.link_input.setTextMargins(5, 0, 0, 0)
        self.link_input.setPlaceholderText(
            "https://www.eksempel.com eller www.eksempel.com "
        )

        self.tag_label = QLabel("Emneknagg (valgfri)")
        self.tag_input = QLineEdit()
        self.tag_input.setTextMargins(5, 0, 0, 0)
        self.tag_input.setPlaceholderText("Arbeid")

        # buttons
        self.save_button = QPushButton("Lagre")
        self.generate_passw_button = QPushButton("Lag passord")
        self.save_button.setFixedWidth(150)
        self.save_button.clicked.connect(self.save_password)
        self.generate_passw_button.clicked.connect(self.generate_password)

        # Radioknapper for passordstyrke
        self.low_strength_button = QPushButton("Lav")
        self.medium_strength_button = QPushButton("Medium")
        self.high_strength_button = QPushButton("Høy")
        self.low_strength_button.setCheckable(True)
        self.medium_strength_button.setCheckable(True)
        self.high_strength_button.setCheckable(True)
        self.medium_strength_button.setChecked(True)  # Medium er standard

        self.main_window.theme_changed.connect(self.init_ui_add_pw)

        self.init_ui_add_pw()

        # Gruppér styrkeknappene
        self.strength_group = QButtonGroup()
        self.strength_group.addButton(self.low_strength_button)
        self.strength_group.addButton(self.medium_strength_button)
        self.strength_group.addButton(self.high_strength_button)

        # Legg til styrkeknappene i en horisontal layout ved siden av "Lag passord"-knappen
        strength_layout = QHBoxLayout()
        strength_layout.addWidget(self.generate_passw_button)
        strength_layout.addWidget(self.low_strength_button)
        strength_layout.addWidget(self.medium_strength_button)
        strength_layout.addWidget(self.high_strength_button)

        # Opprett en QFormLayout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setSpacing(20)
        form_layout.setHorizontalSpacing(30)

        # Legg til feltene i form_layout
        form_layout.addRow(self.email_label, self.email_input)
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, password_layout)
        form_layout.addRow(self.service_label, self.service_input)
        form_layout.addRow(self.link_label, self.link_input)
        form_layout.addRow(self.tag_label, self.tag_input)

        # Opprett hovedlayouten
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(30)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(strength_layout)
        main_layout.addWidget(self.generate_passw_button, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def init_ui_add_pw(self):
        # Bruk style_manager til å sette stiler på widgets
        self.main_window.style_manager.apply_label_style(self.email_label)
        self.main_window.style_manager.apply_label_style(self.username_label)
        self.main_window.style_manager.apply_label_style(self.password_label)
        self.main_window.style_manager.apply_label_style(self.service_label)
        self.main_window.style_manager.apply_label_style(self.link_label)
        self.main_window.style_manager.apply_label_style(self.tag_label)
        self.main_window.style_manager.apply_button_style_1(self.generate_passw_button)
        self.main_window.style_manager.apply_button_style_1(self.save_button)
        self.main_window.style_manager.apply_button_style_circle(
            self.toggle_password_button
        )
        self.main_window.style_manager.apply_line_edit_style(self.email_input)
        self.main_window.style_manager.apply_line_edit_style(self.username_input)
        self.main_window.style_manager.apply_line_edit_style(self.password_input)
        self.main_window.style_manager.apply_line_edit_style(self.service_input)
        self.main_window.style_manager.apply_line_edit_style(self.link_input)
        self.main_window.style_manager.apply_line_edit_style(self.tag_input)
        self.main_window.style_manager.apply_button_style_strength_1(
            self.low_strength_button
        )
        self.main_window.style_manager.apply_button_style_strength_2(
            self.medium_strength_button
        )
        self.main_window.style_manager.apply_button_style_strength_3(
            self.high_strength_button
        )

    def save_password(self):
        # Hent data fra feltene
        data = self.get_data()

        # Validering av nødvendige felt
        if not data["service"] or not data["email"] or not data["password"]:
            QMessageBox.warning(
                self, "Feil", "Vennligst fyll ut alle obligatoriske felt."
            )
            return

        try:
            # Krypter hver relevant kolonne
            encrypted_service = encrypt_password(data["service"], self.key["service"])
            encrypted_email = encrypt_password(data["email"], self.key["email"])
            encrypted_username = encrypt_password(
                data["username"], self.key["username"]
            )
            encrypted_password = encrypt_password(
                data["password"], self.key["password"]
            )
            encrypted_link = encrypt_password(data["link"], self.key["link"])
            encrypted_tag = encrypt_password(data["tag"], self.key["tag"])

            if self.entry_id:
                # Oppdater eksisterende oppføring
                entry = self.session.query(PasswordEntry).get(self.entry_id)
                if entry:
                    entry.service = encrypted_service
                    entry.email = encrypted_email
                    entry.username = encrypted_username
                    entry.encrypted_password = encrypted_password
                    entry.link = encrypted_link
                    entry.tag = encrypted_tag
                    self.session.commit()
                    self.main_window.show_show_password_widget()
                else:
                    QMessageBox.warning(self, "Feil", "Kunne ikke finne oppføringen.")
            else:
                # Opprett ny oppføring
                entry = PasswordEntry(
                    service=encrypted_service,
                    email=encrypted_email,
                    username=encrypted_username,
                    encrypted_password=encrypted_password,
                    link=encrypted_link,
                    tag=encrypted_tag,
                    user_id=self.user.id,
                )
                self.session.add(entry)
                self.session.commit()

            # Emit signal med data inkludert bruker_id
            data["user_id"] = self.user.id
            self.password_saved.emit(data)

            # Tøm feltene etter lagring
            self.clear_fields()
            self.entry_id = None  # Tilbakestill entry_id etter oppdatering/lagring

        except Exception as e:
            QMessageBox.critical(
                self,
                "Feil",
                f"Kunne ikke lagre passordet: {str(e)}",
                QMessageBox.Ok,
            )

    def generate_password(self):
        # Bestem passordstyrke basert på valgt radioknapp
        if self.high_strength_button.isChecked():
            length = 18
        elif self.medium_strength_button.isChecked():
            length = 12
        else:  # Lav styrke
            length = 6

        # Liste med korte og lengre ord
        ordliste = [
            "sol",
            "måne",
            "blomst",
            "fjell",
            "skog",
            "hav",
            "hund",
            "katt",
            "vann",
            "ild",
            "vind",
            "snø",
            "fugl",
            "tre",
            "stein",
            "himmel",
            "natt",
            "dag",
            "blå",
            "rød",
            "grønn",
            "gul",
            "sky",
            "gull",
            "lys",
            "regn",
            "is",
            "fisk",
            "båt",
            "vei",
            "lys",
            "mørke",
            "tid",
            "fred",
            "kaffe",
            "te",
            "bro",
            "tårn",
            "kyst",
            "sjø",
            "solskinn",
            "fjelltopp",
        ]

        # Velg 18 tilfeldige ord fra listen
        passord_ord = random.choices(ordliste, k=length)

        # Sett sammen ordene med en bindestrek
        passord = "-".join(passord_ord)

        # Skriv passordet inn i passordfeltet automatisk
        self.password_input.setText(passord)

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

    def fill_fields(self, data, entry_id=None):
        """Fyll inn feltene med data, og oppdater entry_id hvis vi redigerer."""
        self.entry_id = entry_id
        self.service_input.setText(data.get("service", ""))
        self.email_input.setText(data.get("email", ""))
        self.username_input.setText(data.get("username", ""))
        self.password_input.setText(data.get("password", ""))
        self.link_input.setText(data.get("link", ""))
        self.tag_input.setText(data.get("tag", ""))

    def toggle_password_visibility(self):
        """Vis eller skjul passordet basert på knappen sin tilstand."""
        if self.toggle_password_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setText("\U0001F441")  # Åpent øye-symbol
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setText("\U0001F576")  # Lukket øye-symbol
