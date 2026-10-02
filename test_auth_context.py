from src.auth.context import get_tenant_id
from src.auth.jwt import create_token


def test_get_tenant_id():
    token = create_token(
        "user_123",
        "tenant_a",
        ["employee"],
    )

    tenant_id = get_tenant_id(token)

    assert tenant_id == "tenant_a"