from cryptography.fernet import Fernet

from lock_breaker import DEFAULT_PASSWORD_LENGTH
from lock_breaker.password import random_digits_from_encryption_key, encrypt, \
    decrypt


def test_create_password():
    assert len(
        random_digits_from_encryption_key('apple')) == DEFAULT_PASSWORD_LENGTH
    assert random_digits_from_encryption_key(
        'apple') != random_digits_from_encryption_key('zombie')


def test_encryption():
    message = 'apple'
    key = Fernet.generate_key()
    enc = encrypt(message, key)
    assert message == decrypt(enc, key)
