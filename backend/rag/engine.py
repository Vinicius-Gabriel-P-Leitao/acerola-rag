from typing import Optional

from backend.config import settings as cfg
from backend.rag.pipeline import get_or_create_index

_NO_INDEX_MSG = "Nenhum documento indexado ainda. Faça upload de um arquivo primeiro."

_engine: Optional[object] = None


def _build_engine(index):
    from backend.llm.client import create_llm
    from llama_index.core import Settings

    Settings.llm = create_llm(
        provider=cfg.get_provider(),
        model=cfg.get_llm_model(),
        api_key=cfg.get_active_api_key(),
        ollama_base_url=cfg.get_ollama_base_url(),
        temperature=cfg.llm_temperature,
        max_tokens=cfg.llm_max_tokens,
    )

    if cfg.langfuse_public_key and cfg.langfuse_secret_key:
        try:
            from langfuse.llama_index import LlamaIndexCallbackHandler
            from llama_index.core.callbacks import CallbackManager

            handler = LlamaIndexCallbackHandler(
                public_key=cfg.langfuse_public_key,
                secret_key=cfg.langfuse_secret_key,
                host=cfg.langfuse_base_url,
            )
            Settings.callback_manager = CallbackManager([handler])
            return index.as_query_engine(
                similarity_top_k=5, callback_manager=Settings.callback_manager
            )
        except ImportError:
            pass

    return index.as_query_engine(similarity_top_k=5)


def get_engine() -> Optional[object]:
    global _engine
    if _engine is None:
        index = get_or_create_index()

        if index is None:
            return None
        _engine = _build_engine(index)
    return _engine


def refresh_engine() -> None:
    global _engine
    _engine = None


def query(question: str) -> str:
    engine = get_engine()
    
    if engine is None:
        return _NO_INDEX_MSG
    response = engine.query(question)
    return str(response)
