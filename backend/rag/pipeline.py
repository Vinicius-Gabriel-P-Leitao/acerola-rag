from pathlib import Path

from llama_index.core import VectorStoreIndex

from backend.config import settings as cfg
from backend.indexing.store import build_index, load_index
from backend.ingestion.loader import load_document


def ingest_file(file_path: Path) -> VectorStoreIndex:
    doc = load_document(file_path)
    existing = load_index()
    
    if existing is not None:
        existing.insert(doc)
        
        if cfg.vector_store == "faiss":
            existing.storage_context.persist(persist_dir=str(cfg.persist_dir))
        return existing
    return build_index([doc])


def get_or_create_index() -> VectorStoreIndex | None:
    return load_index()
