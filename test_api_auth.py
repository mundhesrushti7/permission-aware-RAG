from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

import jwt

from src.config import JWT_SECRET_KEY
from src.api.main import app
from src.auth.identity import (
    assign_role_to_user,
    create_role,
    create_tenant,
    create_user,
)
from src.auth.jwt import decode_token
from src.db.connection import get_connection


client = TestClient(app)


TEST_TENANT_ID = "api-auth-test-tenant"
TEST_ROLE_ID = "api-auth-test-role"
TEST_USER_ID = "api-auth-test-user"
TEST_USERNAME = "api_auth_user"
TEST_PASSWORD = "CorrectPassword123!"


def setup_test_user():
    create_tenant(TEST_TENANT_ID, "API Auth Test Tenant")
    create_role(TEST_ROLE_ID, "employee")
    create_user(
        TEST_USER_ID,
        TEST_USERNAME,
        TEST_PASSWORD,
        TEST_TENANT_ID,
    )
    assign_role_to_user(TEST_USER_ID, TEST_ROLE_ID)


def cleanup_test_user():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_roles WHERE user_id = %s",
                (TEST_USER_ID,),
            )
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (TEST_USER_ID,),
            )
            cursor.execute(
                "DELETE FROM roles WHERE id = %s",
                (TEST_ROLE_ID,),
            )
            cursor.execute(
                "DELETE FROM tenants WHERE id = %s",
                (TEST_TENANT_ID,),
            )

        conn.commit()
    finally:
        conn.close()


def test_login_returns_jwt():
    setup_test_user()

    try:
        response = client.post(
            "/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

        payload = decode_token(data["access_token"])

        assert payload["user_id"] == TEST_USER_ID
        assert payload["tenant_id"] == TEST_TENANT_ID
        assert payload["roles"] == ["employee"]

    finally:
        cleanup_test_user()


def test_login_rejects_wrong_password():
    setup_test_user()

    try:
        response = client.post(
            "/login",
            json={
                "username": TEST_USERNAME,
                "password": "WrongPassword!",
            },
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    finally:
        cleanup_test_user()


def test_login_rejects_unknown_username():
    response = client.post(
        "/login",
        json={
            "username": "does_not_exist",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_token_can_access_me():
    setup_test_user()

    try:
        login_response = client.post(
            "/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
            },
        )

        assert login_response.status_code == 200

        access_token = login_response.json()["access_token"]

        me_response = client.get(
            "/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert me_response.status_code == 200

        assert me_response.json() == {
            "user_id": TEST_USER_ID,
            "tenant_id": TEST_TENANT_ID,
            "roles": ["employee"],
        }

    finally:
        cleanup_test_user()


def test_me_rejects_missing_token():
    response = client.get("/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token():
    response = client.get(
        "/me",
        headers={
            "Authorization": "Bearer definitely-not-a-real-jwt",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_me_rejects_expired_token():
    expired_payload = {
        "user_id": "expired-user",
        "tenant_id": "tenant_a",
        "roles": ["employee"],
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }

    expired_token = jwt.encode(
        expired_payload,
        JWT_SECRET_KEY,
        algorithm="HS256",
    )

    response = client.get(
        "/me",
        headers={
            "Authorization": f"Bearer {expired_token}",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"