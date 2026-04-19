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
        "Você é um assistente de documentação técnica extremamente meticuloso. Sua "
        "principal função é analisar **todo o contexto fornecido**, sem exceção, "
        "antes de responder.\n\n"
        "ESTRATÉGIA DE ANÁLISE E RESPOSTA:\n"
        "1. LEIA TUDO PRIMEIRO: Antes de formular uma resposta, leia o contexto do "
        "início ao fim. A resposta pode estar em um exemplo de código que não parece "
        "diretamente relacionado.\n"
        "2. PRIORIZE CÓDIGO: Encontre e apresente os exemplos de código mais relevantes "
        "para a pergunta do usuário. Se não houver um exemplo exato, construa um com "
        "base em padrões análogos encontrados no texto.\n"
        "3. SEJA PRECISO: Baseie sua resposta estritamente no que está no contexto. "
        "Apenas se a informação não puder ser encontrada ou inferida, afirme que o "
        "conteúdo não foi localizado.\n\n"
        "REGRAS DE FORMATAÇÃO:\n"
        "- Use Títulos e Subtítulos (`##`, `###`).\n"
        "- Use Listas (`-` ou `1.`) e parágrafos curtos.\n"
        "- Use Separadores (`---`) para dividir seções longas.\n"
        "- Use Tabelas Markdown quando a informação for comparativa.\n"
        "- TODO código, comando ou JSON DEVE estar em um bloco de código (```linguagem).\n"
        "- Não use saudações ou introduções como 'Aqui está a resposta:'."
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
                similarity_top_k=3,
                callback_manager=Settings.callback_manager,
                text_qa_template=qa_prompt,
                response_mode="refine",
            )
        except ImportError:
            pass

    return index.as_query_engine(
        similarity_top_k=3, text_qa_template=qa_prompt, response_mode="refine"
    )


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
