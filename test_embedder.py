from src.embeddings.embedder import embed_texts


def test_embed_texts():
    texts = [
        "Employees must change their password every 90 days.",
        "Passwords must contain at least 12 characters.",
    ]

    embeddings = embed_texts(texts)

    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] == 384