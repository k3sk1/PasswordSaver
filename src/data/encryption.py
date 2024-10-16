from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64


def derive_key_for_column(password, salt, column_name, iterations=100000):
    # Bruk navnet på kolonnen for å gjøre nøkler unike
    column_specific_salt = salt + column_name.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=column_specific_salt,
        iterations=iterations,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)


def hash_password(password, salt, iterations=100000):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend(),
    )
    return base64.b64encode(kdf.derive(password.encode())).decode().strip()


def encrypt_password(password: str, key: bytes) -> str:
    """Krypter passordet med den gitte nøkkelen."""
    try:
        f = Fernet(key)
        encrypted = f.encrypt(password.encode()).decode()
        print(f"Encrypted data using key: {key}")
        return encrypted
    except Exception as e:
        print(f"Error encrypting entry {password}: {e}")
        raise e


def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """Dekrypter passordet med den gitte nøkkelen."""
    try:
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_password.encode()).decode()
        print(f"Decrypted data using key: {key}")
        return decrypted
    except Exception as e:
        print(f"Error decrypting entry {encrypted_password}: {e}")
        raise e
