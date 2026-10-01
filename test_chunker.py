import pytest
from src.ingestion.chunker import chunk_text

def test_chunker_rejects_invalid_overlap():
    text = "One two three four five six seven eight."

    with pytest.raises(ValueError):
        chunk_text(
            text,
            chunk_size=8,
            overlap=8,
        )
        
def test_chunker_creates_chunks():
    text = """
    One two three four five six seven eight nine ten.
    Eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty.
    """

    chunks = chunk_text(
        text,
        chunk_size=8,
        overlap=2,
    )

    assert len(chunks) > 1


def test_chunker_has_overlap():
    text = """
    One two three four five six seven eight nine ten.
    Eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty.
    """

    chunks = chunk_text(
        text,
        chunk_size=8,
        overlap=2,
    )

    first_chunk_tokens = chunks[0].split()
    second_chunk_tokens = chunks[1].split()

    assert first_chunk_tokens[-2:] == second_chunk_tokens[:2]


