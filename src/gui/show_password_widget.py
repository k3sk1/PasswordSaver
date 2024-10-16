import webbrowser
from PySide2.QtWidgets import (
    QWidget,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QLabel,
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
import styles


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
        self.search_label = QLabel("Søk:")
        self.search_label.setStyleSheet(styles.LABEL_STYLE)
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(styles.LINE_EDIT_STYLE)
        self.search_input.setPlaceholderText("Skriv inn for å søke...")
        self.search_input.textChanged.connect(self.filter_passwords)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)

        # Sett opp hovedlayout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.addLayout(search_layout)

        self.setLayout(main_layout)

        # Sett opp tabellen
        self.setup_table()

        # Oppretter knapper
        self.copy_button = QPushButton("Kopier passord til utklippstavle")
        self.delete_button = QPushButton("Slett passord (rad)")
        self.go_to_web_button = QPushButton("Gå til nettsted og kopier passord")
        self.edit_button = QPushButton("Endre rad")
        self.copy_button.setStyleSheet(styles.BUTTON_STYLE)
        self.delete_button.setStyleSheet(styles.BUTTON_STYLE2)
        self.go_to_web_button.setStyleSheet(styles.BUTTON_STYLE)
        self.edit_button.setStyleSheet(styles.BUTTON_STYLE)
        self.copy_button.clicked.connect(self.copy_password)
        self.delete_button.clicked.connect(self.delete_row)
        self.go_to_web_button.clicked.connect(self.go_to_web)
        self.edit_button.clicked.connect(self.edit_row)

        # Opprett horisontal layout for knappene
        button_layout_1 = QHBoxLayout()
        button_layout_1.addStretch()  # Skyver knappene til høyre
        button_layout_1.addWidget(self.copy_button)
        button_layout_1.addWidget(self.delete_button)
        button_layout_1.addStretch()  # Skyver knappene til venstre og høyre

        # Opprett horisontal layout for den andre raden med knapper
        button_layout_2 = QHBoxLayout()
        button_layout_2.addStretch()  # Skyver knappene til høyre
        button_layout_2.addWidget(self.go_to_web_button)
        button_layout_2.addWidget(self.edit_button)
        button_layout_2.addStretch()  # Skyver knappene til venstre og høyre

        # Opprett en vertikal layout som holder begge radene
        button_layout = QVBoxLayout()
        button_layout.addLayout(button_layout_1)
        button_layout.addLayout(button_layout_2)

        main_layout.addLayout(button_layout)

    def setup_table(self):
        # Opprett tabell
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Tjeneste", "E-post", "Brukernavn", "Passord", "Link", "Tag"]
        )

        header = self.table.horizontalHeader()

        # Sett resize mode for hver kolonne
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Tjeneste
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # E-post
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Brukernavn
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # Passord
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Link
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Tag

        # Sett minimum bredde for "Brukernavn"
        self.table.setColumnWidth(2, 150)  # Brukernavn

        # Sett maksimum bredde for "Passord" og "Tag"
        self.table.setColumnWidth(3, 120)  # Passord
        self.table.setColumnWidth(5, 120)  # Tag

        # Sett sizePolicy for å fylle plassen dynamisk
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.cellDoubleClicked.connect(self.view_password)

        # Legg til tabellen i layouten
        main_layout = self.layout()
        main_layout.addWidget(self.table)

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

    def add_table_row(self, entry):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Opprett og sett inn QTableWidgetItem for hver kolonne
        service_item = QTableWidgetItem(entry["service"])
        email_item = QTableWidgetItem(entry["email"])
        username_item = QTableWidgetItem(entry["username"])
        link_item = QTableWidgetItem(entry["link"])
        tag_item = QTableWidgetItem(entry["tag"])

        # Lagre entry.id i hver QTableWidgetItem
        service_item.setData(Qt.UserRole, entry["id"])

        self.table.setItem(row_position, 0, service_item)
        self.table.setItem(row_position, 1, email_item)
        self.table.setItem(row_position, 2, username_item)
        # For passordet, vis stjerner eller kryptert tekst
        self.table.setItem(row_position, 3, QTableWidgetItem("*" * 4))  # Placeholder
        self.table.setItem(row_position, 4, link_item)
        self.table.setItem(row_position, 5, tag_item)

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
            # Hent PasswordEntry fra databasen basert på row og user_id
            service = self.table.item(row, 0).text()
            email = self.table.item(row, 1).text()
            username = self.table.item(row, 2).text()
            link = self.table.item(row, 4).text()
            tag = self.table.item(row, 5).text()

            entry = (
                self.session.query(PasswordEntry)
                .filter_by(
                    service=service,
                    email=email,
                    username=username,
                    link=link,
                    tag=tag,
                    user_id=self.user.id,  # Sikre at det tilhører riktig bruker
                )
                .first()
            )

            if entry:
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

                QMessageBox.information(
                    self,
                    "Passord Detaljer",
                    f"Tjeneste: {decrypted_service}\n"
                    f"E-post: {decrypted_email}\n"
                    f"Brukernavn: {decrypted_username}\n"
                    f"Passord: {decrypted_password}\n"
                    f"Link: {decrypted_link}\n"
                    f"Tag: {decrypted_tag}",
                    QMessageBox.Ok,
                )
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke vise passord: {str(e)}")

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
            print(f"entry: {entry}")
            if entry:
                decrypted_password = decrypt_password(
                    entry.encrypted_password, self.key["password"]
                )
                # Debugging: Se om vi får det dekrypterte passordet
                print("Decrypted password:", decrypted_password)
                QApplication.clipboard().setText(decrypted_password)
                copied_text = QApplication.clipboard().text()
                print("Copied to clipboard:", copied_text)
                QMessageBox.information(
                    self, "Kopiert", "Passordet er kopiert til utklippstavlen."
                )
        except Exception as e:
            print("Entry not found in the database.")
            QMessageBox.critical(self, "Feil", f"Kunne ikke kopiere passord: {str(e)}")

    def delete_row(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Ingen Valgt", "Vennligst velg et passord fra tabellen."
            )
            return

        # Hent raden som er valgt
        row = selected_items[0].row()

        # Hent ID-en fra tabellen (lagret i UserRole)
        service_item = self.table.item(row, 0)
        entry_id = service_item.data(Qt.UserRole)

        # Hent tjeneste navnet for visning i bekreftelsesmeldingen
        service = service_item.text()

        # Bekreft med brukeren før sletting
        reply = QMessageBox.question(
            self,
            "Bekreft Sletting",
            f"Er du sikker på at du vil slette passordet for tjeneste '{service}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                # Finn det aktuelle PasswordEntry-objektet i databasen basert på ID
                entry = self.session.query(PasswordEntry).filter_by(id=entry_id).first()

                if entry:
                    # Slett objektet fra databasen
                    self.session.delete(entry)
                    self.session.commit()

                    # Fjern raden fra tabellen
                    self.table.removeRow(row)

                    # Emit signal for å oppdatere knappestatusene
                    self.row_deleted.emit()
                else:
                    QMessageBox.warning(
                        self,
                        "Ikke Funnet",
                        "Passordet ble ikke funnet i databasen.",
                        QMessageBox.Ok,
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Feil",
                    f"Kunne ikke slette passordet: {str(e)}",
                    QMessageBox.Ok,
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

        # Hent data fra de nødvendige kolonnene
        service = self.table.item(row, 0).text()
        email = self.table.item(row, 1).text()
        username = self.table.item(row, 2).text()
        link = self.table.item(row, 4).text()
        tag = self.table.item(row, 5).text()

        # Hent passordet fra databasen (dekryptert)
        try:
            entry = (
                self.session.query(PasswordEntry)
                .filter_by(
                    service=service,
                    email=email,
                    username=username,
                    link=link,
                    tag=tag,
                    user_id=self.user.id,
                )
                .first()
            )

            if entry:
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

                # Bytt til AddPasswordWidget og fyll inn data
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
                    password_data, entry.id
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
