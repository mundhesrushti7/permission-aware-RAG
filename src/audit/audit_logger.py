from datetime import datetime, timezone
from uuid import uuid4

from src.db.connection import get_connection


def log_retrieval(
    user_id: str,
    tenant_id: str,
    query: str,
    returned_document_ids: list[str],
    model: str,
) -> dict:
    """
    Create and persist an audit record for a retrieval request.
    """

    request_id = str(uuid4())
    timestamp = datetime.now(timezone.utc)

    audit_record = {
        "request_id": request_id,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "query": query,
        "returned_document_ids": returned_document_ids,
        "model": model,
        "timestamp": timestamp.isoformat(),
    }

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO audit_logs (
                    request_id,
                    user_id,
                    tenant_id,
                    query,
                    returned_document_ids,
                    model,
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
                    user_id,
                    tenant_id,
                    query,
                    returned_document_ids,
                    model,
                    timestamp,
                ),
            )

        conn.commit()

    finally:
        conn.close()

    return audit_record