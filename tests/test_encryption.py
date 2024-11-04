import base64
import sys
import os

# Legg til prosjektets rotkatalog til sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data.encryption import (
    derive_key_for_column,
    hash_password,
    encrypt_password,
    decrypt_password,
)


def test_hash_password():
    password = "test_password"
    salt = b"this_is_a_test_salt"
    hashed = hash_password(password, salt)
    assert hashed is not None
    assert isinstance(hashed, str)


def test_derive_key_for_column():
    password = "test_password"
    salt = b"this_is_a_test_salt"
    column_name = "test_column"
    key = derive_key_for_column(password, salt, column_name)
    assert key is not None
    assert isinstance(key, bytes)


def test_encrypt_decrypt_password():
    password = "test_password"
    key = base64.urlsafe_b64encode(b"0" * 32)  # Simulert nøkkel
    encrypted = encrypt_password(password, key)
    assert encrypted is not None
    decrypted = decrypt_password(encrypted, key)
    assert decrypted == password
