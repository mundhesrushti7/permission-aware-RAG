from src.db.connection import get_connection


def create_audit_logs_table():
    """
    Create the audit_logs table if it does not already exist.
    """
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    request_id UUID PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    returned_document_ids TEXT[] NOT NULL,
                    model TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL
                )
                """
            )

        conn.commit()

    finally:
        conn.close()


def create_permission_audit_logs_table():
    """
    Create the permission_audit_logs table if it does not already exist.
    """
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS permission_audit_logs (
                    request_id UUID PRIMARY KEY,
                    actor_user_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    document_id TEXT NOT NULL,
                    target_user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL
                )
                """
            )

        conn.commit()

    finally:
        conn.close()