from pathlib import Path
from unittest.mock import MagicMock, patch

import backend.ingestion.ocr as ocr_module
from backend.ingestion.ocr import extract_text


def setup_function():
    ocr_module._reader = None


@patch("backend.ingestion.ocr.easyocr.Reader")
def test_extract_text_joins_lines(mock_cls):
    mock_reader = MagicMock()
    mock_reader.readtext.return_value = ["Hello", "World"]
    mock_cls.return_value = mock_reader

    result = extract_text(Path("img.png"))
    assert result == "Hello\nWorld"


@patch("backend.ingestion.ocr.easyocr.Reader")
def test_reader_singleton(mock_cls):
    """Reader é instanciado uma única vez (singleton)."""
    mock_reader = MagicMock()
    mock_reader.readtext.return_value = []
    mock_cls.return_value = mock_reader

    ocr_module._reader = None
    extract_text(Path("a.png"))
    extract_text(Path("b.png"))
    assert mock_cls.call_count == 1
