from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from llama_index.core.chat_engine.types import BaseChatEngine

from backend.config import settings as cfg
from backend.rag.pipeline import get_or_create_index

_sessions: dict[str, "BaseChatEngine"] = {}
_index = None
_langfuse = None


def _get_index():
    global _index
    if _index is None:
        _index = get_or_create_index()
    return _index


def _build_engine():
    global _langfuse

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
        "- TODO código, comando ou JSON DEVE estar em um bloco de código (```linguagem). "
        "Isso inclui código que apareça no contexto SEM formatação: identifique-o e "
        "envolva-o em ``` antes de apresentar. NUNCA exiba código como texto puro.\n"
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

    retriever = index.as_retriever(similarity_top_k=4)
    memory = ChatMemoryBuffer.from_defaults(token_limit=4096)
    postprocessors: list[BaseNodePostprocessor] = [LongContextReorder()]

    if cfg.langfuse_public_key and cfg.langfuse_secret_key:
        try:
            import os

            from langfuse import get_client  # type: ignore
            from openinference.instrumentation.llama_index import LlamaIndexInstrumentor  # type: ignore

            os.environ["LANGFUSE_PUBLIC_KEY"] = cfg.langfuse_public_key
            os.environ["LANGFUSE_SECRET_KEY"] = cfg.langfuse_secret_key
            os.environ["LANGFUSE_BASE_URL"] = cfg.langfuse_base_url or "https://cloud.langfuse.com"

            LlamaIndexInstrumentor().instrument()
            _langfuse = get_client()
        except Exception:
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


def refresh_engine(session_id: str | None = None) -> None:
    global _index
    _index = None
    if session_id is not None:
        _sessions.pop(session_id, None)
    else:
        _sessions.clear()


def query(
    question: str,
    session_id: str = "default",
    extra_context: str | None = None,
) -> tuple[str, list[dict]]:
    engine = get_engine(session_id)
    if engine is None:
        return "Nenhum documento indexado ainda. Faça upload de um arquivo primeiro.", []

    prompt = question
    if extra_context:
        prompt = f"{question}\n\n---\nArquivos anexados pelo usuário:\n{extra_context}"

    response = engine.chat(prompt)

    # if _langfuse is not None:
    #     try:
    #         _langfuse.flush()
    #     except Exception:
    #         pass

    source_nodes = getattr(response, "source_nodes", [])
    sources = [
        {
            "source_file": node.node.metadata.get("source", "desconhecido"),
            "chunk_text": (node.node.get_content() or "")[:600],
            "score": round(float(node.score or 0.0), 4),
        }
        for node in source_nodes
    ]

    return f"<ContentResponse>\n{str(response)}\n</ContentResponse>", sources


def stream_query(
    question: str,
    session_id: str = "default",
    extra_context: str | None = None,
    attached_meta: list[dict] | None = None,
):
    engine = get_engine(session_id)
    if engine is None:
        yield "Nenhum documento indexado ainda. Faça upload de um arquivo primeiro."
        return

    prompt = question
    if extra_context:
        prompt = f"{question}\n\n---\nArquivos anexados pelo usuário:\n{extra_context}"

    full_answer = ""
    try:
        response_stream = engine.stream_chat(prompt)
        for token in response_stream.response_gen:
            full_answer += token
            yield token
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            yield "\n\n❌ **Erro de Cota (429):** Você atingiu o limite de requisições do seu plano atual no Gemini. Por favor, aguarde o reset da cota ou altere a API Key nas configurações."
        else:
            yield f"\n\n❌ **Erro na API:** {error_msg}"
        return

    # Persist to history after the stream finishes successfully
    try:
        from backend.history import manager as hist

        answer_to_save = f"<ContentResponse>\n{full_answer}\n</ContentResponse>"
        source_nodes = getattr(response_stream, "source_nodes", [])
        sources = [
            {
                "source_file": node.node.metadata.get("source", "desconhecido"),
                "chunk_text": (node.node.get_content() or "")[:600],
                "score": round(float(node.score or 0.0), 4),
            }
            for node in source_nodes
        ]

        title = question[:60].strip()
        hist.create_conversation(session_id, title)
        hist.save_message(session_id, "user", question, attached_files=attached_meta)
        asst_msg_id = hist.save_message(session_id, "assistant", answer_to_save)
        hist.save_rag_sources(session_id, asst_msg_id, sources)
    except Exception as e:
        print(f"Error persisting history: {e}")
