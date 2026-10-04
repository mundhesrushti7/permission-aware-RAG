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
