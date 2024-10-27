import webbrowser
from PySide2.QtWidgets import (
    QWidget,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QApplication,
    QSizePolicy,
    QHeaderView,
)
from PySide2.QtCore import Signal, Qt

from data.models import PasswordEntry
from data.encryption import decrypt_password


class ShowPasswordWidget(QWidget):
    row_deleted = Signal()

    def __init__(self, session, key, user, main_window):
        super().__init__()

        self.session = session
        self.key = key
        self.user = user
        self.main_window = main_window

        self.setStyleSheet("background-color: #d1e8e2;")
        self.setWindowTitle("Vis Passord")

        # Opprett søkefelt
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Skriv inn for å søke...")
        self.search_input.textChanged.connect(self.filter_passwords)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.setAlignment(Qt.AlignTop)

        # Sett opp hovedlayout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        main_layout.addLayout(search_layout)

        self.setLayout(main_layout)

        # Sett opp tabellen
        self.setup_table()

        # Oppretter knapper
        self.copy_button = QPushButton("Kopier passord til utklippstavle")
        self.delete_button = QPushButton("Slett passord (rad)")
        self.go_to_web_button = QPushButton("Gå til nettsted og kopier passord")
        self.edit_button = QPushButton("Endre rad")
        self.copy_button.clicked.connect(self.copy_password)
        self.delete_button.clicked.connect(self.delete_row)
        self.go_to_web_button.clicked.connect(self.go_to_web)
        self.edit_button.clicked.connect(self.edit_row)

        # initialisere stiler og kobler mot theme changed i main window
        self.main_window.theme_changed.connect(self.init_ui_show_pw)
        self.init_ui_show_pw()

        # Opprett horisontal layout for knappene
        button_layout_1 = QHBoxLayout()
        # button_layout_1.addStretch()  # Skyver knappene til høyre
        button_layout_1.addWidget(self.copy_button)
        button_layout_1.addWidget(self.delete_button)
        # button_layout_1.addStretch()  # Skyver knappene til venstre og høyre

        # Opprett horisontal layout for den andre raden med knapper
        button_layout_2 = QHBoxLayout()
        # button_layout_2.addStretch()  # Skyver knappene til høyre
        button_layout_2.addWidget(self.go_to_web_button)
        button_layout_2.addWidget(self.edit_button)
        # button_layout_2.addStretch()  # Skyver knappene til venstre og høyre

        # Opprett en vertikal layout som holder begge radene
        button_layout = QVBoxLayout()
        button_layout.addLayout(button_layout_1)
        button_layout.addLayout(button_layout_2)

        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def init_ui_show_pw(self):
        self.main_window.style_manager.apply_line_edit_style(self.search_input)
        self.main_window.style_manager.apply_table_style(self.table)
        self.main_window.style_manager.apply_button_style_1(self.copy_button)
        self.main_window.style_manager.apply_button_style_1(self.go_to_web_button)
        self.main_window.style_manager.apply_button_style_1(self.edit_button)
        self.main_window.style_manager.apply_button_style_2(self.delete_button)

        self.setStyleSheet(
            f"background-color: {self.main_window.style_manager.theme['background']};"
        )

    def setup_table(self):
        # Opprett tabell
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Tjeneste", "E-post", "Brukernavn", "Passord", "Link", "Emne"]
        )

        header = self.table.horizontalHeader()

        # Sett resize mode for hver kolonne
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Tjeneste
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # E-post
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Brukernavn
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Passord
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Link
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Emne

        # Sett minimum bredde for "Brukernavn"
        self.table.setColumnWidth(2, 150)  # Brukernavn

        # Sett maksimum bredde for "Passord" og "Tag"
        self.table.setColumnWidth(3, 170)  # Passord
        self.table.setColumnWidth(5, 120)  # Emne

        # Sett sizePolicy for å fylle plassen dynamisk
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Sett en standard radhøyde
        self.table.verticalHeader().setDefaultSectionSize(60)

        # Tillat valg av celler, ikke bare rader
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.view_password)

        # Legg til tabellen i layouten
        main_layout = self.layout()
        main_layout.addWidget(self.table)
        main_layout.addStretch()

    def load_passwords(self):
        self.table.setRowCount(0)  # Tøm tabellen først
        # Filtrer passordene til den innloggede brukeren
        passwords = (
            self.session.query(PasswordEntry).filter_by(user_id=self.user.id).all()
        )
        if not passwords:
            QMessageBox.information(
                self,
                "Ingen Passord",
                "Ingen passord er lagret i databasen.",
                QMessageBox.Ok,
            )
            return  # Avslutt funksjonen tidlig hvis ingen passord finnes
        for entry in passwords:
            try:
                decrypted_service = decrypt_password(entry.service, self.key["service"])
                decrypted_email = decrypt_password(entry.email, self.key["email"])
                decrypted_username = decrypt_password(
                    entry.username, self.key["username"]
                )
                decrypted_link = decrypt_password(entry.link, self.key["link"])
                decrypted_tag = decrypt_password(entry.tag, self.key["tag"])

                self.add_table_row(
                    {
                        "id": entry.id,
                        "service": decrypted_service,
                        "email": decrypted_email,
                        "username": decrypted_username,
                        "link": decrypted_link,
                        "tag": decrypted_tag,
                    }
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Feil", f"Kunne ikke dekryptere passord: {str(e)}"
                )

        # Etter radene er lagt til, juster høyden på tabellen basert på antall rader
        row_count = self.table.rowCount()
        row_height = self.table.verticalHeader().defaultSectionSize()
        header_height = self.table.horizontalHeader().height()
        total_height = row_count * row_height + header_height + 2  # Juster for marginer

        # Sett tabellens høyde basert på antall rader
        self.table.setMinimumHeight(total_height)
        self.table.setMaximumHeight(total_height)

    def add_table_row(self, entry):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Liste over feltene
        columns = ["service", "email", "username", "*", "link", "tag"]
        for col_index, field in enumerate(columns):
            if field == "*":
                item = QTableWidgetItem("*" * 4)  # Placeholder for passord
            else:
                item = QTableWidgetItem(entry[field])

            # Lagre entry.id i den første cellen
            if col_index == 0:
                item.setData(Qt.UserRole, entry["id"])

            self.table.setItem(row_position, col_index, item)

    def filter_passwords(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def view_password(self, row, column):
        try:
            # Hvis brukeren dobbeltklikker på passord-kolonnen (kolonne 3)
            if column == 3:
                service_item = self.table.item(row, 0)
                entry_id = service_item.data(Qt.UserRole)
                entry = self.session.query(PasswordEntry).filter_by(id=entry_id).first()

                if entry:
                    # Dekrypter passordet
                    decrypted_password = decrypt_password(
                        entry.encrypted_password, self.key["password"]
                    )

                    # Kopier det dekrypterte passordet til utklippstavlen
                    QApplication.clipboard().setText(decrypted_password)
                    copied_text = QApplication.clipboard().text()

                    # Vis en melding om at passordet er kopiert
                    QMessageBox.information(
                        self,
                        "Kopiert",
                        f"Passordet er kopiert til utklippstavlen.",
                    )
                else:
                    QMessageBox.warning(
                        self, "Feil", "Passordet ble ikke funnet i databasen."
                    )
            else:
                # For alle andre kolonner, kopier innholdet som det er
                cell_text = self.table.item(row, column).text()
                QApplication.clipboard().setText(cell_text)
                copied_text = QApplication.clipboard().text()

                # Vis en melding om at tekst er kopiert
                QMessageBox.information(
                    self,
                    "Kopiert",
                    f"Teksten '{copied_text}' er kopiert til utklippstavlen.",
                )
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke kopiere tekst: {str(e)}")

    def copy_password(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Ingen Valgt", "Vennligst velg et passord fra tabellen."
            )
            return

        row = selected_items[0].row()
        service_item = self.table.item(row, 0)
        entry_id = service_item.data(Qt.UserRole)
        try:
            entry = self.session.query(PasswordEntry).filter_by(id=entry_id).first()
            if entry:
                decrypted_password = decrypt_password(
                    entry.encrypted_password, self.key["password"]
                )
                QApplication.clipboard().setText(decrypted_password)
                copied_text = QApplication.clipboard().text()
                QMessageBox.information(
                    self, "Kopiert", "Passordet er kopiert til utklippstavlen."
                )
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke kopiere passord: {str(e)}")

    def delete_row(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Ingen Valgt", "Vennligst velg et passord fra tabellen."
            )
            return

        # Hent raden og entry_id fra tabellen
        row = selected_items[0].row()
        entry_id = self.table.item(row, 0).data(Qt.UserRole)
        service = self.table.item(row, 0).text()

        # Bekreft sletting
        reply = QMessageBox.question(
            self,
            "Bekreft Sletting",
            f"Er du sikker på at du vil slette passordet for tjeneste '{service}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                entry = self.session.query(PasswordEntry).get(entry_id)
                if entry:
                    self.session.delete(entry)
                    self.session.commit()
                    self.table.removeRow(row)
                    self.row_deleted.emit()
                else:
                    QMessageBox.warning(
                        self, "Ikke Funnet", "Passordet ble ikke funnet i databasen."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Feil", f"Kunne ikke slette passordet: {str(e)}"
                )

    def edit_row(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Ingen Valgt", "Vennligst velg et passord fra tabellen."
            )
            return

        # Hent raden som er valgt
        row = selected_items[0].row()
        service_item = self.table.item(row, 0)
        entry_id = service_item.data(Qt.UserRole)

        try:
            entry = self.session.query(PasswordEntry).filter_by(id=entry_id).first()
            if entry:
                # Dekrypter feltene
                decrypted_service = decrypt_password(entry.service, self.key["service"])
                decrypted_email = decrypt_password(entry.email, self.key["email"])
                decrypted_username = decrypt_password(
                    entry.username, self.key["username"]
                )
                decrypted_password = decrypt_password(
                    entry.encrypted_password, self.key["password"]
                )
                decrypted_link = decrypt_password(entry.link, self.key["link"])
                decrypted_tag = decrypt_password(entry.tag, self.key["tag"])

                # Sett dataene i redigeringswidgeten (AddPasswordWidget eller liknende)
                password_data = {
                    "service": decrypted_service,
                    "email": decrypted_email,
                    "username": decrypted_username,
                    "password": decrypted_password,
                    "link": decrypted_link,
                    "tag": decrypted_tag,
                }
                self.main_window.show_add_password_widget()
                self.main_window.add_password_widget.fill_fields(
                    password_data, entry_id
                )
            else:
                QMessageBox.warning(
                    self, "Ikke Funnet", "Passordet ble ikke funnet i databasen."
                )
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke hente passordet: {str(e)}")

    def go_to_web(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Ingen Valgt", "Vennligst velg et passord fra tabellen."
            )
            return

        # Hent raden som er valgt
        row = selected_items[0].row()

        # Hent data fra den nødvendige kolonnen
        link = self.table.item(row, 4).text()

        # Sjekk at linken ikke er tom
        if not link:
            QMessageBox.warning(
                self, "Ingen Link", "Ingen link er lagret for denne tjenesten."
            )
            return

        # Kopier passord
        self.copy_password()

        # Åpne link i standard nettleser
        try:
            webbrowser.open(link)
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke åpne nettleser: {str(e)}")
