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

class QueryRequest(BaseModel):
    question: str
    session_id: str = "default"

class QueryResponse(BaseModel):
    answer: str

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
