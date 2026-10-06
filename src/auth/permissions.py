from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue
from src.audit.permission_audit_logger import log_permission_change

client = QdrantClient(
    url="http://localhost:6333"
)


def revoke_user_access(
    document_id: str,
    target_user_id: str,
    actor_user_id: str,
    actor_tenant_id: str,
    actor_roles: list[str],
) -> None:
    """
    Revoke a user's direct access to a document.

    The actor must be an administrator and the document
    must belong to the actor's tenant.
    """

    if "admin" not in actor_roles:
        raise PermissionError(
            "Only administrators can modify document permissions."
        )

    records, _ = client.scroll(
        collection_name="documents",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
        limit=1,
        with_payload=True,
        with_vectors=False,
    )

    if not records:
        raise ValueError(
            f"Document '{document_id}' was not found."
        )

    document = records[0].payload

    if document["tenant_id"] != actor_tenant_id:
        raise PermissionError(
            "You cannot modify permissions for another tenant's document."
        )

    allowed_users = document.get("allowed_users", [])

    updated_allowed_users = [
        user_id
        for user_id in allowed_users
        if user_id != target_user_id
    ]

    client.set_payload(
        collection_name="documents",
        payload={
            "allowed_users": updated_allowed_users,
        },
        points=[records[0].id],
    )


    log_permission_change(
        actor_user_id=actor_user_id,
        tenant_id=actor_tenant_id,
        document_id=document_id,
        target_user_id=target_user_id,
        action="revoke_user_access",
    )
