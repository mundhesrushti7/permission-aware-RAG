from src.rag.pipeline import answer_question


def test_answer_question():
    question = "How often should I change my password?"

    answer = answer_question(
        question,
        tenant_id="tenant_a",
    )

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "90" in answer


def test_tenant_isolation():
    question = "When do employees receive their salary?"

    answer = answer_question(
        question,
        tenant_id="tenant_a",
    )

    assert "last working day" not in answer.lower()