import base64
import json
import os
import sys
from PySide2.QtWidgets import QApplication, QDialog, QMessageBox
from gui.login_dialog import LoginDialog
from gui.main_window import MainWindow
import styles
from data.encryption import derive_key, hash_password
from data.database import get_engine, create_tables, get_session


def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "config.json")
    if not os.path.exists(config_path):
        return None
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def save_config(config_data):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "..", "config", "config.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config_data, f)


def main():
    app = QApplication(sys.argv)

    # Sett global font
    app.setFont(styles.GLOBAL_FONT)

    config = load_config()

    if config:
        login_dialog = LoginDialog(existing=True)
    else:
        login_dialog = LoginDialog(existing=False)

    if login_dialog.exec_() == QDialog.Accepted:
        password = login_dialog.get_password()
        if config:
            # Eksisterende bruk: deriver nøkkel og valider passord
            derived_key = derive_key(password, base64.b64decode(config["salt"]))
            stored_hash = config["password_hash"]
            if (
                not hash_password(password, base64.b64decode(config["salt"]))
                == stored_hash
            ):
                QMessageBox.critical(
                    None, "Feil", "Ugyldig hovedpassord.", QMessageBox.Ok
                )
                sys.exit()
            key = derived_key

            # Sett opp databasen
            db_path = config.get(
                "db_path",
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "data",
                    "passwords.db",
                ),
            )

            engine = get_engine(db_path)
            create_tables(engine)
            session = get_session(engine)
        else:
            # Første gang bruk: opprett salt, hash passord og lagre config
            confirm_password = login_dialog.get_confirm_password()
            if password != confirm_password:
                QMessageBox.critical(
                    None, "Feil", "Passordene stemmer ikke overens.", QMessageBox.Ok
                )
                sys.exit()
            salt = os.urandom(16)
            key = derive_key(password, salt)
            hashed_password = hash_password(password, salt)
            db_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "data", "passwords.db"
            )

            config_data = {
                "salt": base64.b64encode(salt).decode(),
                "password_hash": hashed_password,
                "db_path": db_path,
            }
            save_config(config_data)

            # Sett opp databasen
            engine = get_engine(db_path)
            create_tables(engine)
            session = get_session(engine)

        main_window = MainWindow(key, session)
        main_window.show()
        sys.exit(app.exec_())
    else:
        sys.exit()


if __name__ == "__main__":
    main()
