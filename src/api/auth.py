import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.models import LoginRequest, LoginResponse
from src.auth.identity import get_user_by_username
from src.auth.jwt import create_token, decode_token
from src.auth.password import verify_password


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify the JWT from the Authorization header
    and return the authenticated user's context.
    """

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
    )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
    )

    return {
        "user_id": payload["user_id"],
        "tenant_id": payload["tenant_id"],
        "roles": payload["roles"],
    }


def authenticate_user(username: str, password: str) -> dict | None:
    """
    Authenticate a user using their username and password.

    Returns the user identity if authentication succeeds.
    Returns None if the credentials are invalid.
    """
    user = get_user_by_username(username)

    if user is None:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return user


def login_user(credentials: LoginRequest) -> LoginResponse:
    """
    Authenticate a user and issue a JWT.
    """
    user = authenticate_user(
        username=credentials.username,
        password=credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_token(
        user_id=user["id"],
        tenant_id=user["tenant_id"],
        roles=user["roles"],
    )

    return LoginResponse(
        access_token=token,
        token_type="bearer",
    )