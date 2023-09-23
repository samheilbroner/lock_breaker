from typing import Union

from cryptography.fernet import Fernet

from lock_breaker import DEFAULT_PASSWORD_LENGTH
from lock_breaker.hashing import sha_hash
from lock_breaker.keys import TEXT_GENERATION_KEY


def random_digits_from_encryption_key(message, key: str = TEXT_GENERATION_KEY,
                                      password_length: int = DEFAULT_PASSWORD_LENGTH) -> str:
    """
    Create random digits for password using hidden key.
    :param message: message to encrypt.
    :param key: encyption key.
    :param password_length: length of return password
    :return: a password of digits
    """
    token = message + key
    password = sha_hash(token) % (10 ** (password_length))
    return str(password)


def encrypt(message, key: bytes) -> str:
    """
    Encrypt message using Fernet.
    :param message: message to encrypt.
    :param key: key to use for encryption.
    :return: encrypted message.
    """
    f = Fernet(key)
    return f.encrypt(message.encode()).decode('utf-8')


def decrypt(message: Union[bytes, str], key: bytes) -> str:
    """
    Decrypt message using Fernet.
    :param message: message to decrypt.
    :param key: key to use for decryption.
    :return: decrypted message.
    """
    f = Fernet(key)
    if isinstance(message, str):
        message = message.encode()
    try:
        answer = f.decrypt(message).decode('utf-8')
    except:
        answer = 'INVALID'
    return answer

