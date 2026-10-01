from pathlib import Path


def load_text_file(file_path: str) -> str:
    """
    Read a text file and return its contents as a string.
    """
    path = Path(file_path)

    return path.read_text(encoding="utf-8")