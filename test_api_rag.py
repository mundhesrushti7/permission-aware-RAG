from fastapi.testclient import TestClient

from src.api.main import app
from src.auth.identity import (
    assign_role_to_user,
    create_role,
    create_tenant,
    create_user,
)
from src.db.connection import get_connection


client = TestClient(app)

TEST_TENANT_ID = "tenant_a"
TEST_ROLE_ID = "rag-api-test-role"
TEST_USER_ID = "rag-api-test-user"
TEST_USERNAME = "rag_api_test_user"
TEST_PASSWORD = "CorrectPassword123!"


def setup_test_user():
    create_tenant(TEST_TENANT_ID, "Tenant A")
    create_role(TEST_ROLE_ID, "employee")
    create_user(
        TEST_USER_ID,
        TEST_USERNAME,
        TEST_PASSWORD,
        TEST_TENANT_ID,
    )
    assign_role_to_user(TEST_USER_ID, TEST_ROLE_ID)


def cleanup_test_user():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_roles WHERE user_id = %s",
                (TEST_USER_ID,),
            )
            cursor.execute(
                "DELETE FROM users WHERE id = %s",
                (TEST_USER_ID,),
            )
            cursor.execute(
                "DELETE FROM roles WHERE id = %s",
                (TEST_ROLE_ID,),
            )
            cursor.execute(
                "DELETE FROM tenants WHERE id = %s",
                (TEST_TENANT_ID,),
            )

        conn.commit()

    finally:
        conn.close()


def test_real_query_pipeline():
    setup_test_user()

    try:
        login_response = client.post(
            "/login",
            json={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
            },
        )

        assert login_response.status_code == 200

        access_token = login_response.json()["access_token"]

        response = client.post(
            "/query",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            json={
                "question": "How often must employees change their password?",
            },
        )

        assert response.status_code == 200

        answer = response.json()["answer"]

        assert isinstance(answer, str)
        assert len(answer) > 0

    finally:
        cleanup_test_user()


def test_real_acl_filtering():
    setup_test_user()

    try:
        from src.rag.pipeline import retrieve_documents

        results = retrieve_documents(
            question="How often must employees change their password?",
            user_id=TEST_USER_ID,
            tenant_id=TEST_TENANT_ID,
            user_roles=["employee"],
        )

        returned_document_ids = {
            result.payload["document_id"]
            for result in results
        }

        assert returned_document_ids == {
            "policy_1",
            "policy_2",
        }

        for result in results:
            document = result.payload

            assert document["tenant_id"] == TEST_TENANT_ID
            assert "employee" in document["allowed_roles"]

    finally:
        cleanup_test_user()