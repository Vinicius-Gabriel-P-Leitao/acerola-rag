from unittest.mock import MagicMock, patch


def _make_collection(metadatas=None, documents=None, ids=None):
    col = MagicMock()
    col.get.return_value = {
        "metadatas": metadatas or [],
        "documents": documents or [],
        "ids": ids or [],
    }
    return col


def _patch_col(col):
    return patch("backend.indexing.documents._collection", return_value=col)


def test_list_documents_empty():
    from backend.indexing.documents import list_documents

    col = _make_collection()
    with _patch_col(col):
        result = list_documents()

    assert result["total"] == 0
    assert result["items"] == []


def test_list_documents_deduplicates_by_source():
    from backend.indexing.documents import list_documents

    metas = [
        {"source": "doc.pdf", "uploaded_at": "2024-01-01T00:00:00"},
        {"source": "doc.pdf", "uploaded_at": "2024-01-01T00:00:00"},
        {"source": "doc.pdf", "uploaded_at": "2024-01-01T00:00:00"},
    ]
    col = _make_collection(metadatas=metas)
    with _patch_col(col):
        result = list_documents()

    assert result["total"] == 1
    assert result["items"][0]["source"] == "doc.pdf"


def test_list_documents_pagination():
    from backend.indexing.documents import list_documents

    metas = [
        {"source": f"doc{i}.pdf", "uploaded_at": f"2024-01-{i:02d}T00:00:00"}
        for i in range(1, 26)
    ]
    col = _make_collection(metadatas=metas)
    with _patch_col(col):
        result = list_documents(page=2, page_size=10)

    assert result["total"] == 25
    assert len(result["items"]) == 10


def test_list_documents_last_page_partial():
    from backend.indexing.documents import list_documents

    metas = [
        {"source": f"doc{i}.pdf", "uploaded_at": f"2024-01-{i:02d}T00:00:00"}
        for i in range(1, 26)
    ]
    col = _make_collection(metadatas=metas)
    with _patch_col(col):
        result = list_documents(page=3, page_size=10)

    assert result["total"] == 25
    assert len(result["items"]) == 5


def test_list_documents_search_filters():
    from backend.indexing.documents import list_documents

    metas = [
        {"source": "manual-usuario.pdf", "uploaded_at": "2024-01-01T00:00:00"},
        {"source": "changelog.md", "uploaded_at": "2024-01-01T00:00:00"},
        {"source": "manual-dev.pdf", "uploaded_at": "2024-01-01T00:00:00"},
    ]
    col = _make_collection(metadatas=metas)
    with _patch_col(col):
        result = list_documents(search="manual")

    assert result["total"] == 2
    sources = [i["source"] for i in result["items"]]
    assert "manual-usuario.pdf" in sources
    assert "manual-dev.pdf" in sources
    assert "changelog.md" not in sources


def test_list_documents_search_case_insensitive():
    from backend.indexing.documents import list_documents

    metas = [{"source": "Manual.PDF", "uploaded_at": "2024-01-01T00:00:00"}]
    col = _make_collection(metadatas=metas)
    with _patch_col(col):
        result = list_documents(search="manual")

    assert result["total"] == 1


def test_list_documents_sorted_by_uploaded_at_desc():
    from backend.indexing.documents import list_documents

    metas = [
        {"source": "antigo.pdf", "uploaded_at": "2023-01-01T00:00:00"},
        {"source": "novo.pdf", "uploaded_at": "2024-06-01T00:00:00"},
        {"source": "medio.pdf", "uploaded_at": "2024-01-01T00:00:00"},
    ]
    col = _make_collection(metadatas=metas)
    with _patch_col(col):
        result = list_documents()

    sources = [i["source"] for i in result["items"]]
    assert sources[0] == "novo.pdf"
    assert sources[-1] == "antigo.pdf"


def test_get_document_content_concatenates_chunks():
    from backend.indexing.documents import get_document_content

    col = _make_collection(documents=["chunk 1", "chunk 2", "chunk 3"])
    with _patch_col(col):
        content = get_document_content("doc.pdf")

    assert "chunk 1" in content
    assert "chunk 2" in content
    assert "chunk 3" in content
    assert "---" in content


def test_get_document_content_empty_source():
    from backend.indexing.documents import get_document_content

    col = _make_collection(documents=[])
    with _patch_col(col):
        content = get_document_content("inexistente.pdf")

    assert content == ""


def test_get_document_content_filters_empty_chunks():
    from backend.indexing.documents import get_document_content

    col = _make_collection(documents=["chunk 1", "", "chunk 3"])
    with _patch_col(col):
        content = get_document_content("doc.pdf")

    assert "chunk 1" in content
    assert "chunk 3" in content


def test_delete_document_calls_collection_delete():
    from backend.indexing.documents import delete_document

    col = _make_collection(ids=["id1", "id2", "id3"])
    with _patch_col(col):
        count = delete_document("doc.pdf")

    col.delete.assert_called_once_with(ids=["id1", "id2", "id3"])
    assert count == 3


def test_delete_document_returns_count():
    from backend.indexing.documents import delete_document

    col = _make_collection(ids=["a", "b"])
    with _patch_col(col):
        count = delete_document("qualquer.pdf")

    assert count == 2


def test_delete_document_nonexistent_returns_zero():
    from backend.indexing.documents import delete_document

    col = _make_collection(ids=[])
    with _patch_col(col):
        count = delete_document("nao-existe.pdf")

    col.delete.assert_not_called()
    assert count == 0
