from datetime import datetime, timezone
from uuid import uuid4

from src.db.connection import get_connection


def log_permission_change(
    actor_user_id: str,
    tenant_id: str,
    document_id: str,
    target_user_id: str,
    action: str,
) -> dict:
    """
    Create and persist an audit record for a permission change.
    """

    request_id = str(uuid4())
    timestamp = datetime.now(timezone.utc)

    audit_record = {
        "request_id": request_id,
        "actor_user_id": actor_user_id,
        "tenant_id": tenant_id,
        "document_id": document_id,
        "target_user_id": target_user_id,
        "action": action,
        "timestamp": timestamp.isoformat(),
    }

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO permission_audit_logs (
                    request_id,
                    actor_user_id,
                    tenant_id,
                    document_id,
                    target_user_id,
                    action,
                    timestamp
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    request_id,
                    actor_user_id,
                    tenant_id,
                    document_id,
                    target_user_id,
                    action,
                    timestamp,
                ),
            )

        conn.commit()

    finally:
        conn.close()

    return audit_record