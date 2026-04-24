from pathlib import Path

import easyocr

_reader: easyocr.Reader | None = None


def _get_reader(languages: list[str] = ["en", "pt"]) -> easyocr.Reader:
    global _reader

    if _reader is None:
        _reader = easyocr.Reader(languages, gpu=False)
    return _reader


def extract_text(image_path: Path, languages: list[str] = ["en", "pt"]) -> str:
    """Extrai texto de imagem via EasyOCR (OpenCV internamente)."""

    reader = _get_reader(languages)
    results = reader.readtext(str(image_path), detail=0)

    # results can be a list of strings
    return "\n".join([str(rows) for rows in results])
