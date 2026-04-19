from datetime import UTC, datetime
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".doc", ".txt", ".md"}


def _elements_to_text(elements: list) -> str:
    return "\n\n".join(str(el) for el in elements if str(el).strip())


def _metadata(path: Path, file_type: str, text: str) -> dict:
    return {
        "source": path.name,
        "file_type": file_type,
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
        "uploaded_at": datetime.now(UTC).isoformat(),
        "word_count": len(text.split()),
    }


def load_pdf(path: Path):
    from llama_index.core import Document
    from unstructured.partition.pdf import partition_pdf

    elements = partition_pdf(filename=str(path), languages=["por", "eng"])
    text = _elements_to_text(elements)
    return Document(text=text, metadata=_metadata(path, "pdf", text))


def load_docx(path: Path):
    from llama_index.core import Document
    from unstructured.partition.docx import partition_docx

    elements = partition_docx(filename=str(path), languages=["por", "eng"])
    text = _elements_to_text(elements)
    return Document(text=text, metadata=_metadata(path, "docx", text))


def load_txt(path: Path):
    from llama_index.core import Document

    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower().lstrip(".")
    return Document(text=text, metadata=_metadata(path, suffix, text))


def load_text(title: str, content: str):
    """Indexa texto puro usando title como identificador de source."""
    from llama_index.core import Document

    meta = {
        "source": title,
        "file_type": "text",
        "file_size_bytes": len(content.encode()),
        "uploaded_at": datetime.now(UTC).isoformat(),
        "word_count": len(content.split()),
    }
    return Document(text=content, metadata=meta)


def load_document(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)

    if suffix in (".docx", ".doc"):
        return load_docx(path)

    if suffix in (".txt", ".md"):
        return load_txt(path)
    raise ValueError(f"Tipo não suportado: {suffix}. Use: {SUPPORTED}")
