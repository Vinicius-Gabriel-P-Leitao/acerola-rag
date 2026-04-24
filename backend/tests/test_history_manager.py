"""Tests for backend/history/manager.py (SQLite + FTS5)."""

import pytest

from backend.history import manager as hist


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    """Initialise a clean in-file SQLite database for each test."""
    hist.init(tmp_path / "test_history.db")


# ── create_conversation ───────────────────────────────────────────────────────


def test_create_conversation_returns_dict():
    result = hist.create_conversation("c1", "Minha conversa")
    assert result["id"] == "c1"
    assert result["title"] == "Minha conversa"
    assert "created_at" in result
    assert "updated_at" in result


def test_create_conversation_appears_in_list():
    hist.create_conversation("c1", "Primeira")
    convs = hist.list_conversations()
    assert len(convs) == 1
    assert convs[0]["id"] == "c1"


def test_create_conversation_duplicate_is_ignored():
    hist.create_conversation("c1", "Original")
    hist.create_conversation("c1", "Duplicada")
    convs = hist.list_conversations()
    assert len(convs) == 1
    assert convs[0]["title"] == "Original"


def test_list_conversations_ordered_by_updated_at_desc():
    hist.create_conversation("old", "Antiga")
    hist.create_conversation("new", "Nova")
    # save a message to new so it has a later updated_at
    hist.save_message("new", "user", "oi")
    convs = hist.list_conversations()
    assert convs[0]["id"] == "new"


# ── save_message / get_messages ───────────────────────────────────────────────


def test_save_message_returns_integer_id():
    hist.create_conversation("c1", "t")
    msg_id = hist.save_message("c1", "user", "olá")
    assert isinstance(msg_id, int)


def test_get_messages_returns_saved_messages():
    hist.create_conversation("c1", "t")
    hist.save_message("c1", "user", "pergunta")
    hist.save_message("c1", "assistant", "resposta")
    msgs = hist.get_messages("c1")
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[0]["content"] == "pergunta"
    assert msgs[1]["role"] == "assistant"


def test_get_messages_includes_attached_files():
    hist.create_conversation("c1", "t")
    files = [{"name": "doc.pdf", "type": "pdf", "size_bytes": 1024}]
    hist.save_message("c1", "user", "com arquivo", attached_files=files)
    msgs = hist.get_messages("c1")
    assert msgs[0]["attached_files"] == files


def test_get_messages_empty_for_unknown_conversation():
    msgs = hist.get_messages("nao-existe")
    assert msgs == []


def test_get_messages_returns_empty_list_for_attached_files_when_none():
    hist.create_conversation("c1", "t")
    hist.save_message("c1", "user", "sem arquivo")
    msgs = hist.get_messages("c1")
    assert msgs[0]["attached_files"] == []


# ── save_rag_sources / get_rag_sources ────────────────────────────────────────


def test_save_and_get_rag_sources():
    hist.create_conversation("c1", "t")
    msg_id = hist.save_message("c1", "assistant", "resp")
    sources = [
        {"source_file": "a.pdf", "chunk_text": "trecho A", "score": 0.9},
        {"source_file": "b.pdf", "chunk_text": "trecho B", "score": 0.7},
    ]
    hist.save_rag_sources("c1", msg_id, sources)
    result = hist.get_rag_sources("c1")
    assert len(result) == 2
    assert result[0]["source_file"] == "a.pdf"  # highest score first
    assert result[1]["source_file"] == "b.pdf"


def test_save_rag_sources_empty_list_is_noop():
    hist.create_conversation("c1", "t")
    msg_id = hist.save_message("c1", "assistant", "resp")
    hist.save_rag_sources("c1", msg_id, [])
    assert hist.get_rag_sources("c1") == []


def test_get_rag_sources_empty_for_unknown_conversation():
    assert hist.get_rag_sources("nao-existe") == []


# ── delete_conversation ───────────────────────────────────────────────────────


def test_delete_conversation_removes_from_list():
    hist.create_conversation("c1", "t")
    hist.delete_conversation("c1")
    assert hist.list_conversations() == []


def test_delete_conversation_cascades_messages():
    hist.create_conversation("c1", "t")
    hist.save_message("c1", "user", "msg")
    hist.delete_conversation("c1")
    assert hist.get_messages("c1") == []


def test_delete_conversation_cascades_rag_sources():
    hist.create_conversation("c1", "t")
    msg_id = hist.save_message("c1", "assistant", "resp")
    hist.save_rag_sources("c1", msg_id, [{"source_file": "a.pdf", "chunk_text": "x", "score": 0.5}])
    hist.delete_conversation("c1")
    assert hist.get_rag_sources("c1") == []


def test_delete_conversation_returns_true():
    hist.create_conversation("c1", "t")
    assert hist.delete_conversation("c1") is True


# ── search_conversations (FTS5) ───────────────────────────────────────────────


def test_search_finds_matching_conversation():
    hist.create_conversation("c1", "sobre Python")
    hist.save_message("c1", "user", "como usar decoradores em Python")
    result = hist.search_conversations("decoradores")
    assert any(c["id"] == "c1" for c in result)


def test_search_does_not_match_unrelated():
    hist.create_conversation("c1", "sobre Python")
    hist.save_message("c1", "user", "como usar decoradores")
    result = hist.search_conversations("kubernetes")
    assert result == []


def test_search_empty_query_returns_empty():
    hist.create_conversation("c1", "t")
    hist.save_message("c1", "user", "qualquer coisa")
    result = hist.search_conversations("")
    assert result == []


def test_search_prefix_match():
    hist.create_conversation("c1", "t")
    hist.save_message("c1", "user", "arquitetura de microsserviços")
    result = hist.search_conversations("micross")
    assert any(c["id"] == "c1" for c in result)


def test_search_deleted_conversation_not_returned():
    hist.create_conversation("c1", "t")
    hist.save_message("c1", "user", "conteúdo deletado")
    hist.delete_conversation("c1")
    result = hist.search_conversations("deletado")
    assert result == []
