import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from backend.ingestion.loader import _elements_to_text, load_document, load_text


def _mock_el(text: str) -> MagicMock:
    el = MagicMock()
    el.__str__ = lambda self: text
    return el


def test_elements_to_text_joins_non_empty():
    elements = [_mock_el("hello"), _mock_el("   "), _mock_el("world")]
    result = _elements_to_text(elements)
    assert "hello" in result
    assert "world" in result
    assert result.count("\n\n") == 1


def test_elements_to_text_all_empty_returns_empty():
    assert _elements_to_text([_mock_el("  "), _mock_el("")]) == ""


def test_load_document_unsupported_raises():
    with pytest.raises(ValueError, match="Tipo não suportado"):
        load_document(Path("arquivo.xyz"))


def test_load_pdf_returns_document():
    mock_pdf_mod = MagicMock()
    mock_pdf_mod.partition_pdf.return_value = [_mock_el("conteúdo PDF")]

    with patch.dict(sys.modules, {"unstructured.partition.pdf": mock_pdf_mod}):
        doc = load_document(Path("manual.pdf"))

    assert "conteúdo PDF" in doc.text
    assert doc.metadata["file_type"] == "pdf"
    assert doc.metadata["source"] == "manual.pdf"


def test_load_docx_returns_document():
    mock_docx_mod = MagicMock()
    mock_docx_mod.partition_docx.return_value = [_mock_el("conteúdo Word")]

    with patch.dict(sys.modules, {"unstructured.partition.docx": mock_docx_mod}):
        doc = load_document(Path("doc.docx"))

    assert "conteúdo Word" in doc.text
    assert doc.metadata["file_type"] == "docx"


def test_load_txt_file():
    txt_path = Path("notas.txt")
    with patch.object(Path, "read_text", return_value="texto simples"), \
         patch.object(Path, "stat") as mock_stat, \
         patch.object(Path, "exists", return_value=True):
        mock_stat.return_value.st_size = 100
        doc = load_document(txt_path)

    assert "texto simples" in doc.text
    assert doc.metadata["file_type"] == "txt"
    assert doc.metadata["source"] == "notas.txt"


def test_load_md_file():
    md_path = Path("readme.md")
    with patch.object(Path, "read_text", return_value="# Título\nConteúdo"), \
         patch.object(Path, "stat") as mock_stat, \
         patch.object(Path, "exists", return_value=True):
        mock_stat.return_value.st_size = 50
        doc = load_document(md_path)

    assert "Título" in doc.text
    assert doc.metadata["file_type"] == "md"
    assert doc.metadata["source"] == "readme.md"


def test_load_text_returns_document():
    doc = load_text("minha-lib", "conteúdo da documentação")
    assert "conteúdo da documentação" in doc.text


def test_load_text_metadata_fields():
    doc = load_text("fastapi-docs", "texto de exemplo com várias palavras aqui")
    assert doc.metadata["source"] == "fastapi-docs"
    assert doc.metadata["file_type"] == "text"
    assert doc.metadata["word_count"] == 7
    assert doc.metadata["file_size_bytes"] > 0
    assert "uploaded_at" in doc.metadata


def test_load_text_empty_title_still_works():
    doc = load_text("", "algum conteúdo")
    assert doc.metadata["source"] == ""


def test_load_txt_word_count_correct():
    words = "um dois três quatro cinco"
    with patch.object(Path, "read_text", return_value=words), \
         patch.object(Path, "stat") as mock_stat, \
         patch.object(Path, "exists", return_value=True):
        mock_stat.return_value.st_size = len(words)
        doc = load_document(Path("test.txt"))

    assert doc.metadata["word_count"] == 5
