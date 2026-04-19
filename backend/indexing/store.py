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


def _chroma_storage(_persist_dir: Optional[Path] = None):
    from llama_index.core import StorageContext
    from llama_index.vector_stores.chroma import ChromaVectorStore

    vector_store = ChromaVectorStore.from_params(
        collection_name="acerola_rag",
        host=cfg.chroma_host,
        port=cfg.chroma_port,
    )
    return StorageContext.from_defaults(vector_store=vector_store)


def _get_storage(persist_dir: Optional[Path] = None):
    if cfg.vector_store == "chroma":
        return _chroma_storage(persist_dir)
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
    if cfg.vector_store == "chroma":
        storage_ctx = _chroma_storage()
        index = VectorStoreIndex.from_vector_store(storage_ctx.vector_store)

        # retorna None se a coleção estiver vazia (nenhum doc indexado ainda)
        collection = getattr(storage_ctx.vector_store, "_collection", None)
        if collection and collection.count() == 0:
            return None
        return index

    if not (cfg.persist_dir / "default__vector_store.json").exists():
        return None
    storage_ctx = _faiss_storage(cfg.persist_dir)
    return cast("VectorStoreIndex", load_index_from_storage(storage_ctx))
