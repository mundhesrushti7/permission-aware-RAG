from datetime import datetime, timezone
from uuid import uuid4


audit_logs = []


def log_retrieval(
    user_id: str,
    tenant_id: str,
    query: str,
    returned_document_ids: list[str],
    model: str,
) -> dict:
    """
    Create and store an audit record for a retrieval request.
    """

    audit_record = {
        "request_id": str(uuid4()),
        "user_id": user_id,
        "tenant_id": tenant_id,
        "query": query,
        "returned_document_ids": returned_document_ids,
        "model": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    audit_logs.append(audit_record)

    return audit_record