import base64
import os
from data.encryption import derive_key, hash_password
from data.models import User, Settings
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


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
        print("Authenticating user:", username)
        user = self.session.query(User).filter_by(username=username).first()
        if not user:
            print("User does not exist.")
            return (None, None)

        try:
            salt = base64.b64decode(user.salt)
            derived_key = derive_key(password, salt)
            computed_hash = hash_password(password, salt)
            print("Stored hash:", repr(user.password_hash))
            print("Computed hash:", repr(computed_hash))
            if computed_hash == user.password_hash:
                print("Authentication successful.")
                return (user, derived_key)
            else:
                print("Invalid password.")
                return (None, None)
        except Exception as e:
            print("Error during authentication:", e)
            return (None, None)

    def create_user(self, username: str, password: str) -> bool:
        print("Creating user:", username)
        existing_user = self.session.query(User).filter_by(username=username).first()
        if existing_user:
            print("Username already taken.")
            return False

        try:
            salt = os.urandom(16)
            hashed_password = hash_password(password, salt)
            derived_key = derive_key(password, salt)
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
            print("New user created successfully.")
            return True
        except IntegrityError:
            self.session.rollback()
            print("IntegrityError: Username already taken.")
            return False
        except Exception as e:
            self.session.rollback()
            print("Error during user creation:", e)
            return False
