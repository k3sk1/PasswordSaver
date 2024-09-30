# src/gui/main_window.py

from PySide2.QtWidgets import QMainWindow
from PySide2.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Password Saver")
        self.setGeometry(100, 100, 800, 600)  # Sett posisjon og størrelse

        # Her kan du legge til menylinje, verktøylinje, statuslinje osv.
        # Foreløpig er vinduet tomt.
