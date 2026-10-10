from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

from src.api.main import app
from src.auth.identity import (
    assign_role_to_user,
    create_role,
    create_tenant,
    create_user,
)
from src.db.connection import get_connection


client = TestClient(app)
qdrant = QdrantClient(url="http://localhost:6333")


TEST_TENANT_A = "tenant_a"
TEST_TENANT_B = "api-permission-test-tenant-b"

ADMIN_ROLE_ID = "api-permission-admin-role"
EMPLOYEE_ROLE_ID = "api-permission-employee-role"

ADMIN_A_ID = "api-permission-admin-a"
EMPLOYEE_A_ID = "api-permission-employee-a"
ADMIN_B_ID = "api-permission-admin-b"

ADMIN_A_USERNAME = "api_permission_admin_a"
EMPLOYEE_A_USERNAME = "api_permission_employee_a"
ADMIN_B_USERNAME = "api_permission_admin_b"

TEST_PASSWORD = "CorrectPassword123!"

TEST_DOCUMENT_ID = "policy_3"
TEST_TARGET_USER_ID = EMPLOYEE_A_ID



def setup_test_users():
    # Reuse tenant_a because it already exists in the database.
    create_tenant(
        TEST_TENANT_B,
        "API Permission Test Tenant B",
    )

    create_role(
        ADMIN_ROLE_ID,
        "admin",
    )

    create_role(
        EMPLOYEE_ROLE_ID,
        "employee",
    )

    create_user(
        ADMIN_A_ID,
        ADMIN_A_USERNAME,
        TEST_PASSWORD,
        TEST_TENANT_A,
    )

    create_user(
        EMPLOYEE_A_ID,
        EMPLOYEE_A_USERNAME,
        TEST_PASSWORD,
        TEST_TENANT_A,
    )

    create_user(
        ADMIN_B_ID,
        ADMIN_B_USERNAME,
        TEST_PASSWORD,
        TEST_TENANT_B,
    )

    assign_role_to_user(
        ADMIN_A_ID,
        ADMIN_ROLE_ID,
    )

    assign_role_to_user(
        EMPLOYEE_A_ID,
        EMPLOYEE_ROLE_ID,
    )

    assign_role_to_user(
        ADMIN_B_ID,
        ADMIN_ROLE_ID,
    )



def cleanup_test_users():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_roles WHERE user_id IN (%s, %s, %s)",
                (
                    ADMIN_A_ID,
                    EMPLOYEE_A_ID,
                    ADMIN_B_ID,
                ),
            )

            cursor.execute(
                "DELETE FROM users WHERE id IN (%s, %s, %s)",
                (
                    ADMIN_A_ID,
                    EMPLOYEE_A_ID,
                    ADMIN_B_ID,
                ),
            )

            cursor.execute(
                "DELETE FROM roles WHERE id IN (%s, %s)",
                (
                    ADMIN_ROLE_ID,
                    EMPLOYEE_ROLE_ID,
                ),
            )

            cursor.execute(
                "DELETE FROM tenants WHERE id = %s",
                (TEST_TENANT_B,),
            )

        conn.commit()

    finally:
        conn.close()


def get_test_document():
    records, _ = qdrant.scroll(
        collection_name="documents",
        scroll_filter=None,
        limit=100,
        with_payload=True,
        with_vectors=False,
    )

    for record in records:
        if record.payload.get("document_id") == TEST_DOCUMENT_ID:
            return record

    return None


def get_permission_audit_count() -> int:
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM permission_audit_logs
                WHERE actor_user_id = %s
                  AND document_id = %s
                  AND target_user_id = %s
                  AND action = %s
                """,
                (
                    ADMIN_A_ID,
                    TEST_DOCUMENT_ID,
                    TEST_TARGET_USER_ID,
                    "revoke_user_access",
                ),
            )

            return cursor.fetchone()[0]

    finally:
        conn.close()



def test_admin_can_revoke_user_access_via_api():
    setup_test_users()

    original_allowed_users = None

    try:
        # 1. Get the document and save its original permissions
        document = get_test_document()
        assert document is not None

        original_allowed_users = document.payload.get("allowed_users", [])

        # 2. Count matching audit records before the API call
        audit_count_before = get_permission_audit_count()

        # 3. Log in as an administrator
        login_response = client.post(
            "/login",
            json={
                "username": ADMIN_A_USERNAME,
                "password": TEST_PASSWORD,
            },
        )

        assert login_response.status_code == 200

        access_token = login_response.json()["access_token"]

        # 4. Call the permission-revocation API
        response = client.post(
            f"/documents/{TEST_DOCUMENT_ID}/permissions/revoke",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "target_user_id": TEST_TARGET_USER_ID,
            },
        )

        assert response.status_code == 200

        assert response.json() == {
            "message": "User access revoked successfully.",
            "document_id": TEST_DOCUMENT_ID,
            "target_user_id": TEST_TARGET_USER_ID,
        }

        # 5. Verify that the user's access was removed in Qdrant
        updated_document = get_test_document()
        assert updated_document is not None

        updated_allowed_users = updated_document.payload.get(
            "allowed_users", []
        )

        assert TEST_TARGET_USER_ID not in updated_allowed_users

        # 6. Verify that an audit record was created
        audit_count_after = get_permission_audit_count()

        assert audit_count_after == audit_count_before + 1

    finally:
        # 7. Restore the original permissions so the test is repeatable
        if original_allowed_users is not None:
            document = get_test_document()

            if document is not None:
                qdrant.set_payload(
                    collection_name="documents",
                    payload={
                        "allowed_users": original_allowed_users,
                    },
                    points=[document.id],
                )

        # 8. Remove the test users and related database records
        cleanup_test_users()



def test_unauthenticated_user_cannot_revoke_access():
    response = client.post(
        f"/documents/{TEST_DOCUMENT_ID}/permissions/revoke",
        json={"target_user_id": TEST_TARGET_USER_ID},
    )

    assert response.status_code == 401


def test_employee_cannot_revoke_access():
    setup_test_users()

    try:
        login_response = client.post(
            "/login",
            json={
                "username": EMPLOYEE_A_USERNAME,
                "password": TEST_PASSWORD,
            },
        )

        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]

        response = client.post(
            f"/documents/{TEST_DOCUMENT_ID}/permissions/revoke",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"target_user_id": TEST_TARGET_USER_ID},
        )

        assert response.status_code == 403

    finally:
        cleanup_test_users()


def test_admin_cannot_revoke_access_to_another_tenants_document():
    setup_test_users()

    try:
        login_response = client.post(
            "/login",
            json={
                "username": ADMIN_A_USERNAME,
                "password": TEST_PASSWORD,
            },
        )

        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]

        # policy_4 belongs to tenant_b, but this admin belongs to tenant_a.
        response = client.post(
            "/documents/policy_4/permissions/revoke",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"target_user_id": TEST_TARGET_USER_ID},
        )

        assert response.status_code == 403

    finally:
        cleanup_test_users()


def test_revoking_access_to_nonexistent_document_returns_404():
    setup_test_users()

    try:
        login_response = client.post(
            "/login",
            json={
                "username": ADMIN_A_USERNAME,
                "password": TEST_PASSWORD,
            },
        )

        assert login_response.status_code == 200
        access_token = login_response.json()["access_token"]

        response = client.post(
            "/documents/nonexistent-api-test-document/permissions/revoke",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"target_user_id": TEST_TARGET_USER_ID},
        )

        assert response.status_code == 404

    finally:
        cleanup_test_users()
