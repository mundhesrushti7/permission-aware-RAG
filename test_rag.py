from src.rag.pipeline import answer_question, retrieve_documents


def test_answer_question():
    question = "How often should I change my password?"

    answer = answer_question(
        question,
        user_id="user_123",
        tenant_id="tenant_a",
        user_roles=["employee"],
    )

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "90" in answer


def test_tenant_isolation():
    question = "When do employees receive their salary?"

    answer = answer_question(
        question,
        user_id="user_123",
        tenant_id="tenant_a",
        user_roles=["employee"],
    )

    assert "last working day" not in answer.lower()


def test_retrieved_documents_are_tenant_isolated():
    question = "When do employees receive their salary?"

    results = retrieve_documents(
        question,
        user_id="user_123",
        tenant_id="tenant_a",
        user_roles=["employee"],
    )

    retrieved_tenant_ids = [
        result.payload["tenant_id"]
        for result in results
    ]

    assert all(
        tenant_id == "tenant_a"
        for tenant_id in retrieved_tenant_ids
    )


def test_role_restricted_document_is_not_retrieved():
    question = "What authentication is required for administrative accounts?"

    results = retrieve_documents(
        question,
        user_id="user_123",
        tenant_id="tenant_a",
        user_roles=["employee"],
    )

    retrieved_document_ids = [
        result.payload["document_id"]
        for result in results
    ]

    assert "policy_3" not in retrieved_document_ids