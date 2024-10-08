from datetime import datetime
import os
import tempfile
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide2.QtCore import Qt, Signal

import styles
from data.encryption import encrypt_file, decrypt_file
from data.database import get_engine, create_tables, get_session
from data.models import PasswordEntry

from sqlalchemy.exc import SQLAlchemyError


class BackupWidget(QWidget):
    sync_completed = Signal(int)

    def __init__(self, user, db_path, encryption_key, session, parent=None):
        super().__init__(parent)

        self.user = user
        self.db_path = db_path
        self.encryption_key = encryption_key
        self.session = session

        # Sjekk at encryption_key er gyldig
        if not self.encryption_key:
            QMessageBox.critical(
                self,
                "Feil",
                "Krypteringsnøkkel er ikke initialisert.",
                QMessageBox.Ok,
            )
            self.close()
            return

        self.setStyleSheet("background-color: #fcd4a0;")
        self.setWindowTitle("Sikkerhetskopiering")

        # Opprett knapper
        self.create_backup_button = QPushButton("Sikkerhetskopier passord")
        self.synchronize_backup_button = QPushButton("Synkroniser database med backup")
        self.create_backup_button.setStyleSheet(styles.BUTTON_STYLE)
        self.synchronize_backup_button.setStyleSheet(styles.BUTTON_STYLE)
        self.create_backup_button.clicked.connect(self.backup_database)
        self.synchronize_backup_button.clicked.connect(self.synchronize_backup)

        # Sett opp layout
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.create_backup_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.synchronize_backup_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def backup_database(self):
        # Åpne en dialog for å velge backup mappe
        backup_dir = QFileDialog.getExistingDirectory(
            self,
            "Velg backup mappe",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if backup_dir:
            try:
                # Sjekk om databasefilen eksisterer
                if not os.path.exists(self.db_path):
                    QMessageBox.warning(
                        self,
                        "Fil Ikke Funnet",
                        f"Databasefilen ble ikke funnet:\n{self.db_path}",
                        QMessageBox.Ok,
                    )
                    return

                # Generer et backup-filnavn med tidsstempel
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"passwords_backup_{timestamp}.db"
                backup_path = os.path.join(backup_dir, backup_filename)

                # Opprett en midlertidig database med kun brukerens passord
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".db"
                ) as temp_db_file:
                    temp_db_path = temp_db_file.name

                temp_engine = get_engine(temp_db_path)
                create_tables(temp_engine)
                temp_session = get_session(temp_engine)

                # Kopier kun brukerens passord til den midlertidige databasen
                user_passwords = (
                    self.session.query(PasswordEntry)
                    .filter_by(user_id=self.user.id)
                    .all()
                )
                for entry in user_passwords:
                    new_entry = PasswordEntry(
                        service=entry.service,
                        email=entry.email,
                        username=entry.username,
                        encrypted_password=entry.encrypted_password,
                        link=entry.link,
                        tag=entry.tag,
                        user_id=entry.user_id,
                    )
                    temp_session.add(new_entry)
                temp_session.commit()

                # Krypter den midlertidige databasen og lagre den til backup_path
                encrypt_file(temp_db_path, self.encryption_key, backup_path)

                # Rydd opp den midlertidige databasen
                temp_session.close()
                temp_engine.dispose()
                os.remove(temp_db_path)

                # Informer brukeren om suksess
                QMessageBox.information(
                    self,
                    "Backup fullført",
                    f"Backup er lagret til:\n{backup_path}",
                    QMessageBox.Ok,
                )
            except Exception as e:
                # Informer brukeren om feil
                QMessageBox.critical(
                    self,
                    "Backup Feilet",
                    f"Kunne ikke sikkerhetskopiere databasen:\n{str(e)}",
                    QMessageBox.Ok,
                )

    def synchronize_backup(self):
        # Åpne en dialog for å velge backup fil
        backup_file, _ = QFileDialog.getOpenFileName(
            self,
            "Velg backup fil",
            "",
            "Encrypted Backup Files (*.db)",
            options=QFileDialog.ReadOnly,
        )
        if not backup_file:
            return  # Bruker avbrøt

        # Velg en midlertidig mappe for dekryptering
        with tempfile.TemporaryDirectory() as temp_dir:
            decrypted_backup_path = os.path.join(temp_dir, "decrypted_backup.db")
            try:
                # Dekrypter backup filen med riktig parameterrekkefølge
                decrypt_file(backup_file, self.encryption_key, decrypted_backup_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Dekryptering Feilet",
                    f"Kunne ikke dekryptere backup filen:\n{str(e)}",
                    QMessageBox.Ok,
                )
                return

            try:
                # Sett opp engine og session for backup databasen
                backup_engine = get_engine(decrypted_backup_path)
                create_tables(backup_engine)  # Sikre at tabellene finnes
                backup_session = get_session(backup_engine)

                # Hent alle passord fra backup (kun brukerens passord)
                backup_passwords = backup_session.query(PasswordEntry).all()

                if not backup_passwords:
                    QMessageBox.information(
                        self,
                        "Ingen Passord i Backup",
                        "Backup-databasen inneholder ingen passord.",
                        QMessageBox.Ok,
                    )
                    return

                # Hent alle passord fra nåværende database som tilhører brukeren
                current_passwords = (
                    self.session.query(PasswordEntry)
                    .filter_by(user_id=self.user.id)
                    .all()
                )

                # Lag en sett av unike identifikatorer for nåværende passord
                current_identifiers = set(
                    (p.service, p.email, p.username, p.link, p.tag)
                    for p in current_passwords
                )

                # Legg til passord fra backup som ikke finnes i nåværende database
                new_entries = []
                for entry in backup_passwords:
                    identifier = (
                        entry.service,
                        entry.email,
                        entry.username,
                        entry.link,
                        entry.tag,
                    )
                    if identifier not in current_identifiers:
                        new_entries.append(entry)

                if not new_entries:
                    QMessageBox.information(
                        self,
                        "Ingen Nye Passord",
                        "Backup-databasen inneholder ingen nye passord som ikke allerede er i den nåværende databasen.",
                        QMessageBox.Ok,
                    )
                    return

                # Legg til de nye passordene i den nåværende databasen
                for entry in new_entries:
                    # Kopier nødvendige felt
                    new_entry = PasswordEntry(
                        service=entry.service,
                        email=entry.email,
                        username=entry.username,
                        encrypted_password=entry.encrypted_password,
                        link=entry.link,
                        tag=entry.tag,
                        user_id=self.user.id,  # Knytt til den innloggede brukeren
                    )
                    self.session.add(new_entry)

                self.session.commit()

                # Emit signal med antall synkroniserte passord
                self.sync_completed.emit(len(new_entries))

                QMessageBox.information(
                    self,
                    "Synkronisering Fullført",
                    f"Synkroniserte {len(new_entries)} nye passord fra backup.",
                    QMessageBox.Ok,
                )

            except SQLAlchemyError as e:
                QMessageBox.critical(
                    self,
                    "Database Feil",
                    f"En feil oppstod under synkroniseringen:\n{str(e)}",
                    QMessageBox.Ok,
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Feil",
                    f"En uventet feil oppstod:\n{str(e)}",
                    QMessageBox.Ok,
                )
            finally:
                backup_session.close()
                backup_engine.dispose()
