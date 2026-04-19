import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.api import ingestion_queue as iq
from backend.config import set_llm_override, settings as cfg
from backend.rag.engine import query, refresh_engine

router = APIRouter()

_ALLOWED = {".pdf", ".docx", ".doc", ".txt", ".md"}


# ── Upload ────────────────────────────────────────────────────────────────────


class UploadResponse(BaseModel):
    jobs: list[dict]


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
        created.append({"job_id": job.job_id, "filename": job.filename})
    return UploadResponse(jobs=created)


@router.get("/upload/status")
async def upload_status():
    return {
        "queue_size": iq.queue_size(),
        "jobs": [
            {
                "job_id": job.job_id,
                "filename": job.filename,
                "status": job.status,
                "error": job.error,
                "created_at": job.created_at,
                "finished_at": job.finished_at,
            }
            for job in iq.all_jobs()
        ],
    }


@router.get("/upload/status/{job_id}")
async def upload_job_status(job_id: str):
    job = iq.get_job(job_id)
    if not job:
        raise HTTPException(404, "Job não encontrado")
    return {
        "job_id": job.job_id,
        "filename": job.filename,
        "status": job.status,
        "error": job.error,
        "created_at": job.created_at,
        "finished_at": job.finished_at,
    }


# ── Documents (admin) ─────────────────────────────────────────────────────────


@router.get("/documents")
async def list_documents(page: int = 1, page_size: int = 20, search: str = ""):
    from backend.indexing.documents import list_documents as _list

    return _list(page=page, page_size=page_size, search=search)


@router.get("/documents/{source}/content")
async def get_document_content(source: str):
    from backend.indexing.documents import get_document_content as _content

    content = _content(source)
    if not content:
        raise HTTPException(404, f"Documento '{source}' não encontrado")
    return {"source": source, "content": content}


@router.delete("/documents/{source}")
async def delete_document(source: str):
    from backend.indexing.documents import delete_document as _delete

    deleted = _delete(source)
    refresh_engine()
    return {"deleted_chunks": deleted}


class IndexTextRequest(BaseModel):
    title: str
    content: str


@router.post("/documents/text", status_code=202)
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
    return {"job_id": job.job_id, "filename": job.filename}


# ── Query ─────────────────────────────────────────────────────────────────────


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str


@router.post("/query", response_model=QueryResponse)
async def query_documents(req: QueryRequest):
    if not cfg.is_llm_configured():
        raise HTTPException(
            status_code=422,
            detail=(
                f"Modelo não configurado corretamente para o provider "
                f"'{cfg.get_provider()}'. Verifique a API key no painel lateral."
            ),
        )
    answer = query(req.question)
    return QueryResponse(answer=answer)


# ── Settings ──────────────────────────────────────────────────────────────────


class LLMSettingsRequest(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None


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


@router.post("/settings")
async def update_settings(body: LLMSettingsRequest):
    set_llm_override(**body.model_dump())
    refresh_engine()
    _save_settings()
    return {
        "configured": cfg.is_llm_configured(),
        "provider": cfg.get_provider(),
        "model": cfg.get_llm_model(),
        "has_key": bool(cfg.get_active_api_key()),
    }


@router.get("/settings")
async def get_settings():
    return {
        "configured": cfg.is_llm_configured(),
        "provider": cfg.get_provider(),
        "model": cfg.get_llm_model(),
        "has_key": bool(cfg.get_active_api_key()),
    }


# ── Health ────────────────────────────────────────────────────────────────────


@router.get("/health")
async def health():
    return {"status": "ok"}
