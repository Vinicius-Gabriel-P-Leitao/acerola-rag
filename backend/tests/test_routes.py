from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from backend.api.routes import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return TestClient(app)


# ── /documents list ───────────────────────────────────────────────────────────

def test_list_documents_endpoint(client):
    with patch(
        "backend.api.routes.list_documents",
        return_value={"total": 2, "items": [{"source": "a.pdf"}, {"source": "b.pdf"}]},
    ) as mock_list:
        # need to patch the import inside routes
        pass

    with patch("backend.indexing.documents.list_documents", return_value={"total": 0, "items": []}):
        r = client.get("/api/v1/documents")
    assert r.status_code == 200
    assert "total" in r.json()
    assert "items" in r.json()


def test_list_documents_pagination_params(client):
    with patch("backend.indexing.documents.list_documents", return_value={"total": 0, "items": []}) as m:
        client.get("/api/v1/documents?page=2&page_size=5&search=foo")
        m.assert_called_once_with(page=2, page_size=5, search="foo")


def test_list_documents_default_params(client):
    with patch("backend.indexing.documents.list_documents", return_value={"total": 0, "items": []}) as m:
        client.get("/api/v1/documents")
        m.assert_called_once_with(page=1, page_size=20, search="")


# ── /documents/{source}/content ───────────────────────────────────────────────

def test_get_document_content_endpoint(client):
    with patch("backend.indexing.documents.get_document_content", return_value="conteúdo aqui"):
        r = client.get("/api/v1/documents/meu-doc.pdf/content")
    assert r.status_code == 200
    assert r.json()["content"] == "conteúdo aqui"
    assert r.json()["source"] == "meu-doc.pdf"


def test_get_document_content_not_found(client):
    with patch("backend.indexing.documents.get_document_content", return_value=""):
        r = client.get("/api/v1/documents/inexistente.pdf/content")
    assert r.status_code == 404


# ── DELETE /documents/{source} ────────────────────────────────────────────────

def test_delete_document_endpoint(client):
    with patch("backend.indexing.documents.delete_document", return_value=5), \
         patch("backend.rag.engine.refresh_engine"):
        r = client.delete("/api/v1/documents/doc.pdf")
    assert r.status_code == 200
    assert r.json()["deleted_chunks"] == 5


# ── /upload ───────────────────────────────────────────────────────────────────

def _make_file(name: str, content: bytes = b"data"):
    return ("files", (name, BytesIO(content), "application/octet-stream"))


def test_upload_exceeds_limit_returns_400(client):
    with patch("backend.config.settings.max_upload_files", 2):
        files = [_make_file(f"doc{i}.pdf") for i in range(3)]
        r = client.post("/api/v1/upload", files=files)
    assert r.status_code == 400


def test_upload_txt_accepted(client):
    with patch("backend.config.settings.upload_dir") as mock_dir, \
         patch("backend.api.ingestion_queue.enqueue"):
        mock_dir.mkdir = MagicMock()
        dest = MagicMock()
        dest.__truediv__ = MagicMock(return_value=dest)
        dest.open = MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock(return_value=False)))
        mock_dir.__truediv__ = MagicMock(return_value=dest)
        mock_dir.mkdir = MagicMock()

        r = client.post("/api/v1/upload", files=[_make_file("notas.txt")])
    assert r.status_code != 400 or "Tipo não suportado" not in (r.text or "")


def test_upload_md_accepted(client):
    with patch("backend.config.settings.upload_dir") as mock_dir, \
         patch("backend.api.ingestion_queue.enqueue"):
        mock_dir.mkdir = MagicMock()
        dest = MagicMock()
        mock_dir.__truediv__ = MagicMock(return_value=dest)
        dest.open = MagicMock(return_value=MagicMock(__enter__=MagicMock(return_value=MagicMock()), __exit__=MagicMock(return_value=False)))

        r = client.post("/api/v1/upload", files=[_make_file("readme.md")])
    assert r.status_code != 400 or "Tipo não suportado" not in (r.text or "")


def test_upload_unsupported_returns_400(client):
    r = client.post("/api/v1/upload", files=[_make_file("planilha.xlsx")])
    assert r.status_code == 400
    assert "Tipo não suportado" in r.json()["detail"]


# ── POST /documents/text ──────────────────────────────────────────────────────

def test_index_text_endpoint(client):
    with patch("backend.config.settings.upload_dir") as mock_dir, \
         patch("backend.api.ingestion_queue.enqueue"):
        mock_dir.mkdir = MagicMock()
        dest = MagicMock()
        mock_dir.__truediv__ = MagicMock(return_value=dest)
        dest.write_text = MagicMock()

        r = client.post(
            "/api/v1/documents/text",
            json={"title": "minha-lib", "content": "documentação da lib"},
        )
    assert r.status_code == 202
    assert "job_id" in r.json()
    assert "filename" in r.json()


def test_index_text_empty_title_returns_400(client):
    r = client.post("/api/v1/documents/text", json={"title": "", "content": "algo"})
    assert r.status_code == 400


def test_index_text_empty_content_returns_400(client):
    r = client.post("/api/v1/documents/text", json={"title": "lib", "content": "   "})
    assert r.status_code == 400


# ── /settings ─────────────────────────────────────────────────────────────────

def test_get_settings_returns_configured_status(client):
    r = client.get("/api/v1/settings")
    assert r.status_code == 200
    assert "configured" in r.json()
    assert "provider" in r.json()
    assert "model" in r.json()


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_endpoint(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
