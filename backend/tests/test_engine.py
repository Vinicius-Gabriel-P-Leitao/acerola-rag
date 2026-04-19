from unittest.mock import MagicMock, patch

import backend.rag.engine as engine_module
from backend.rag.engine import query, refresh_engine


def setup_function():
    engine_module._engine = None


def test_query_returns_no_index_message_when_no_index():
    with patch("backend.rag.engine.get_or_create_index", return_value=None):
        result = query("Qual é o método X?")
    assert "upload" in result.lower() or "nenhum" in result.lower()


def test_query_returns_engine_response():
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: "resposta gerada"
    mock_engine = MagicMock()
    mock_engine.query.return_value = mock_response
    mock_index = MagicMock()

    with (
        patch("backend.rag.engine.get_or_create_index", return_value=mock_index),
        patch("backend.rag.engine._build_engine", return_value=mock_engine),
    ):
        engine_module._engine = None
        result = query("pergunta qualquer")

    assert result == "<ContentResponse>\nresposta gerada\n</ContentResponse>"


def test_refresh_engine_resets_cache():
    engine_module._engine = MagicMock()
    refresh_engine()
    assert engine_module._engine is None


def test_query_called_twice_reuses_engine():
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: "ok"
    mock_engine = MagicMock()
    mock_engine.query.return_value = mock_response
    mock_index = MagicMock()

    with (
        patch("backend.rag.engine.get_or_create_index", return_value=mock_index),
        patch("backend.rag.engine._build_engine", return_value=mock_engine) as mock_build,
    ):
        engine_module._engine = None
        query("q1")
        query("q2")
        assert mock_build.call_count == 1
