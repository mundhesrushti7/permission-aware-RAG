def is_tenant_allowed(
    document_tenant_id: str,
    user_tenant_id: str,
) -> bool:
    """
    Check whether a document belongs to the user's tenant.
    """
    return document_tenant_id == user_tenant_id


def is_document_allowed(
    document: dict,
    user_id: str,
    user_tenant_id: str,
    user_roles: list[str],
) -> bool:
    """
    Check whether a user is authorized to access a document.
    """

    if not is_tenant_allowed(
        document["tenant_id"],
        user_tenant_id,
    ):
        return False

    allowed_users = document.get("allowed_users", [])
    allowed_roles = document.get("allowed_roles", [])

    if user_id in allowed_users:
        return True

    if any(role in allowed_roles for role in user_roles):
        return True

    return False



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