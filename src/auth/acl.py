def is_tenant_allowed(
    document_tenant_id: str,
    user_tenant_id: str,
) -> bool:
    """
    Check whether a document belongs to the user's tenant.
    """
    return document_tenant_id == user_tenant_id