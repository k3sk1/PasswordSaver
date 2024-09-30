from PySide2.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QStackedWidget,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from gui.add_password_widget import AddPasswordWidget
from gui.placeholder_widget import PlaceholderWidget
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Saver")
        # Sett en fast størrelse på vinduet
        self.resize(800, 600)

        # Legg til statuslinje
        self.create_status_bar()

        # Initialiser DataManager
        # os.makedirs("data", exist_ok=True)
        # self.data_manager = DataManager("data/passwords.db", "data/key.key")

        # Opprett hovedwidget og layout
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #b4a19e;")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Opprett sidepanelet med knappene
        self.create_side_panel(main_layout)

        # Opprett QStackedWidget for å holde forskjellige skjermer
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #fcd4a0;")
        main_layout.addWidget(self.stack)

        # Opprett placeholder-widgeten
        self.placeholder_widget = PlaceholderWidget()

        # Opprett passordskjemaet
        self.add_password_widget = AddPasswordWidget()
        self.add_password_widget.setParent(self)

        # Hvis du har en widget for å vise passord, opprett den her
        # self.view_password_widget = ViewPasswordWidget()
        # self.view_password_widget.setParent(self)

        # Legg widgets til stacken
        self.stack.addWidget(self.placeholder_widget)  # Indeks 0
        self.stack.addWidget(self.add_password_widget)  # Indeks 1
        # self.stack.addWidget(self.view_password_widget)  # Indeks 2

        # Skjul alle widgets ved oppstart
        self.stack.setCurrentWidget(self.placeholder_widget)

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
        settings_button = QPushButton("Innstillinger")

        # Endre skrifttype og størrelse
        font = QFont()
        font.setPointSize(16)
        add_password_button.setFont(font)
        view_password_button.setFont(font)
        settings_button.setFont(font)

        # Koble knappene til funksjoner
        add_password_button.clicked.connect(self.show_add_password_widget)
        view_password_button.clicked.connect(self.view_passwords)
        settings_button.clicked.connect(self.open_settings)

        # Legg knappene til i layouten
        side_layout.addWidget(add_password_button)
        side_layout.addWidget(view_password_button)
        side_layout.addWidget(settings_button)

        # Sett maksimal bredde på sidepanelet
        side_panel.setMaximumWidth(200)

        # Legg til sidepanelet i hovedlayouten
        main_layout.addWidget(side_panel)

    def create_status_bar(self):
        # Opprett statuslinjen
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)
        statusbar.showMessage("Klar")

    def show_add_password_widget(self):
        # Bytt til add_password_widget i stacken
        self.stack.setCurrentWidget(self.add_password_widget)

    def show_view_password_widget(self):
        # Hvis du har implementert view_password_widget, bytt til den
        # self.stack.setCurrentWidget(self.view_password_widget)
        pass  # Fjern denne linjen når du har implementert view_password_widget

    def save_password(self, data):
        pass

    def view_passwords(self):
        pass

    def open_settings(self):
        print("Åpne innstillinger")
