from datetime import datetime
import os
import shutil
import tempfile
import traceback
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide2.QtCore import Qt, Signal

import styles
from data.encryption import decrypt_password
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
                backup_path = os.path.normpath(
                    os.path.join(backup_dir, backup_filename)
                )

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

                # Lagre databasen som backup
                shutil.copy2(temp_db_path, backup_path)

                # Rydd opp den midlertidige databasen
                temp_session.close()
                temp_engine.dispose()
                os.remove(temp_db_path)

                # Informer brukeren om suksess
                QMessageBox.information(
                    self,
                    "Backup Fullført",
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
                # les inn kryptert tabell uten å dekryptere
                shutil.copy2(backup_file, decrypted_backup_path)
                print(f"Kopiert backup-fil til {decrypted_backup_path}")
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
                backup_session = get_session(backup_engine)
                print("Backup engine og session er satt opp.")

                # Hent alle passordoppføringer fra backup
                backup_passwords = backup_session.query(PasswordEntry).all()
                print("Hentet alle passordoppføringer fra backup.")
                if not backup_passwords:
                    QMessageBox.information(
                        self,
                        "Ingen Passord i Backup",
                        "Backup-databasen inneholder ingen passord.",
                        QMessageBox.Ok,
                    )
                    return

                # Hent alle passordoppføringer fra current db
                current_passwords = (
                    self.session.query(PasswordEntry)
                    .filter_by(user_id=self.user.id)
                    .all()
                )
                print(
                    f"Hentet alle passordoppføringer fra brukeren med id: {self.user.id}"
                )

                # Lag en sett av unike identifikatorer for nåværende passord
                current_identifiers = set(
                    (
                        decrypt_password(p.service, self.encryption_key["service"]),
                        decrypt_password(p.email, self.encryption_key["email"]),
                        decrypt_password(p.username, self.encryption_key["username"]),
                        decrypt_password(p.link, self.encryption_key["link"]),
                        decrypt_password(p.tag, self.encryption_key["tag"]),
                    )
                    for p in current_passwords
                )
                print(
                    "Opprettet sett av unike identifikatorer for eksisterende passord."
                )

                # Legg til passord fra backup som ikke finnes i nåværende database
                new_entries = []
                for entry in backup_passwords:
                    try:
                        identifier = (
                            decrypt_password(
                                entry.service, self.encryption_key["service"]
                            ),
                            decrypt_password(entry.email, self.encryption_key["email"]),
                            decrypt_password(
                                entry.username, self.encryption_key["username"]
                            ),
                            decrypt_password(entry.link, self.encryption_key["link"]),
                            decrypt_password(entry.tag, self.encryption_key["tag"]),
                        )
                        print(f"Identifier successfully decrypted: {identifier}")
                        if identifier not in current_identifiers:
                            new_entries.append(entry)
                    except Exception as e:
                        print(f"Error decrypting entry {entry.service}: {str(e)}")
                        traceback.print_exc()

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
                    try:
                        print(
                            f"Adding entry: {entry.service}, {entry.email}, {entry.username}, {entry.link}, {entry.tag}"
                        )
                        new_entry = PasswordEntry(
                            service=entry.service,
                            email=entry.email,
                            username=entry.username,
                            encrypted_password=entry.encrypted_password,
                            link=entry.link,
                            tag=entry.tag,
                            user_id=self.user.id,
                        )
                        self.session.add(new_entry)
                        self.session.flush()
                        print(f"Entry added and flushed: {new_entry}")
                    except Exception as e:
                        print(f"Error adding entry {entry.service}: {str(e)}")
                        traceback.print_exc()

                try:
                    self.session.commit()
                    print(f"Successfully committed {len(new_entries)} entries.")
                except SQLAlchemyError as e:
                    print(f"SQLAlchemyError during commit: {str(e)}")
                    traceback.print_exc()
                    QMessageBox.critical(
                        self,
                        "Database Feil",
                        f"En feil oppstod under synkroniseringen:\n{str(e)}",
                        QMessageBox.Ok,
                    )
                    return
                except Exception as e:
                    print(f"Unexpected error during commit: {str(e)}")
                    traceback.print_exc()
                    QMessageBox.critical(
                        self,
                        "Feil",
                        f"En uventet feil oppstod:\n{str(e)}",
                        QMessageBox.Ok,
                    )
                    return

            except SQLAlchemyError as e:
                print(f"SQLAlchemyError while synchronizing: {str(e)}")
                traceback.print_exc()
                QMessageBox.critical(
                    self,
                    "Database Feil",
                    f"En feil oppstod under synkroniseringen:\n{str(e)}",
                    QMessageBox.Ok,
                )
            except Exception as e:
                print(f"Uventet feil: {str(e)}")
                traceback.print_exc()
                QMessageBox.critical(
                    self,
                    "Feil",
                    f"En uventet feil oppstod:\n{str(e)}",
                    QMessageBox.Ok,
                )
            finally:
                try:
                    backup_session.close()
                    backup_engine.dispose()
                    print("Backup session closed and engine disposed.")
                except Exception as e:
                    print(f"Error during cleanup: {str(e)}")
                    traceback.print_exc()
