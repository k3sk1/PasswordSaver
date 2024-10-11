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
from PySide2.QtCore import Signal

from data.models import PasswordEntry
from data.encryption import decrypt_password
import styles


class ShowPasswordWidget(QWidget):
    row_deleted = Signal()

    def __init__(self, session, key, user):
        super().__init__()

        self.session = session
        self.key = key
        self.user = user

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
        self.copy_button.setStyleSheet(styles.BUTTON_STYLE)
        self.delete_button.setStyleSheet(styles.BUTTON_STYLE2)
        self.go_to_web_button.setStyleSheet(styles.BUTTON_STYLE)
        self.copy_button.clicked.connect(self.copy_password)
        self.delete_button.clicked.connect(self.delete_row)
        self.go_to_web_button.clicked.connect(self.go_to_web)

        # Opprett horisontal layout for knappene
        button_layout_1 = QHBoxLayout()
        button_layout_1.addStretch()  # Skyver knappene til høyre (valgfritt)
        button_layout_1.addWidget(self.copy_button)
        button_layout_1.addWidget(self.delete_button)
        button_layout_1.addStretch()  # Skyver knappene til venstre og høyre (valgfritt)

        # Opprett horisontal layout for den andre raden med knapper
        button_layout_2 = QHBoxLayout()
        button_layout_2.addStretch()  # Skyver knappene til høyre (valgfritt)
        button_layout_2.addWidget(self.go_to_web_button)  # Legger til en ny knapp
        button_layout_2.addStretch()  # Skyver knappene til venstre og høyre (valgfritt)

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
            self.add_table_row(entry)

    def add_table_row(self, entry):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Opprett og sett inn QTableWidgetItem for hver kolonne
        self.table.setItem(row_position, 0, QTableWidgetItem(entry.service))
        self.table.setItem(row_position, 1, QTableWidgetItem(entry.email))
        self.table.setItem(row_position, 2, QTableWidgetItem(entry.username))
        # For passordet, vis stjerner eller kryptert tekst
        self.table.setItem(row_position, 3, QTableWidgetItem("*" * 4))  # Placeholder
        self.table.setItem(row_position, 4, QTableWidgetItem(entry.link))
        self.table.setItem(row_position, 5, QTableWidgetItem(entry.tag))

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
                decrypted_password = decrypt_password(
                    entry.encrypted_password, self.key
                )
                QMessageBox.information(
                    self,
                    "Passord Detaljer",
                    f"Tjeneste: {entry.service}\n"
                    f"E-post: {entry.email}\n"
                    f"Brukernavn: {entry.username}\n"
                    f"Passord: {decrypted_password}\n"
                    f"Link: {entry.link}\n"
                    f"Tag: {entry.tag}",
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
        service = self.table.item(row, 0).text()
        email = self.table.item(row, 1).text()
        username = self.table.item(row, 2).text()
        link = self.table.item(row, 4).text()
        tag = self.table.item(row, 5).text()

        try:
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
                decrypted_password = decrypt_password(
                    entry.encrypted_password, self.key
                )
                QApplication.clipboard().setText(decrypted_password)
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

        # Hent raden som er valgt
        row = selected_items[0].row()

        # Hent data fra de nødvendige kolonnene
        service = self.table.item(row, 0).text()
        email = self.table.item(row, 1).text()
        username = self.table.item(row, 2).text()
        link = self.table.item(row, 4).text()
        tag = self.table.item(row, 5).text()

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
                # Finn det aktuelle PasswordEntry-objektet i databasen
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
