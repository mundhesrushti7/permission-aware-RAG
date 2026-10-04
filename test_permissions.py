import pytest

from qdrant_client import QdrantClient

from src.auth.permissions import revoke_user_access


client = QdrantClient(url="http://localhost:6333")


def get_document(document_id: str):
    records, _ = client.scroll(
        collection_name="documents",
        scroll_filter=None,
        limit=100,
        with_payload=True,
        with_vectors=False,
    )

    for record in records:
        if record.payload.get("document_id") == document_id:
            return record

    return None


def test_admin_can_revoke_user_access():
    document = get_document("policy_3")
    assert document is not None

    original_users = document.payload.get("allowed_users", [])

    try:
        client.set_payload(
            collection_name="documents",
            payload={"allowed_users": ["user_123"]},
            points=[document.id],
        )

        revoke_user_access(
            document_id="policy_3",
            target_user_id="user_123",
            actor_user_id="admin_1",
            actor_tenant_id="tenant_a",
            actor_roles=["admin"],
        )

        updated = get_document("policy_3")
        assert updated.payload["allowed_users"] == []

    finally:
        client.set_payload(
            collection_name="documents",
            payload={"allowed_users": original_users},
            points=[document.id],
        )


def test_non_admin_cannot_revoke():
    with pytest.raises(PermissionError):
        revoke_user_access(
            document_id="policy_3",
            target_user_id="user_123",
            actor_user_id="employee_1",
            actor_tenant_id="tenant_a",
            actor_roles=["employee"],
        )


def test_admin_cannot_modify_another_tenant():
    document = get_document("policy_4")
    assert document is not None

    original_users = document.payload.get("allowed_users", [])

    try:
        client.set_payload(
            collection_name="documents",
            payload={"allowed_users": ["user_123"]},
            points=[document.id],
        )

        with pytest.raises(PermissionError):
            revoke_user_access(
                document_id="policy_4",
                target_user_id="user_123",
                actor_user_id="admin_1",
                actor_tenant_id="tenant_a",
                actor_roles=["admin"],
            )

        unchanged = get_document("policy_4")

        assert unchanged.payload["allowed_users"] == ["user_123"]

    finally:
        client.set_payload(
            collection_name="documents",
            payload={"allowed_users": original_users},
            points=[document.id],
        )


def test_revoke_is_idempotent():
    document = get_document("policy_3")
    assert document is not None

    original_users = document.payload.get("allowed_users", [])

    try:
        client.set_payload(
            collection_name="documents",
            payload={"allowed_users": []},
            points=[document.id],
        )

        revoke_user_access(
            document_id="policy_3",
            target_user_id="user_123",
            actor_user_id="admin_1",
            actor_tenant_id="tenant_a",
            actor_roles=["admin"],
        )

        updated = get_document("policy_3")
        assert updated.payload["allowed_users"] == []

    finally:
        client.set_payload(
            collection_name="documents",
            payload={"allowed_users": original_users},
            points=[document.id],
        )


def test_nonexistent_document_is_rejected():
    with pytest.raises(ValueError):
        revoke_user_access(
            document_id="does_not_exist",
            target_user_id="user_123",
            actor_user_id="admin_1",
            actor_tenant_id="tenant_a",
            actor_roles=["admin"],
        )
