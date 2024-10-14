import sys
import os
from PySide2.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.login_manager import LoginManager
import styles


def main():
    app = QApplication(sys.argv)

    # Sett global font
    app.setFont(styles.GLOBAL_FONT)

    # Få den absolutte stien til 'data' mappen
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    db_path = os.path.join(data_dir, "passwords.db")

    # Initialiser LoginManager
    login_manager = LoginManager(db_path)

    # Opprett hovedvinduet
    main_window = MainWindow(None, login_manager.session, None, db_path)
    main_window.login_manager = login_manager  # Sett login manager som en attributt
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
