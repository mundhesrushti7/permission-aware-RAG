from src.auth.acl import is_document_allowed


def test_permission_revoke_blocks_user_access():
    document = {
        "tenant_id": "tenant_a",
        "allowed_users": ["user_123"],
        "allowed_roles": [],
    }

    # Before revocation: user is allowed.
    assert is_document_allowed(
        document,
        user_id="user_123",
        user_tenant_id="tenant_a",
        user_roles=[],
    )

    # Revoke the user's permission.
    document["allowed_users"] = []

    # After revocation: user must be denied.
    assert not is_document_allowed(
        document,
        user_id="user_123",
        user_tenant_id="tenant_a",
        user_roles=[],
    )


from qdrant_client import QdrantClient

from src.rag.pipeline import retrieve_documents


client = QdrantClient(
    url="http://localhost:6333"
)


def test_permission_revoke_blocks_user_at_retrieval_layer():
    original_payload = {
        "allowed_users": [],
        "allowed_roles": ["admin"],
    }

    try:
        # Grant direct access to user_123.
        client.set_payload(
            collection_name="documents",
            payload={
                "allowed_users": ["user_123"],
            },
            points=[3],
        )

        results_before_revoke = retrieve_documents(
            "What authentication is required for administrative accounts?",
            user_id="user_123",
            tenant_id="tenant_a",
            user_roles=[],
        )

        document_ids_before_revoke = [
            result.payload["document_id"]
            for result in results_before_revoke
        ]

        assert "policy_3" in document_ids_before_revoke

        # Revoke the user's direct access.
        client.set_payload(
            collection_name="documents",
            payload={
                "allowed_users": [],
            },
            points=[3],
        )

        results_after_revoke = retrieve_documents(
            "What authentication is required for administrative accounts?",
            user_id="user_123",
            tenant_id="tenant_a",
            user_roles=[],
        )

        document_ids_after_revoke = [
            result.payload["document_id"]
            for result in results_after_revoke
        ]

        assert "policy_3" not in document_ids_after_revoke

    finally:
        # Restore the original ACL.
        client.set_payload(
            collection_name="documents",
            payload=original_payload,
            points=[3],
        )