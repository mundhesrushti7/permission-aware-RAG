from src.ingestion.loader import load_text_file


def test_load_text_file():
    text = load_text_file("data/sample_policy.txt")

    assert "Employees must change their password" in text