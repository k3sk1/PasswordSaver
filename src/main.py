import sys
from PySide2.QtWidgets import QApplication, QDialog
from gui.login_dialog import LoginDialog
from gui.main_window import MainWindow
import styles


def main():
    app = QApplication(sys.argv)

    # Sett global font
    app.setFont(styles.GLOBAL_FONT)

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        password = login_dialog.get_password()
        # Valider hovedpassordet her (implementer valideringslogikk)
        # For nå antar vi at valideringen er vellykket

        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()


if __name__ == "__main__":
    main()
