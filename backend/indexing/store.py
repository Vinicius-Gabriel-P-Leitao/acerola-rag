from pathlib import Path
from typing import Optional, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from llama_index.core import VectorStoreIndex

from backend.config import settings as cfg


_embedding_configured = False


def configure_embedding_settings() -> None:
    """Configura embeddings e chunking no LlamaIndex. LLM é configurado em engine.py."""
    global _embedding_configured
    if _embedding_configured:
        return

    from llama_index.core import Settings
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    Settings.embed_model = HuggingFaceEmbedding(model_name=cfg.embed_model)
    Settings.node_parser = SentenceSplitter(
        chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap
    )
    _embedding_configured = True


def _faiss_storage(persist_dir: Optional[Path] = None):
    import faiss
    from llama_index.core import StorageContext
    from llama_index.vector_stores.faiss import FaissVectorStore

    if persist_dir and (persist_dir / "default__vector_store.json").exists():
        vector_store = FaissVectorStore.from_persist_dir(str(persist_dir))
        return StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=str(persist_dir)
        )
    faiss_index = faiss.IndexFlatL2(cfg.embed_dim)
    return StorageContext.from_defaults(
        vector_store=FaissVectorStore(faiss_index=faiss_index)
    )


_sparse_model = None


def _get_sparse_model():
    global _sparse_model
    if _sparse_model is None:
        from fastembed import SparseTextEmbedding
        _sparse_model = SparseTextEmbedding(model_name="Qdrant/bm25")
    return _sparse_model


def _sparse_doc_fn(texts: list[str]) -> tuple[list[list[int]], list[list[float]]]:
    model = _get_sparse_model()
    embeddings = list(model.embed(texts))
    return (
        [list(e.indices) for e in embeddings],
        [list(e.values) for e in embeddings],
    )


def _sparse_query_fn(texts: list[str]) -> tuple[list[list[int]], list[list[float]]]:
    model = _get_sparse_model()
    embeddings = list(model.query_embed(texts))
    return (
        [list(e.indices) for e in embeddings],
        [list(e.values) for e in embeddings],
    )


def _qdrant_storage():
    from llama_index.core import StorageContext
    from llama_index.vector_stores.qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient

    client = QdrantClient(host=cfg.qdrant_host, port=cfg.qdrant_port)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="acerola_rag",
        enable_hybrid=True,
        sparse_doc_fn=_sparse_doc_fn,
        sparse_query_fn=_sparse_query_fn,
    )
    return StorageContext.from_defaults(vector_store=vector_store)


def _get_storage(persist_dir: Optional[Path] = None):
    if cfg.vector_store == "qdrant":
        return _qdrant_storage()
    return _faiss_storage(persist_dir)


def build_index(documents: list):
    from llama_index.core import VectorStoreIndex

    configure_embedding_settings()
    cfg.persist_dir.mkdir(parents=True, exist_ok=True)
    storage_ctx = _get_storage()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_ctx)
    if cfg.vector_store == "faiss":
        index.storage_context.persist(persist_dir=str(cfg.persist_dir))
    return index


def load_index() -> Optional["VectorStoreIndex"]:
    from llama_index.core import load_index_from_storage, VectorStoreIndex

    configure_embedding_settings()
    if cfg.vector_store == "qdrant":
        from qdrant_client import QdrantClient
        from qdrant_client.http.exceptions import UnexpectedResponse

        client = QdrantClient(host=cfg.qdrant_host, port=cfg.qdrant_port)
        try:
            info = client.get_collection("acerola_rag")
            if info.points_count == 0:
                return None
        except (UnexpectedResponse, Exception):
            return None

        storage_ctx = _qdrant_storage()
        return VectorStoreIndex.from_vector_store(storage_ctx.vector_store)

    if not (cfg.persist_dir / "default__vector_store.json").exists():
        return None
    storage_ctx = _faiss_storage(cfg.persist_dir)
    return cast("VectorStoreIndex", load_index_from_storage(storage_ctx))
