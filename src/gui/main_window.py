from PySide2.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QStackedWidget,
    QAction,
    QApplication,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont
from gui.add_password_widget import AddPasswordWidget
from gui.placeholder_widget import PlaceholderWidget
from gui.settings_widget import SettingsWidget
import styles


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Saver")
        # Sett en fast størrelse på vinduet
        self.resize(1000, 800)

        # Opprett hovedwidget og layout
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #b4a19e;")
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()
        self.central_widget.setLayout(main_layout)

        # Opprett sidepanelet med knappene
        self.create_side_panel(main_layout)

        # Opprett QStackedWidget for å holde forskjellige skjermer
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #fcd4a0;")
        main_layout.addWidget(self.stack)

        # Opprett widgets uten å sette forelder
        self.placeholder_widget = PlaceholderWidget()
        self.add_password_widget = AddPasswordWidget()

        # Hvis du har en widget for å vise passord, opprett den her
        # self.view_password_widget = ViewPasswordWidget()

        self.settings_widget = SettingsWidget(
            current_font_family=self.font().family(),
            current_font_size=self.font().pointSize(),
        )
        # Koble signaler til slots
        self.settings_widget.settings_changed.connect(self.apply_font_and_switch)
        self.settings_widget.settings_cancelled.connect(self.switch_back)

        # Legg widgets til stacken
        self.stack.addWidget(self.placeholder_widget)  # Indeks 0
        self.stack.addWidget(self.add_password_widget)  # Indeks 1
        self.stack.addWidget(self.settings_widget)  # Indeks 2

        # Skjul alle widgets ved oppstart
        self.stack.setCurrentWidget(self.placeholder_widget)

        # Sett global font
        self.apply_font((self.font().family(), self.font().pointSize()))

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

        # Koble knappene til funksjoner
        add_password_button.clicked.connect(self.show_add_password_widget)
        view_password_button.clicked.connect(self.view_passwords)
        settings_button.clicked.connect(self.open_settings)

        # Legg knappene til i layouten
        side_layout.addWidget(add_password_button)
        side_layout.addWidget(view_password_button)
        side_layout.addWidget(settings_button)

        # Sett maksimal bredde på sidepanelet
        side_panel.setMaximumWidth(300)

        # Legg til sidepanelet i hovedlayouten
        main_layout.addWidget(side_panel)

    def show_add_password_widget(self):
        # Bytt til add_password_widget i stacken
        self.stack.setCurrentWidget(self.add_password_widget)

    def show_view_password_widget(self):
        # Hvis du har implementert view_password_widget, bytt til den
        # self.stack.setCurrentWidget(self.view_password_widget)
        QMessageBox.information(self, "Info", "Funksjonalitet under utvikling.")

    def save_password(self, data):
        pass

    def view_passwords(self):
        pass

    def open_settings(self):
        # Bytt til settings_widget i stacken
        self.stack.setCurrentWidget(self.settings_widget)

    def apply_font_and_switch(self, font_settings):
        font_family, font_size = font_settings
        new_font = QFont(font_family, font_size)
        QApplication.instance().setFont(new_font)

        # Rekursivt sette font på alle widgets, inkludert statuslinjen
        self.set_font_recursively(self, new_font)

    def switch_back(self):
        # Bytt tilbake til placeholder uten å endre font
        self.stack.setCurrentWidget(self.placeholder_widget)

    def apply_font(self, font_settings):
        font_family, font_size = font_settings
        new_font = QFont(font_family, font_size)
        QApplication.instance().setFont(new_font)
        self.set_font_recursively(self, new_font)

    def set_font_recursively(self, widget, font):
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            self.set_font_recursively(child, font)
