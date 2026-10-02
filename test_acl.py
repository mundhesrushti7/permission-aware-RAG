from src.auth.acl import is_tenant_allowed


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