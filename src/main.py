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

    # Get a writable directory for the database (e.g., user's home directory)
    user_home_dir = os.path.expanduser("~")
    data_dir = os.path.join(
        user_home_dir, "PassordSkapData"
    )  # Create a folder for app data
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)  # Create the directory if it doesn't exist

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
