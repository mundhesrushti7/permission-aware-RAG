from src.auth.acl import (
    is_tenant_allowed,
    is_document_allowed,
)


def test_same_tenant_is_allowed():
    assert is_tenant_allowed(
        "tenant_a",
        "tenant_a",
    )


def test_different_tenant_is_rejected():
    assert not is_tenant_allowed(
        "tenant_b",
        "tenant_a",
    )



def test_allowed_role_can_access_document():
    document = {
        "tenant_id": "tenant_a",
        "allowed_users": [],
        "allowed_roles": ["employee"],
    }

    assert is_document_allowed(
        document,
        user_id="user_123",
        user_tenant_id="tenant_a",
        user_roles=["employee"],
    )


def test_wrong_role_cannot_access_document():
    document = {
        "tenant_id": "tenant_a",
        "allowed_users": [],
        "allowed_roles": ["admin"],
    }

    assert not is_document_allowed(
        document,
        user_id="user_123",
        user_tenant_id="tenant_a",
        user_roles=["employee"],
    )


def test_allowed_user_can_access_document():
    document = {
        "tenant_id": "tenant_a",
        "allowed_users": ["user_123"],
        "allowed_roles": [],
    }

    assert is_document_allowed(
        document,
        user_id="user_123",
        user_tenant_id="tenant_a",
        user_roles=["employee"],
    )


def test_wrong_user_cannot_access_document():
    document = {
        "tenant_id": "tenant_a",
        "allowed_users": ["user_123"],
        "allowed_roles": [],
    }

    assert not is_document_allowed(
        document,
        user_id="user_456",
        user_tenant_id="tenant_a",
        user_roles=["employee"],
    )


def test_matching_role_cannot_cross_tenant():
    document = {
        "tenant_id": "tenant_b",
        "allowed_users": [],
        "allowed_roles": ["employee"],
    }

    assert not is_document_allowed(
        document,
        user_id="user_123",
        user_tenant_id="tenant_a",
        user_roles=["employee"],
    )