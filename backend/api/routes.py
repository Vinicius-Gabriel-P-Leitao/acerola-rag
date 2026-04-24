import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.api import ingestion_queue as iq
from backend.api.dtos import (
    ConversationDetailDTO,
    DeleteDocumentResponse,
    DocumentContentResponse,
    DocumentListResponse,
    HealthResponse,
    HistoryListResponse,
    HistorySearchResponse,
    IndexTextRequest,
    IndexTextResponse,
    JobCreatedDTO,
    JobInfoDTO,
    LLMSettingsRequest,
    LLMSettingsResponse,
    MessageDTO,
    QueryResponse,
    RagSourceDTO,
    UploadResponse,
    UploadStatusResponse,
)
from backend.config import set_llm_override
from backend.config import settings as cfg
from backend.rag.engine import query as rag_query
from backend.rag.engine import refresh_engine

router = APIRouter()

_ALLOWED = {".pdf", ".docx", ".doc", ".txt", ".md"}
_MAX_ATTACH = 5
_MAX_ATTACH_CHARS = 6000  # chars per file sent to context


# ── Upload ────────────────────────────────────────────────────────────────────


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_documents(files: list[UploadFile] = File(...)):
    if len(files) > cfg.max_upload_files:
        raise HTTPException(400, f"Máximo de {cfg.max_upload_files} arquivos por vez")

    cfg.upload_dir.mkdir(parents=True, exist_ok=True)
    created = []

    for file in files:
        filename = file.filename or "unknown"
        suffix = Path(filename).suffix.lower()

        if suffix not in _ALLOWED:
            raise HTTPException(400, f"Tipo não suportado: {suffix}")

        dest = cfg.upload_dir / filename
        with dest.open("wb") as dest_file:
            shutil.copyfileobj(file.file, dest_file)

        job = iq.IngestionJob(filename=filename, file_path=dest)
        iq.enqueue(job)
        created.append(JobCreatedDTO(job_id=job.job_id, filename=job.filename))
    return UploadResponse(jobs=created)


@router.get("/upload/status", response_model=UploadStatusResponse)
async def upload_status():
    jobs = [
        JobInfoDTO(
            job_id=job.job_id,
            filename=job.filename,
            status=job.status.value if hasattr(job.status, "value") else job.status,
            error=job.error,
            created_at=job.created_at,
            finished_at=job.finished_at,
        )
        for job in iq.all_jobs()
    ]
    return UploadStatusResponse(queue_size=iq.queue_size(), jobs=jobs)


@router.get("/upload/status/{job_id}", response_model=JobInfoDTO)
async def upload_job_status(job_id: str):
    job = iq.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job não encontrado")
    return JobInfoDTO(
        job_id=job.job_id,
        filename=job.filename,
        status=job.status.value if hasattr(job.status, "value") else job.status,
        error=job.error,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )


# ── Documents (admin) ─────────────────────────────────────────────────────────


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(page: int = 1, page_size: int = 20, search: str = ""):
    from backend.indexing.documents import list_documents as _list

    result = _list(page=page, page_size=page_size, search=search)
    return DocumentListResponse(**result)


@router.get("/documents/{source}/content", response_model=DocumentContentResponse)
async def get_document_content(source: str):
    from backend.indexing.documents import get_document_content as _content

    content = _content(source)
    if not content:
        raise HTTPException(404, f"Documento '{source}' não encontrado")
    return DocumentContentResponse(source=source, content=content)


@router.delete("/documents/{source}", response_model=DeleteDocumentResponse)
async def delete_document(source: str):
    from backend.indexing.documents import delete_document as _delete

    deleted = _delete(source)
    refresh_engine()
    return DeleteDocumentResponse(deleted_chunks=deleted)


@router.post("/documents/text", response_model=IndexTextResponse, status_code=202)
async def index_text(req: IndexTextRequest):
    if not req.title.strip():
        raise HTTPException(400, "O título não pode ser vazio")
    if not req.content.strip():
        raise HTTPException(400, "O conteúdo não pode ser vazio")

    cfg.upload_dir.mkdir(parents=True, exist_ok=True)
    filename = req.title if req.title.endswith(".txt") else f"{req.title}.txt"
    dest = cfg.upload_dir / filename
    dest.write_text(req.content, encoding="utf-8")

    job = iq.IngestionJob(filename=filename, file_path=dest)
    iq.enqueue(job)
    return IndexTextResponse(job_id=job.job_id, filename=job.filename)


# ── Query ─────────────────────────────────────────────────────────────────────


