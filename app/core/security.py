from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

bcrypt_hasher = BcryptHasher(rounds=10)

password_hash = PasswordHash((bcrypt_hasher,))


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)
