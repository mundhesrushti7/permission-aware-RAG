from src.audit.audit_logger import log_retrieval
from src.db.connection import get_connection
from src.rag.pipeline import retrieve_documents


def get_audit_record(request_id: str):
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    request_id,
                    user_id,
                    tenant_id,
                    query,
                    returned_document_ids,
                    model,
                    timestamp
                FROM audit_logs
                WHERE request_id = %s
                """,
                (request_id,),
            )

            return cursor.fetchone()

    finally:
        conn.close()


def test_log_retrieval_creates_audit_record():
    record = log_retrieval(
        user_id="user_123",
        tenant_id="tenant_a",
        query="How often should I change my password?",
        returned_document_ids=["policy_1"],
        model="rag-model",
    )

    stored_record = get_audit_record(record["request_id"])

    assert stored_record is not None
    assert stored_record[1] == "user_123"
    assert stored_record[2] == "tenant_a"
    assert stored_record[3] == "How often should I change my password?"
    assert stored_record[4] == ["policy_1"]
    assert stored_record[5] == "rag-model"


def test_each_audit_record_has_unique_request_id():
    first_record = log_retrieval(
        user_id="user_123",
        tenant_id="tenant_a",
        query="Question one",
        returned_document_ids=["policy_1"],
        model="rag-model",
    )

    second_record = log_retrieval(
        user_id="user_123",
        tenant_id="tenant_a",
        query="Question two",
        returned_document_ids=["policy_2"],
        model="rag-model",
    )

    assert first_record["request_id"] != second_record["request_id"]


def test_audit_record_contains_timestamp():
    record = log_retrieval(
        user_id="user_123",
        tenant_id="tenant_a",
        query="Test question",
        returned_document_ids=[],
        model="rag-model",
    )

    stored_record = get_audit_record(record["request_id"])

    assert stored_record is not None
    assert stored_record[6] is not None


def test_retrieval_creates_audit_log():
    results = retrieve_documents(
        "How often should I change my password?",
        user_id="user_123",
        tenant_id="tenant_a",
        user_roles=["employee"],
    )

    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    user_id,
                    tenant_id,
                    query,
                    returned_document_ids
                FROM audit_logs
                WHERE user_id = %s
                  AND tenant_id = %s
                  AND query = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (
                    "user_123",
                    "tenant_a",
                    "How often should I change my password?",
                ),
            )

            audit_record = cursor.fetchone()

    finally:
        conn.close()

    assert audit_record is not None
    assert audit_record[0] == "user_123"
    assert audit_record[1] == "tenant_a"
    assert audit_record[2] == "How often should I change my password?"

    returned_ids = [
        result.payload["document_id"]
        for result in results
    ]

    assert audit_record[3] == returned_ids