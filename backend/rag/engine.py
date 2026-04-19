from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from llama_index.core.base.base_query_engine import BaseQueryEngine

from backend.config import settings as cfg
from backend.rag.pipeline import get_or_create_index

_engine: Optional["BaseQueryEngine"] = None

_SYSTEM_PROMPT = """Sua resposta DEVE ser SEMPRE e ESTRITAMENTE formatada em Markdown, usando blocos de código, negrito e listas quando necessário. 
Além disso, ela deve ser envelopada dentro das tags `<ContentResponse>` e `</ContentResponse>`. 
Não adicione textos, saudações ou explicações fora dessas tags."""


def _build_engine(index):
    from llama_index.core import Settings
    from llama_index.core.prompts import PromptTemplate

    from backend.llm.client import create_llm

    Settings.llm = create_llm(
        provider=cfg.get_provider(),
        model=cfg.get_llm_model(),
        api_key=cfg.get_active_api_key(),
        ollama_base_url=cfg.get_ollama_base_url(),
        temperature=cfg.llm_temperature,
        max_tokens=cfg.llm_max_tokens,
    )

    qa_prompt = PromptTemplate(
        _SYSTEM_PROMPT + "\n\n"
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, "
        "answer the query ALWAYS USING MARKDOWN FORMATTING.\n"
        "Query: {query_str}\n"
        "Answer: "
    )

    if cfg.langfuse_public_key and cfg.langfuse_secret_key:
        try:
            from langfuse.llama_index import LlamaIndexCallbackHandler  # type: ignore
            from llama_index.core.callbacks import CallbackManager

            handler = LlamaIndexCallbackHandler(
                public_key=cfg.langfuse_public_key,
                secret_key=cfg.langfuse_secret_key,
                host=cfg.langfuse_base_url,
            )

            Settings.callback_manager = CallbackManager([handler])

            return index.as_query_engine(
                similarity_top_k=5,
                callback_manager=Settings.callback_manager,
                text_qa_template=qa_prompt,
            )
        except ImportError:
            pass

    return index.as_query_engine(similarity_top_k=5, text_qa_template=qa_prompt)


def get_engine() -> Optional["BaseQueryEngine"]:
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
        return "Nenhum documento indexado ainda. Faça upload de um arquivo primeiro."
    response = engine.query(question)
    return str(response)
