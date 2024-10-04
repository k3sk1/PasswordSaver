from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os


def derive_key(password: str, salt: bytes) -> bytes:
    """Generer en krypteringsnøkkel basert på master passordet og salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def hash_password(password: str, salt: bytes) -> str:
    return derive_key(password, salt).decode()


def encrypt_password(password: str, key: bytes) -> str:
    """Krypter passordet med den gitte nøkkelen."""
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """Dekrypter passordet med den gitte nøkkelen."""
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()


def encrypt_file(input_path, key, output_path):
    fernet = Fernet(key)
    with open(input_path, "rb") as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    with open(output_path, "wb") as encrypted_file:
        encrypted_file.write(encrypted)


def decrypt_file(input_path, key, output_path):
    fernet = Fernet(key)
    with open(input_path, "rb") as enc_file:
        encrypted = enc_file.read()

    decrypted = fernet.decrypt(encrypted)

    with open(output_path, "wb") as dec_file:
        dec_file.write(decrypted)
