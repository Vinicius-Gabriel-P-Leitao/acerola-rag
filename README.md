# Acerola RAG

Sistema de Retrieval-Augmented Generation (RAG) que permite fazer perguntas sobre documentos carregados, usando LLMs como OpenAI, Gemini, Anthropic ou Ollama.

## Screenshots

<table>
  <tr>
    <td align="center"><b>Chat</b></td>
    <td align="center"><b>Admin</b></td>
  </tr>
  <tr>
    <td><img src="./docs/chat-print.png" alt="Chat" width="280"/></td>
    <td><img src="./docs/admin-print.png" alt="Admin" width="280"/></td>
  </tr>
</table>

## Arquitetura

```mermaid
flowchart TD
    U([Usuário]) -->|upload| IQ[Ingestion Queue]
    IQ --> P[Parser\nUnstructured / EasyOCR]
    P --> C[Chunking\n1024 tokens / overlap 128]
    C --> E[Embeddings\nBAAI/bge-small-en-v1.5]
    E --> QD[(Qdrant\nDense + BM25)]

    U -->|pergunta| CE[CondensePlusContext\nChatEngine]
    CE -->|hybrid search top-6| QD
    QD -->|docs reordenados| LCR[LongContextReorder]
    LCR --> LLM[LLM\nOpenAI · Gemini · Anthropic · Ollama]
    LLM -->|resposta| U
```

## Fluxo de sessão

```mermaid
sequenceDiagram
    participant Browser
    participant FastAPI
    participant Engine
    participant Qdrant
    participant LLM

    Browser->>FastAPI: POST /api/v1/query {question, session_id}
    FastAPI->>Engine: query(question, session_id)
    Engine->>Engine: get or create ChatEngine for session
    Engine->>Qdrant: hybrid search (BM25 + vector)
    Qdrant-->>Engine: top-6 nodes
    Engine->>LLM: condense history + context + question
    LLM-->>Engine: resposta
    Engine-->>FastAPI: <ContentResponse>...</ContentResponse>
    FastAPI-->>Browser: 200 OK
```

## Stack

| Camada | Tecnologias |
|--------|-------------|
| Frontend | SvelteKit 2 · Svelte 5 · Tailwind CSS 4 · shadcn-svelte |
| Backend | FastAPI · LlamaIndex · Uvicorn |
| LLMs | OpenAI · Gemini · Anthropic · Ollama |
| Vector store | Qdrant v1.17 (dense + BM25 híbrido) |
| Parsing | Unstructured · EasyOCR · Poppler |
| Observabilidade | Langfuse v3 · OpenInference |

## Rodando localmente

```bash
# 1. Qdrant
docker run -d -p 6333:6333 qdrant/qdrant:v1.17.0

# 2. Backend
cd backend
pip install -r requirements.txt
cp .env.example .env   # preencha as chaves
python -m backend.main

# 3. Frontend (dev)
cd frontend
npm install
npm run dev
```

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `LLM_PROVIDER` | `openai` \| `gemini` \| `claude` \| `ollama` |
| `LLM_MODEL` | Ex: `gpt-4o-mini`, `gemini-2.0-flash` |
| `OPENAI_API_KEY` | Chave OpenAI |
| `GEMINI_API_KEY` | Chave Gemini |
| `ANTHROPIC_API_KEY` | Chave Anthropic |
| `QDRANT_HOST` | Host do Qdrant (default `localhost`) |
| `QDRANT_PORT` | Porta do Qdrant (default `6333`) |
| `LANGFUSE_PUBLIC_KEY` | Chave pública Langfuse (opcional) |
| `LANGFUSE_SECRET_KEY` | Chave secreta Langfuse (opcional) |

## Licença

Veja [LICENSE](./LICENSE).
