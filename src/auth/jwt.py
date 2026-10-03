import jwt
from datetime import datetime, timedelta, timezone

from src.config import JWT_SECRET_KEY


ALGORITHM = "HS256"


def create_token(
    user_id: str,
    tenant_id: str,
    roles: list[str],
) -> str:
    """
    Create a JWT containing the user's identity and permissions.
    """

    payload = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


def decode_token(token: str) -> dict:
    """
    Verify a JWT and return its payload.
    """

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    return payload
