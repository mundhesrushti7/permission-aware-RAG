import pytest

from qdrant_client import QdrantClient
from src.db.connection import get_connection
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


def get_permission_audit_count() -> int:
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM permission_audit_logs"
            )
            return cursor.fetchone()[0]
    finally:
        conn.close()



def get_latest_permission_audit():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT request_id,
                       actor_user_id,
                       tenant_id,
                       document_id,
                       target_user_id,
                       action,
                       timestamp
                FROM permission_audit_logs
                ORDER BY timestamp DESC
                LIMIT 1
                """
            )
            return cursor.fetchone()
    finally:
        conn.close()


def test_admin_can_revoke_user_access():
    document = get_document("policy_3")
    assert document is not None

    original_users = document.payload.get("allowed_users", [])
    audit_count_before = get_permission_audit_count()

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

        audit_count_after = get_permission_audit_count()

        assert audit_count_after == audit_count_before + 1

        audit_record = get_latest_permission_audit()
        assert audit_record is not None

        (
            request_id,
            actor_user_id,
            tenant_id,
            document_id,
            target_user_id,
            action,
            timestamp,
        ) = audit_record

        assert request_id is not None
        assert actor_user_id == "admin_1"
        assert tenant_id == "tenant_a"
        assert document_id == "policy_3"
        assert target_user_id == "user_123"
        assert action == "revoke_user_access"
        assert timestamp is not None

    finally:
        client.set_payload(
            collection_name="documents",
            payload={"allowed_users": original_users},
            points=[document.id],
        )


def test_non_admin_cannot_revoke():
    audit_count_before = get_permission_audit_count()

    with pytest.raises(PermissionError):
        revoke_user_access(
            document_id="policy_3",
            target_user_id="user_123",
            actor_user_id="employee_1",
            actor_tenant_id="tenant_a",
            actor_roles=["employee"],
        )

    audit_count_after = get_permission_audit_count()

    assert audit_count_after == audit_count_before


def test_admin_cannot_modify_another_tenant():
    document = get_document("policy_4")
    assert document is not None

    original_users = document.payload.get("allowed_users", [])
    audit_count_before = get_permission_audit_count()

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

        audit_count_after = get_permission_audit_count()

        assert audit_count_after == audit_count_before

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
    audit_count_before = get_permission_audit_count()

    with pytest.raises(ValueError):
        revoke_user_access(
            document_id="does_not_exist",
            target_user_id="user_123",
            actor_user_id="admin_1",
            actor_tenant_id="tenant_a",
            actor_roles=["admin"],
        )

    audit_count_after = get_permission_audit_count()

    assert audit_count_after == audit_count_before