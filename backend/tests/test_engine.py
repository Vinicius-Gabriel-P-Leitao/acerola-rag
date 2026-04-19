from unittest.mock import MagicMock, patch

import backend.rag.engine as engine_module
from backend.rag.engine import query, refresh_engine


def setup_function():
    engine_module._sessions.clear()
    engine_module._index = None


def test_query_returns_no_index_message_when_no_index():
    with patch("backend.rag.engine.get_or_create_index", return_value=None):
        result = query("Qual é o método X?")
    assert "upload" in result.lower() or "nenhum" in result.lower()


def test_query_returns_engine_response():
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: "resposta gerada"
    mock_engine = MagicMock()
    mock_engine.chat.return_value = mock_response

    with patch("backend.rag.engine._build_engine", return_value=mock_engine):
        result = query("pergunta qualquer", session_id="test")

    assert result == "<ContentResponse>\nresposta gerada\n</ContentResponse>"


def test_query_uses_chat_not_query():
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: "ok"
    mock_engine = MagicMock()
    mock_engine.chat.return_value = mock_response

    with patch("backend.rag.engine._build_engine", return_value=mock_engine):
        query("pergunta", session_id="test")

    mock_engine.chat.assert_called_once_with("pergunta")
    mock_engine.query.assert_not_called()


def test_refresh_engine_clears_all_sessions():
    engine_module._sessions["a"] = MagicMock()
    engine_module._sessions["b"] = MagicMock()
    refresh_engine()
    assert engine_module._sessions == {}


def test_refresh_engine_clears_single_session():
    engine_module._sessions["a"] = MagicMock()
    engine_module._sessions["b"] = MagicMock()
    refresh_engine(session_id="a")
    assert "a" not in engine_module._sessions
    assert "b" in engine_module._sessions


def test_different_sessions_get_different_engines():
    mock_engine_1 = MagicMock()
    mock_engine_2 = MagicMock()
    mock_engine_1.chat.return_value = MagicMock(__str__=lambda s: "r1")
    mock_engine_2.chat.return_value = MagicMock(__str__=lambda s: "r2")

    with patch("backend.rag.engine._build_engine", side_effect=[mock_engine_1, mock_engine_2]):
        query("q", session_id="user1")
        query("q", session_id="user2")

    assert engine_module._sessions["user1"] is mock_engine_1
    assert engine_module._sessions["user2"] is mock_engine_2


def test_same_session_reuses_engine():
    mock_engine = MagicMock()
    mock_engine.chat.return_value = MagicMock(__str__=lambda s: "ok")

    with patch("backend.rag.engine._build_engine", return_value=mock_engine) as mock_build:
        query("q1", session_id="user1")
        query("q2", session_id="user1")
        assert mock_build.call_count == 1


def test_default_session_id():
    mock_engine = MagicMock()
    mock_engine.chat.return_value = MagicMock(__str__=lambda s: "ok")

    with patch("backend.rag.engine._build_engine", return_value=mock_engine):
        query("pergunta")

    assert "default" in engine_module._sessions


# ── _build_engine internals ────────────────────────────────────────────────────

def _call_build_engine():
    mock_chat_engine = MagicMock()

    with patch("backend.llm.client.create_llm"), \
         patch("llama_index.core.Settings"), \
         patch("llama_index.core.chat_engine.CondensePlusContextChatEngine") as mock_cls, \
         patch("backend.rag.engine._get_index", return_value=MagicMock()), \
         patch("backend.config.settings.langfuse_public_key", ""), \
         patch("backend.config.settings.langfuse_secret_key", ""):
        mock_cls.from_defaults.return_value = mock_chat_engine
        from backend.rag.engine import _build_engine
        result = _build_engine()

    return mock_cls.from_defaults.call_args, result


def test_build_engine_retriever_uses_top_k_6():
    mock_index = MagicMock()

    with patch("backend.llm.client.create_llm"), \
         patch("llama_index.core.Settings"), \
         patch("llama_index.core.chat_engine.CondensePlusContextChatEngine"), \
         patch("backend.rag.engine._get_index", return_value=mock_index), \
         patch("backend.config.settings.langfuse_public_key", ""), \
         patch("backend.config.settings.langfuse_secret_key", ""):
        from backend.rag.engine import _build_engine
        _build_engine()

    mock_index.as_retriever.assert_called_once_with(similarity_top_k=6)


def test_build_engine_has_long_context_reorder():
    from llama_index.core.postprocessor import LongContextReorder

    call, _ = _call_build_engine()
    postprocessors = call.kwargs.get("node_postprocessors", [])
    assert any(isinstance(p, LongContextReorder) for p in postprocessors)


def test_build_engine_single_reorder_postprocessor():
    from llama_index.core.postprocessor import LongContextReorder

    call, _ = _call_build_engine()
    postprocessors = call.kwargs.get("node_postprocessors", [])
    reorders = [p for p in postprocessors if isinstance(p, LongContextReorder)]
    assert len(reorders) == 1


def test_build_engine_has_memory():
    from llama_index.core.memory import ChatMemoryBuffer

    call, _ = _call_build_engine()
    memory = call.kwargs.get("memory")
    assert isinstance(memory, ChatMemoryBuffer)


def test_build_engine_returns_none_when_no_index():
    with patch("backend.rag.engine._get_index", return_value=None):
        from backend.rag.engine import _build_engine
        result = _build_engine()
    assert result is None


def test_build_engine_returns_chat_engine():
    _, result = _call_build_engine()
    assert result is not None