def _extract_file_text(upload: UploadFile) -> tuple[str, dict]:
    """Extrai texto de um arquivo anexado para uso inline no contexto."""
    from backend.ingestion.loader import load_document

    filename = upload.filename or "anexo"
    suffix = Path(filename).suffix.lower()

    if suffix not in _ALLOWED:
        raise HTTPException(400, f"Tipo de anexo não suportado: {suffix}")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(upload.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        doc = load_document(tmp_path)
        text = doc.text[:_MAX_ATTACH_CHARS]
    finally:
        tmp_path.unlink(missing_ok=True)

    meta = {
        "name": filename,
        "type": suffix.lstrip("."),
        "size_bytes": upload.size or 0,
    }
    return text, meta


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    question: str = Form(...),
    conversation_id: str = Form(default=""),
    files: list[UploadFile] = File(default=[]),
):
    if not cfg.is_llm_configured():
        raise HTTPException(
            422,
            f"Modelo não configurado corretamente para o provider "
            f"'{cfg.get_provider()}'. Verifique a API key no painel lateral.",
        )

    if len(files) > _MAX_ATTACH:
        raise HTTPException(400, f"Máximo de {_MAX_ATTACH} arquivos por conversa")

    conv_id = conversation_id.strip() or str(uuid.uuid4())

    # Process attached files
    extra_parts: list[str] = []
    attached_meta: list[dict] = []
    for upload in files:
        try:
            text, meta = _extract_file_text(upload)
            extra_parts.append(f"[{meta['name']}]\n{text}")
            attached_meta.append(meta)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(422, f"Erro ao processar '{upload.filename}': {exc}") from exc

    extra_context = "\n\n".join(extra_parts) if extra_parts else None

    answer, sources = rag_query(question, session_id=conv_id, extra_context=extra_context)

    # Persist to history
    from backend.history import manager as hist

    title = question[:60].strip()
    hist.create_conversation(conv_id, title)
    hist.save_message(conv_id, "user", question, attached_files=attached_meta)
    asst_msg_id = hist.save_message(conv_id, "assistant", answer)
    hist.save_rag_sources(conv_id, asst_msg_id, sources)

    return QueryResponse(
        answer=answer,
        conversation_id=conv_id,
        sources=[RagSourceDTO(**s) for s in sources],
    )


# ── History ───────────────────────────────────────────────────────────────────


@router.get("/history", response_model=HistoryListResponse)
async def list_history():
    from backend.api.dtos import ConversationDTO
    from backend.history import manager as hist

    convs = hist.list_conversations()
    return HistoryListResponse(conversations=[ConversationDTO(**c) for c in convs])


@router.get("/history/search", response_model=HistorySearchResponse)
async def search_history(q: str = ""):
    from backend.history import manager as hist

    results = hist.search_conversations(q)
    return HistorySearchResponse(conversations=results)


@router.get("/history/{conversation_id}", response_model=ConversationDetailDTO)
async def get_conversation(conversation_id: str):
    from backend.history import manager as hist

    messages_raw = hist.get_messages(conversation_id)
    if not messages_raw:
        raise HTTPException(404, "Conversa não encontrada")

    sources_raw = hist.get_rag_sources(conversation_id)

    messages = [
        MessageDTO(
            id=m["id"],
            role=m["role"],
            content=m["content"],
            created_at=m["created_at"],
            attached_files=m.get("attached_files", []),
        )
        for m in messages_raw
    ]
    sources = [RagSourceDTO(**s) for s in sources_raw]

    convs = hist.list_conversations(limit=1000)
    title = next((c["title"] for c in convs if c["id"] == conversation_id), "Conversa")

    return ConversationDetailDTO(
        id=conversation_id,
        title=title,
        messages=messages,
        sources=sources,
    )


@router.delete("/history/{conversation_id}")
async def delete_history(conversation_id: str):
    from backend.history import manager as hist

    hist.delete_conversation(conversation_id)
    return {"deleted": True}


# ── Settings ──────────────────────────────────────────────────────────────────


_SETTINGS_FILE = cfg.upload_dir.parent / "settings.json"


def _save_settings() -> None:
    import json

    _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _SETTINGS_FILE.write_text(
        json.dumps({"llm_provider": cfg.get_provider(), "llm_model": cfg.get_llm_model()}),
        encoding="utf-8",
    )


def load_persisted_settings() -> None:
    import json

    if not _SETTINGS_FILE.exists():
        return
    try:
        data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
        set_llm_override(**data)
    except Exception:
        pass


@router.post("/settings", response_model=LLMSettingsResponse)
async def update_settings(body: LLMSettingsRequest):
    set_llm_override(**body.model_dump())
    refresh_engine()
    _save_settings()
    return LLMSettingsResponse(
        configured=cfg.is_llm_configured(),
        provider=cfg.get_provider(),
        model=cfg.get_llm_model(),
        has_key=bool(cfg.get_active_api_key()),
    )


@router.get("/settings", response_model=LLMSettingsResponse)
async def get_settings():
    return LLMSettingsResponse(
        configured=cfg.is_llm_configured(),
        provider=cfg.get_provider(),
        model=cfg.get_llm_model(),
        has_key=bool(cfg.get_active_api_key()),
    )


# ── Health ────────────────────────────────────────────────────────────────────


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")
