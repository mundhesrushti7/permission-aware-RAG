from transformers import AutoTokenizer


tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Document text to split.
        chunk_size: Maximum number of tokens per chunk.
        overlap: Number of tokens shared between consecutive chunks.

    Returns:
        A list of text chunks.
    """

    if chunk_size <= 0:
     raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
     raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
     raise ValueError("overlap must be smaller than chunk_size")
    tokens = tokenizer.encode(
        text,
        add_special_tokens=False,
    )

    chunks = []

    start = 0

    while start < len(tokens):
        end = start + chunk_size

        chunk = tokens[start:end]

        chunks.append(chunk)

        if end >= len(tokens):
            break

        start = end - overlap

    decoded_chunks = []

    for chunk in chunks:
        decoded_chunk = tokenizer.decode(chunk)
        decoded_chunks.append(decoded_chunk)

    return decoded_chunks