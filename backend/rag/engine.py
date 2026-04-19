from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from llama_index.core.base.base_query_engine import BaseQueryEngine

from backend.config import settings as cfg
from backend.rag.pipeline import get_or_create_index

_engine: Optional["BaseQueryEngine"] = None


def _build_engine(index):
    from llama_index.core import Settings
    from llama_index.core.prompts import PromptTemplate

    from backend.llm.client import create_llm

    system_prompt = (
        "Você é um assistente técnico focado em extrair informações de documentações. "
        "Sua função é responder a dúvida do usuário com base estritamente no contexto fornecido. "
        "Você DEVE SEMPRE usar formatação Markdown rica. Use obrigatoriamente: "
        "- Cabeçalhos (###) para estruturar sua resposta; "
        "- Listas e bullet-points para enumerar passos ou características; "
        "- Blocos de código (```linguagem) quando mencionar configurações, comandos ou código-fonte. "
        "Não adicione textos informais como 'Aqui está a resposta', seja direto."
    )

    Settings.llm = create_llm(
        provider=cfg.get_provider(),
        model=cfg.get_llm_model(),
        api_key=cfg.get_active_api_key(),
        ollama_base_url=cfg.get_ollama_base_url(),
        temperature=cfg.llm_temperature,
        max_tokens=cfg.llm_max_tokens,
        system_prompt=system_prompt,
    )

    qa_prompt = PromptTemplate(
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and not prior knowledge, "
        "answer the query.\n"
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
    return f"<ContentResponse>\n{str(response)}\n</ContentResponse>"
