from src.db.connection import get_connection


def test_database_can_store_audit_record():
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
                    gen_random_uuid(),
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    NOW()
                )
                """,
                (
                    "user_test",
                    "tenant_a",
                    "Test audit query",
                    ["policy_1", "policy_2"],
                    "rag-model",
                ),
            )

        conn.commit()

    finally:
        conn.close()