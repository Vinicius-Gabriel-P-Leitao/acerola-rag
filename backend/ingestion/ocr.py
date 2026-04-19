from pathlib import Path
from typing import List, Optional

import easyocr

_reader: Optional[easyocr.Reader] = None


def _get_reader(languages: List[str] = ["en", "pt"]) -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(languages, gpu=False)
    return _reader


def extract_text(image_path: Path, languages: List[str] = ["en", "pt"]) -> str:
    """Extrai texto de imagem via EasyOCR (OpenCV internamente)."""
    reader = _get_reader(languages)
    results = reader.readtext(str(image_path), detail=0)
    # results can be a list of strings
    return "\n".join([str(r) for r in results])
