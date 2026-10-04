from src.api.auth import authenticate_user
from src.auth.identity import (
    assign_role_to_user,
    create_role,
    create_tenant,
    create_user,
)
from src.db.connection import get_connection


def cleanup_identity(
    tenant_id: str,
    role_id: str,
    user_id: str,
) -> None:
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_roles WHERE user_id = %s",
                (user_id,),
            )
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,),
            )
            cursor.execute(
                "DELETE FROM roles WHERE id = %s",
                (role_id,),
            )
            cursor.execute(
                "DELETE FROM tenants WHERE id = %s",
                (tenant_id,),
            )

        conn.commit()
    finally:
        conn.close()


def test_authenticate_user_success():
    tenant_id = "test_tenant_auth"
    role_id = "test_role_auth"
    user_id = "test_user_auth"
    username = "auth_user"

    cleanup_identity(
        tenant_id,
        role_id,
        user_id,
    )

    create_tenant(
        tenant_id=tenant_id,
        name="Test Authentication Tenant",
    )

    create_role(
        role_id=role_id,
        name="employee_auth",
    )

    create_user(
        user_id=user_id,
        username=username,
        password="correct-password",
        tenant_id=tenant_id,
    )

    assign_role_to_user(
        user_id=user_id,
        role_id=role_id,
    )

    user = authenticate_user(
        username=username,
        password="correct-password",
    )

    assert user is not None
    assert user["id"] == user_id
    assert user["username"] == username
    assert user["tenant_id"] == tenant_id
    assert user["roles"] == ["employee_auth"]

    cleanup_identity(
        tenant_id,
        role_id,
        user_id,
    )


def test_authenticate_user_rejects_wrong_password():
    tenant_id = "test_tenant_auth_wrong"
    role_id = "test_role_auth_wrong"
    user_id = "test_user_auth_wrong"
    username = "auth_wrong_user"

    cleanup_identity(
        tenant_id,
        role_id,
        user_id,
    )

    create_tenant(
        tenant_id=tenant_id,
        name="Test Wrong Password Tenant",
    )

    create_role(
        role_id=role_id,
        name="employee_auth_wrong",
    )

    create_user(
        user_id=user_id,
        username=username,
        password="correct-password",
        tenant_id=tenant_id,
    )

    assign_role_to_user(
        user_id=user_id,
        role_id=role_id,
    )

    user = authenticate_user(
        username=username,
        password="wrong-password",
    )

    assert user is None

    cleanup_identity(
        tenant_id,
        role_id,
        user_id,
    )


def test_authenticate_user_rejects_unknown_username():
    user = authenticate_user(
        username="does-not-exist",
        password="anything",
    )

    assert user is None