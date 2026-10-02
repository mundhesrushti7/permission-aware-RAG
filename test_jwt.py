import pytest

from src.auth.jwt import create_token, decode_token

from datetime import datetime, timedelta, timezone



def test_create_and_decode_token():
    token = create_token(
        "user_123",
        "tenant_a",
        ["employee"],
    )

    payload = decode_token(token)

    assert payload["user_id"] == "user_123"
    assert payload["tenant_id"] == "tenant_a"
    assert payload["roles"] == ["employee"]




def test_tampered_token_is_rejected():
    token = create_token(
        "user_123",
        "tenant_a",
        ["employee"],
    )

    parts = token.split(".")

    tampered_payload = (
        "eyJ1c2VyX2lkIjoiYXR0YWNrZXIiLCJ0ZW5hbnRfaWQiOiJ0ZW5hbnRfYiIs"
        "InJvbGVzIjpbImFkbWluIl19"
    )

    tampered_token = (
        parts[0]
        + "."
        + tampered_payload
        + "."
        + parts[2]
    )

    with pytest.raises(Exception):
        decode_token(tampered_token)


def test_expired_token_is_rejected():
    token = create_token(
        "user_123",
        "tenant_a",
        ["employee"],
    )

    import jwt

    expired_payload = {
        "user_id": "user_123",
        "tenant_id": "tenant_a",
        "roles": ["employee"],
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }

    expired_token = jwt.encode(
        expired_payload,
        "development-secret-key-1234567890",
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(expired_token)