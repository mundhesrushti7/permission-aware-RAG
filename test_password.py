from src.auth.password import hash_password, verify_password


def test_password_hashing_and_verification():
    password = "correct-password"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False