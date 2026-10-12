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
    Deny access if required metadata is missing or malformed.
    """

    # A document must have a tenant ID.
    document_tenant_id = document.get("tenant_id")

    if not isinstance(document_tenant_id, str) or not document_tenant_id:
        return False

    # Tenant isolation must be checked before other permissions.
    if not is_tenant_allowed(
        document_tenant_id,
        user_tenant_id,
    ):
        return False

    # Permission lists must be lists of strings.
    allowed_users = document.get("allowed_users", [])
    allowed_roles = document.get("allowed_roles", [])

    if not isinstance(allowed_users, list):
        return False

    if not isinstance(allowed_roles, list):
        return False

    if not all(isinstance(user, str) for user in allowed_users):
        return False

    if not all(isinstance(role, str) for role in allowed_roles):
        return False

    # Explicit user permission grants access.
    if user_id in allowed_users:
        return True

    # A matching role also grants access.
    if any(role in allowed_roles for role in user_roles):
        return True

    # Deny access by default.
    return False
