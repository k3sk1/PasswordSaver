import sys
import os
from PySide2.QtWidgets import QApplication, QMessageBox, QDialog
from gui.main_window import MainWindow
from utils.login_manager import LoginManager
from gui.login_dialog import LoginDialog
from data.models import User
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

    while True:
        # Sjekk om det finnes noen brukere
        user_exists = login_manager.session.query(User).first() is not None
        print("User exists:", user_exists)

        # Opprett login dialog
        login_dialog = LoginDialog(db_path, login_manager.session, existing=user_exists)
        print("Login dialog created.")

        # Vis dialogen som modal
        result = login_dialog.exec_()
        print("Dialog executed with result:", result)

        if result == QDialog.Accepted:
            credentials = login_dialog.get_credentials()
            mode = credentials["mode"]
            username = credentials["username"]
            password = credentials["password"]

            if mode == "login":
                user, key = login_manager.authenticate_user(username, password)
                if user:
                    print("Login successful, opening main window.")
                    main_window = MainWindow(
                        key,
                        login_manager.session,
                        user,
                        db_path,
                    )
                    main_window.logged_out.connect(
                        lambda: app.quit()
                    )  # Logg ut fører til at hovedvinduet lukkes
                    main_window.show()
                    app.exec_()

                    # Når hovedvinduet lukkes, tilbake til login
                    continue

                else:
                    QMessageBox.critical(
                        None,
                        "Feil",
                        "Ugyldig brukernavn eller passord.",
                        QMessageBox.Ok,
                    )
                    print("Authentication failed. Showing login dialog again.")
                    # Fortsett løkka for å vise dialogen igjen
            elif mode == "register":
                created = login_manager.create_user(username, password)
                if created:
                    QMessageBox.information(
                        None,
                        "Suksess",
                        "Bruker opprettet! Vennligst logg inn.",
                        QMessageBox.Ok,
                    )
                    print("User created. Showing login dialog again.")
                    # Fortsett løkka for å vise dialogen igjen i innloggingsmodus
                else:
                    QMessageBox.critical(
                        None,
                        "Feil",
                        "Kunne ikke opprette bruker. Brukernavn kan allerede være tatt.",
                        QMessageBox.Ok,
                    )
                    print("User creation failed. Showing login dialog again.")
                    # Fortsett løkka for å vise dialogen igjen
        else:
            # Dialog avvist (bruker trykker "Avbryt")
            print("Dialog rejected, quitting app.")
            login_manager.session.close()
            app.quit()
            sys.exit(0)


if __name__ == "__main__":
    main()
