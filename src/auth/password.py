from argon2 import PasswordHasher


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Convert a plain-text password into a secure Argon2 hash.
    """
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain-text password against an existing Argon2 hash.
    """
    try:
        return password_hasher.verify(password_hash, password)
    except Exception:
        return False