from pathlib import Path


def decode_text_or_bytes(path: Path) -> str | bytes:
    assert path.is_file()
    with path.open("r") as f:
        try:
            return f.read()
        except UnicodeDecodeError:
            return path.read_bytes()
