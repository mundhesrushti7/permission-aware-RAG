from src.db.connection import get_connection


def create_identity_tables():
    """
    Create the tables required for users, tenants, and roles.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tenants (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    tenant_id TEXT NOT NULL REFERENCES tenants(id)
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS roles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id TEXT NOT NULL REFERENCES users(id),
                    role_id TEXT NOT NULL REFERENCES roles(id),
                    PRIMARY KEY (user_id, role_id)
                )
                """
            )

        conn.commit()

    finally:
        conn.close()