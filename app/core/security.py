# app/core/security.py
"""Функции безопасности для хеширования и проверки паролей."""

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

bcrypt_hasher = BcryptHasher(rounds=10)

password_hash = PasswordHash((bcrypt_hasher,))


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет пароль против его хеша."""
    return password_hash.verify(password, hashed_password)
