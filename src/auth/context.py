from src.auth.jwt import decode_token


def get_tenant_id(token: str) -> str:
    """
    Extract the tenant ID from a verified JWT.
    """

    payload = decode_token(token)

    tenant_id = payload["tenant_id"]

    return tenant_id