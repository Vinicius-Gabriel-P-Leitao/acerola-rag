from typing import Any

from pydantic import BaseModel


class JobInfoDTO(BaseModel):
    job_id: str
    filename: str
    status: str
    error: str | None = None
    created_at: str
    finished_at: str | None = None


class JobCreatedDTO(BaseModel):
    job_id: str
    filename: str


class UploadResponse(BaseModel):
    jobs: list[JobCreatedDTO]


class UploadStatusResponse(BaseModel):
    queue_size: int
    jobs: list[JobInfoDTO]


class DocumentListResponse(BaseModel):
    total: int
    items: list[dict[str, Any]]


class DocumentContentResponse(BaseModel):
    source: str
    content: str


class DeleteDocumentResponse(BaseModel):
    deleted_chunks: int


class IndexTextRequest(BaseModel):
    title: str
    content: str


class IndexTextResponse(BaseModel):
    job_id: str
    filename: str


# ── Query ─────────────────────────────────────────────────────────────────────


class AttachedFileDTO(BaseModel):
    name: str
    type: str
    size_bytes: int


class RagSourceDTO(BaseModel):
    source_file: str
    chunk_text: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    conversation_id: str
    sources: list[RagSourceDTO] = []
    error: str | None = None


# ── History ───────────────────────────────────────────────────────────────────


class ConversationDTO(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class HistoryListResponse(BaseModel):
    conversations: list[ConversationDTO]


class MessageDTO(BaseModel):
    id: int
    role: str
    content: str
    created_at: str
    attached_files: list[AttachedFileDTO] = []


class ConversationDetailDTO(BaseModel):
    id: str
    title: str
    messages: list[MessageDTO]
    sources: list[RagSourceDTO]


class HistorySearchResponse(BaseModel):
    conversations: list[dict[str, Any]]


# ── Settings ──────────────────────────────────────────────────────────────────


class LLMSettingsRequest(BaseModel):
    llm_provider: str | None = None
    llm_model: str | None = None


class LLMSettingsResponse(BaseModel):
    configured: bool
    provider: str
    model: str
    has_key: bool


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str | None = None
    detail: Any | None = None
