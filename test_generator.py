from src.generation.generator import generate_answer


def test_generate_answer():
    prompt = """
    Context:
    Employees must change their password every 90 days.

    Question:
    How often should employees change their password?

    Answer:
    """

    answer = generate_answer(prompt)

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "90" in answer