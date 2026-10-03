from src.auth.password import hash_password
from src.db.connection import get_connection


def create_tenant(tenant_id: str, name: str) -> None:
    """
    Create a tenant.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tenants (id, name)
                VALUES (%s, %s)
                """,
                (tenant_id, name),
            )
        conn.commit()
    finally:
        conn.close()


def create_role(role_id: str, name: str) -> None:
    """
    Create a role.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO roles (id, name)
                VALUES (%s, %s)
                """,
                (role_id, name),
            )
        conn.commit()
    finally:
        conn.close()


def create_user(
    user_id: str,
    username: str,
    password: str,
    tenant_id: str,
) -> None:
    """
    Create a user and store only the Argon2 password hash.
    """
    password_hash = hash_password(password)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    id,
                    username,
                    password_hash,
                    tenant_id
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_id,
                    username,
                    password_hash,
                    tenant_id,
                ),
            )
        conn.commit()
    finally:
        conn.close()



def assign_role_to_user(user_id: str, role_id: str) -> None:
    """
    Assign an existing role to an existing user.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO user_roles (user_id, role_id)
                VALUES (%s, %s)
                """,
                (user_id, role_id),
            )
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(username: str) -> dict | None:
    """
    Retrieve a user and their roles by username.
    """
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    u.password_hash,
                    u.tenant_id,
                    COALESCE(
                        ARRAY_AGG(r.name) FILTER (WHERE r.name IS NOT NULL),
                        ARRAY[]::TEXT[]
                    ) AS roles
                FROM users u
                LEFT JOIN user_roles ur
                    ON u.id = ur.user_id
                LEFT JOIN roles r
                    ON ur.role_id = r.id
                WHERE u.username = %s
                GROUP BY
                    u.id,
                    u.username,
                    u.password_hash,
                    u.tenant_id
                """,
                (username,),
            )

            row = cursor.fetchone()

        if row is None:
            return None

        user_id, username, password_hash, tenant_id, roles = row

        return {
            "id": user_id,
            "username": username,
            "password_hash": password_hash,
            "tenant_id": tenant_id,
            "roles": roles,
        }

    finally:
        conn.close()