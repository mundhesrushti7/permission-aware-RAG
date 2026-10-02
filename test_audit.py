from src.audit.audit_logger import audit_logs, log_retrieval
from src.rag.pipeline import retrieve_documents

def test_log_retrieval_creates_audit_record():
    audit_logs.clear()

    record = log_retrieval(
        user_id="user_123",
        tenant_id="tenant_a",
        query="How often should I change my password?",
        returned_document_ids=["policy_1"],
        model="rag-model",
    )

    assert len(audit_logs) == 1

    assert record["user_id"] == "user_123"
    assert record["tenant_id"] == "tenant_a"
    assert record["query"] == "How often should I change my password?"
    assert record["returned_document_ids"] == ["policy_1"]
    assert record["model"] == "rag-model"


def test_each_audit_record_has_unique_request_id():
    audit_logs.clear()

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
    audit_logs.clear()

    record = log_retrieval(
        user_id="user_123",
        tenant_id="tenant_a",
        query="Test question",
        returned_document_ids=[],
        model="rag-model",
    )

    assert "timestamp" in record
    assert record["timestamp"]



def test_retrieval_creates_audit_log():
    audit_logs.clear()

    results = retrieve_documents(
        "How often should I change my password?",
        user_id="user_123",
        tenant_id="tenant_a",
        user_roles=["employee"],
    )

    assert len(audit_logs) == 1

    audit_record = audit_logs[0]

    assert audit_record["user_id"] == "user_123"
    assert audit_record["tenant_id"] == "tenant_a"
    assert audit_record["query"] == "How often should I change my password?"

    returned_ids = [
        result.payload["document_id"]
        for result in results
    ]

    assert audit_record["returned_document_ids"] == returned_ids