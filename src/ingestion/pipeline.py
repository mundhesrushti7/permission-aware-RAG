from src.ingestion.loader import load_text_file
from src.ingestion.chunker import chunk_text

def ingest_text_file(
    file_path: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Load a text file and split it into chunks.
    """

    text = load_text_file(file_path)

    chunks = chunk_text(
        text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    return chunks