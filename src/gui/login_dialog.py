from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logg inn")

        self.label = QLabel("Angi hovedpassordet:")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Logg inn")
        self.login_button.clicked.connect(self.verify_password)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def verify_password(self):
        # Implementer passordvalidering her
        # For nå antar vi at passordet alltid er korrekt
        self.accept()

    def get_password(self):
        return self.password_edit.text()
