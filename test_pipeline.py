from src.ingestion.pipeline import ingest_text_file


def test_ingest_text_file():
    chunks = ingest_text_file(
        "data/sample_policy.txt",
        chunk_size=20,
        overlap=5,
    )

    assert len(chunks) > 1
    assert all(isinstance(chunk, str) for chunk in chunks)