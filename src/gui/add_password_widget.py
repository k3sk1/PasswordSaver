from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
    QMessageBox,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont


class AddPasswordWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #ffad8d;")
        self.setWindowTitle("Legg til passord")

        # Stilark
        line_edit_style = """
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 5px;
            font-size: 14px;
        }
        """

        button_style = """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        """

        label_style = """
        QLabel {
            font-size: 14px;
        }
        """

        # Opprett etiketter og inngangsfelt
        self.website_label = QLabel("Navn på nettside:")
        self.website_label.setStyleSheet(label_style)
        self.website_input = QLineEdit()
        self.website_input.setStyleSheet(line_edit_style)
        self.website_input.setTextMargins(5, 0, 0, 0)

        self.tag_label = QLabel("Emneknagg (valgfri):")
        self.tag_label.setStyleSheet(label_style)
        self.tag_input = QLineEdit()
        self.tag_input.setStyleSheet(line_edit_style)
        self.tag_input.setTextMargins(5, 0, 0, 0)

        self.username_label = QLabel("Brukernavn:")
        self.username_label.setStyleSheet(label_style)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(line_edit_style)
        self.username_input.setTextMargins(5, 0, 0, 0)

        self.password_label = QLabel("Passord:")
        self.password_label.setStyleSheet(label_style)
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet(line_edit_style)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setTextMargins(5, 0, 0, 0)

        self.link_label = QLabel("Link til nettside:")
        self.link_label.setStyleSheet(label_style)
        self.link_input = QLineEdit()
        self.link_input.setStyleSheet(line_edit_style)
        self.link_input.setTextMargins(5, 0, 0, 0)

        # Lagre-knapp
        self.save_button = QPushButton("Lagre")
        self.save_button.setStyleSheet(button_style)
        self.save_button.setFixedWidth(100)

        # Koble knappen til lagringsfunksjonen
        self.save_button.clicked.connect(self.save_password)

        # Opprett en QFormLayout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignCenter)
        form_layout.setSpacing(15)
        form_layout.setHorizontalSpacing(20)

        # Legg til feltene i form_layout
        form_layout.addRow(self.website_label, self.website_input)
        form_layout.addRow(self.tag_label, self.tag_input)
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, self.password_input)
        form_layout.addRow(self.link_label, self.link_input)

        # Opprett hovedlayouten
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)

    def save_password(self):
        # Hent data fra feltene
        data = self.get_data()
        # Validering av nødvendige felt
        if not data["website"] or not data["username"] or not data["password"]:
            QMessageBox.warning(
                self, "Feil", "Vennligst fyll ut alle obligatoriske felt."
            )
            return
        # Lagre dataene (du må implementere lagringsfunksjonen i MainWindow)
        # self.parent().save_password(data)
        QMessageBox.information(self, "Suksess", "Passord lagret.")
        # Tøm feltene etter lagring
        self.clear_fields()

    def get_data(self):
        return {
            "website": self.website_input.text(),
            "tag": self.tag_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "link": self.link_input.text(),
        }

    def clear_fields(self):
        self.website_input.clear()
        self.tag_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.link_input.clear()
