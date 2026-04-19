from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import BaseChatEngine

from backend.config import settings as cfg
from backend.rag.pipeline import get_or_create_index

_sessions: dict[str, "BaseChatEngine"] = {}
_index = None


def _get_index():
    global _index
    if _index is None:
        _index = get_or_create_index()
    return _index


def _build_engine():
    from llama_index.core import Settings
    from llama_index.core.chat_engine import CondensePlusContextChatEngine
    from llama_index.core.memory import ChatMemoryBuffer
    from llama_index.core.postprocessor import LongContextReorder
    from llama_index.core.postprocessor.types import BaseNodePostprocessor

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

    index = _get_index()
    if index is None:
        return None

    Settings.llm = create_llm(
        provider=cfg.get_provider(),
        model=cfg.get_llm_model(),
        api_key=cfg.get_active_api_key(),
        ollama_base_url=cfg.get_ollama_base_url(),
        temperature=cfg.llm_temperature,
        max_tokens=cfg.llm_max_tokens,
        system_prompt=system_prompt,
    )

    retriever = index.as_retriever(similarity_top_k=6)
    memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
    postprocessors: list[BaseNodePostprocessor] = [LongContextReorder()]

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
        except ImportError:
            pass

    return CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        memory=memory,
        node_postprocessors=postprocessors,
        system_prompt=system_prompt,
    )


def get_engine(session_id: str) -> Optional["BaseChatEngine"]:
    if session_id not in _sessions:
        engine = _build_engine()
        if engine is None:
            return None
        _sessions[session_id] = engine
    return _sessions[session_id]


def refresh_engine(session_id: Optional[str] = None) -> None:
    global _index
    _index = None
    if session_id is not None:
        _sessions.pop(session_id, None)
    else:
        _sessions.clear()


def query(question: str, session_id: str = "default") -> str:
    engine = get_engine(session_id)
    if engine is None:
        return "Nenhum documento indexado ainda. Faça upload de um arquivo primeiro."
    response = engine.chat(question)
    return f"<ContentResponse>\n{str(response)}\n</ContentResponse>"
