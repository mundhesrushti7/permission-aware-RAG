from src.auth.identity import (
    assign_role_to_user,
    create_role,
    create_tenant,
    create_user,
    get_user_by_username,
)
from src.db.connection import get_connection
from src.auth.password import verify_password

def test_create_identity_records():
    tenant_id = "test_tenant_identity"
    role_id = "test_role_identity"
    user_id = "test_user_identity"
    username = "test_identity_user"

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

    create_tenant(
        tenant_id=tenant_id,
        name="Test Identity Tenant",
    )

    create_role(
        role_id=role_id,
        name="test_identity_role",
    )

    create_user(
        user_id=user_id,
        username=username,
        password="test-password-123",
        tenant_id=tenant_id,
    )

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT username, password_hash, tenant_id
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )

            row = cursor.fetchone()

        assert row is not None

        stored_username, stored_password_hash, stored_tenant_id = row

        assert stored_username == username
        assert stored_password_hash != "test-password-123"
        assert stored_password_hash.startswith("$argon2")
        assert stored_tenant_id == tenant_id

    finally:
        conn.close()

    # Clean up the records created by this test.
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


def test_assign_role_and_get_user():
    tenant_id = "test_tenant_lookup"
    role_id = "test_role_lookup"
    user_id = "test_user_lookup"
    username = "lookup_user"

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

    create_tenant(
        tenant_id=tenant_id,
        name="Test Lookup Tenant",
    )

    create_role(
        role_id=role_id,
        name="employee",
    )

    create_user(
        user_id=user_id,
        username=username,
        password="lookup-password-123",
        tenant_id=tenant_id,
    )

    assign_role_to_user(
        user_id=user_id,
        role_id=role_id,
    )

    user = get_user_by_username(username)

    assert user is not None
    assert user["id"] == user_id
    assert user["username"] == username
    assert user["tenant_id"] == tenant_id
    assert user["roles"] == ["employee"]

    assert verify_password(
        "lookup-password-123",
        user["password_hash"],
    ) is True

    assert verify_password(
        "wrong-password",
        user["password_hash"],
    ) is False

    # Clean up.
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