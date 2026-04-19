import json
from unittest.mock import MagicMock, patch


def _make_point(source="doc.pdf", uploaded_at="2024-01-01T00:00:00", text="chunk content"):
    point = MagicMock()
    point.payload = {
        "source": source,
        "uploaded_at": uploaded_at,
        "_node_content": json.dumps({"text": text}),
    }
    return point


def _patch_client(points=None, scroll_side_effect=None):
    mock_client = MagicMock()
    if scroll_side_effect is not None:
        mock_client.scroll.side_effect = scroll_side_effect
    else:
        mock_client.scroll.return_value = (points or [], None)
    return patch("backend.indexing.documents._client", return_value=mock_client), mock_client


# ── list_documents ─────────────────────────────────────────────────────────────

def test_list_documents_empty():
    from backend.indexing.documents import list_documents

    ctx, _ = _patch_client([])
    with ctx:
        result = list_documents()

    assert result["total"] == 0
    assert result["items"] == []


def test_list_documents_deduplicates_by_source():
    from backend.indexing.documents import list_documents

    points = [_make_point("doc.pdf"), _make_point("doc.pdf"), _make_point("doc.pdf")]
    ctx, _ = _patch_client(points)
    with ctx:
        result = list_documents()

    assert result["total"] == 1
    assert result["items"][0]["source"] == "doc.pdf"


def test_list_documents_pagination():
    from backend.indexing.documents import list_documents

    points = [
        _make_point(f"doc{i}.pdf", f"2024-01-{i:02d}T00:00:00")
        for i in range(1, 26)
    ]
    ctx, _ = _patch_client(points)
    with ctx:
        result = list_documents(page=2, page_size=10)

    assert result["total"] == 25
    assert len(result["items"]) == 10


def test_list_documents_last_page_partial():
    from backend.indexing.documents import list_documents

    points = [
        _make_point(f"doc{i}.pdf", f"2024-01-{i:02d}T00:00:00")
        for i in range(1, 26)
    ]
    ctx, _ = _patch_client(points)
    with ctx:
        result = list_documents(page=3, page_size=10)

    assert result["total"] == 25
    assert len(result["items"]) == 5


def test_list_documents_search_filters():
    from backend.indexing.documents import list_documents

    points = [
        _make_point("manual-usuario.pdf", "2024-01-01T00:00:00"),
        _make_point("changelog.md", "2024-01-01T00:00:00"),
        _make_point("manual-dev.pdf", "2024-01-01T00:00:00"),
    ]
    ctx, _ = _patch_client(points)
    with ctx:
        result = list_documents(search="manual")

    assert result["total"] == 2
    sources = [i["source"] for i in result["items"]]
    assert "manual-usuario.pdf" in sources
    assert "manual-dev.pdf" in sources
    assert "changelog.md" not in sources


def test_list_documents_search_case_insensitive():
    from backend.indexing.documents import list_documents

    points = [_make_point("Manual.PDF")]
    ctx, _ = _patch_client(points)
    with ctx:
        result = list_documents(search="manual")

    assert result["total"] == 1


def test_list_documents_sorted_by_uploaded_at_desc():
    from backend.indexing.documents import list_documents

    points = [
        _make_point("antigo.pdf", "2023-01-01T00:00:00"),
        _make_point("novo.pdf", "2024-06-01T00:00:00"),
        _make_point("medio.pdf", "2024-01-01T00:00:00"),
    ]
    ctx, _ = _patch_client(points)
    with ctx:
        result = list_documents()

    sources = [i["source"] for i in result["items"]]
    assert sources[0] == "novo.pdf"
    assert sources[-1] == "antigo.pdf"


def test_list_documents_excludes_internal_fields():
    from backend.indexing.documents import list_documents

    points = [_make_point("doc.pdf")]
    ctx, _ = _patch_client(points)
    with ctx:
        result = list_documents()

    item = result["items"][0]
    assert "_node_content" not in item


def test_list_documents_returns_zero_on_exception():
    from backend.indexing.documents import list_documents

    ctx, mock_client = _patch_client()
    mock_client.scroll.side_effect = Exception("connection refused")
    with ctx:
        result = list_documents()

    assert result == {"total": 0, "items": []}


# ── get_document_content ───────────────────────────────────────────────────────

def test_get_document_content_concatenates_chunks():
    from backend.indexing.documents import get_document_content

    points = [
        _make_point(text="chunk 1"),
        _make_point(text="chunk 2"),
        _make_point(text="chunk 3"),
    ]
    ctx, _ = _patch_client(points)
    with ctx:
        content = get_document_content("doc.pdf")

    assert "chunk 1" in content
    assert "chunk 2" in content
    assert "chunk 3" in content
    assert "---" in content


def test_get_document_content_empty_source():
    from backend.indexing.documents import get_document_content

    ctx, _ = _patch_client([])
    with ctx:
        content = get_document_content("inexistente.pdf")

    assert content == ""


def test_get_document_content_filters_empty_text():
    from backend.indexing.documents import get_document_content

    point_with_text = _make_point(text="chunk 1")
    point_empty = MagicMock()
    point_empty.payload = {"_node_content": json.dumps({"text": ""})}
    point_no_content = MagicMock()
    point_no_content.payload = {}

    ctx, _ = _patch_client([point_with_text, point_empty, point_no_content])
    with ctx:
        content = get_document_content("doc.pdf")

    assert "chunk 1" in content
    assert content.count("---") == 0


# ── delete_document ────────────────────────────────────────────────────────────

def test_delete_document_returns_count():
    from backend.indexing.documents import delete_document

    points = [_make_point(), _make_point(), _make_point()]
    ctx, mock_client = _patch_client(points)
    with ctx:
        count = delete_document("doc.pdf")

    assert count == 3
    mock_client.delete.assert_called_once()


def test_delete_document_nonexistent_returns_zero():
    from backend.indexing.documents import delete_document

    ctx, mock_client = _patch_client([])
    with ctx:
        count = delete_document("nao-existe.pdf")

    assert count == 0
    mock_client.delete.assert_not_called()


def test_delete_document_calls_delete_with_filter():
    from backend.indexing.documents import delete_document
    from qdrant_client.models import FilterSelector

    points = [_make_point()]
    ctx, mock_client = _patch_client(points)
    with ctx:
        delete_document("doc.pdf")

    args, kwargs = mock_client.delete.call_args
    selector = kwargs.get("points_selector") or args[1]
    assert isinstance(selector, FilterSelector)
