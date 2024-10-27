import base64
import datetime
import os
from data.encryption import derive_key_for_column, hash_password
from data.models import User, Settings


class LoginManager:
    def __init__(self, db_path):
        from data.database import get_engine, create_tables, get_session

        self.db_path = db_path
        self.engine = get_engine(db_path)
        create_tables(self.engine)
        self.session = get_session(self.engine)

    def authenticate_user(self, username: str, password: str) -> tuple:
        """
        Authenticate user and return (user, derived_key) if successful, else (None, None)
        """
        user = self.session.query(User).filter_by(username=username).first()
        if not user:
            return (None, None, "Bruker eksisterer ikke.")

        # Check if user is locked out
        current_time = datetime.datetime.now()
        if user.lockout_until and current_time < user.lockout_until:
            lockout_remaining = user.lockout_until - current_time
            minutes, seconds = divmod(lockout_remaining.total_seconds(), 60)
            message = f"Brukeren er låst ute i {int(minutes)} minutter og {int(seconds)} sekunder."
            return (None, None, message)

        try:
            salt = base64.b64decode(user.salt)
            computed_hash = hash_password(password, salt)
            if computed_hash == user.password_hash:
                # Utlede nøkler for hver kolonne som trenger kryptering
                derived_keys = {
                    "service": derive_key_for_column(password, salt, "service"),
                    "email": derive_key_for_column(password, salt, "email"),
                    "username": derive_key_for_column(password, salt, "username"),
                    "password": derive_key_for_column(password, salt, "password"),
                    "link": derive_key_for_column(password, salt, "link"),
                    "tag": derive_key_for_column(password, salt, "tag"),
                }
                # Reset failed attempts on successful login
                user.failed_attempts = 0
                user.lockout_until = None
                self.session.commit()
                return (user, derived_keys, None)
            else:
                user.failed_attempts += 1
                user.last_failed_attempt = current_time

                # Lock out user if failed attempts exceed threshold
                if user.failed_attempts >= 3:
                    lockout_duration = datetime.timedelta(
                        minutes=5 * user.failed_attempts
                    )
                    user.lockout_until = current_time + lockout_duration

                self.session.commit()
                return (None, None, "Ugyldig passord.")
        except Exception as e:
            return (None, None, "En feil oppstod under autentisering.")

    def register_user(self, username: str, password: str) -> bool:
        existing_user = self.session.query(User).filter_by(username=username).first()
        if existing_user:
            return False

        try:
            salt = os.urandom(16)
            hashed_password = hash_password(password, salt)
            new_user = User(
                username=username,
                password_hash=hashed_password,
                salt=base64.b64encode(salt).decode(),
            )

            # Opprett standard innstillinger for ny bruker
            new_settings = Settings(theme="default", font_size=16)
            new_user.settings = new_settings

            self.session.add(new_user)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            return False

    def get_all_users(self):
        """
        Hent alle brukernavn fra databasen.
        """
        try:
            users = self.session.query(User.username).all()
            return [user.username for user in users]
        except Exception as e:
            return []
