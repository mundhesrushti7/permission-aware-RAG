from src.rag.pipeline import answer_question


def test_answer_question():
    question = "How often should I change my password?"

    answer = answer_question(question)

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "90" in answer