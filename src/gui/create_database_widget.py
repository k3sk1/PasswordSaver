# src/gui/create_database_widget.py
from PySide2.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QInputDialog,
    QLineEdit,
)
from PySide2.QtCore import Qt, Signal
import os
import json
import base64
from data.encryption import derive_key
from data.database import get_engine, create_tables, get_session


class CreateDatabaseWidget(QWidget):
    # Signal som emitteres når databasen er opprettet
    database_created = Signal()

    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #d1e8e2;")
        self.setWindowTitle("Opprett Passord Database")

        # Initialize key and session
        self.key = None
        self.session = None

        # Opprett "Opprett Database" knapp
        self.create_db_button = QPushButton("Opprett Passord Database")
        self.create_db_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px 32px;
                text-align: center;
                font-size: 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        self.create_db_button.setFixedSize(300, 50)
        self.create_db_button.clicked.connect(self.create_database)

        # Sett opp layout
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.create_db_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def create_database(self):
        # Få den absolutte stien til 'data' mappen
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, "..", "data")
        salt_file = os.path.join(data_dir, "salt.json")
        db_path = os.path.join(data_dir, "passwords.db")

        # Sørg for at 'data' mappen eksisterer
        os.makedirs(data_dir, exist_ok=True)

        # Generer salt
        salt = os.urandom(16)

        # Generer en tilfeldig nøkkel
        key = base64.urlsafe_b64encode(os.urandom(32))

        # Lagre salt og nøkkel til 'salt.json'
        try:
            with open(salt_file, "w") as f:
                json.dump(
                    {"salt": base64.b64encode(salt).decode(), "key": key.decode()}, f
                )
        except Exception as e:
            QMessageBox.critical(self, "Feil", f"Kunne ikke lagre saltfilen: {str(e)}")
            return

        # Sett opp databasen
        try:
            engine = get_engine(db_path)
            create_tables(engine)
            session = get_session(engine)
        except Exception as e:
            QMessageBox.critical(
                self, "Feil", f"Kunne ikke sette opp databasen: {str(e)}"
            )
            return

        # Lagre key og session som attributter
        self.key = key
        self.session = session

        # Emit signal for at databasen er opprettet
        self.database_created.emit()
