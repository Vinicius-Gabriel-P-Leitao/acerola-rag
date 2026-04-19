from backend.config import settings as cfg

_COLLECTION_NAME = "acerola_rag"


def _collection():
    import chromadb

    client = chromadb.HttpClient(host=cfg.chroma_host, port=cfg.chroma_port)
    return client.get_or_create_collection(_COLLECTION_NAME)


def list_documents(page: int = 1, page_size: int = 20, search: str = "") -> dict:
    col = _collection()
    result = col.get(include=["metadatas"])

    seen: dict = {}
    for meta in result.get("metadatas") or []:
        if meta is None:
            continue
        src = meta.get("source", "")
        if src and src not in seen:
            seen[src] = meta

    if search:
        searchLower = search.lower()
        seen = {k: v for k, v in seen.items() if searchLower in k.lower()}

    items = sorted(seen.values(), key=lambda m: m.get("uploaded_at", ""), reverse=True)
    total = len(items)
    start = (page - 1) * page_size
    return {"total": total, "items": items[start : start + page_size]}


def get_document_content(source: str) -> str:
    col = _collection()
    result = col.get(where={"source": source}, include=["documents"])
    docs = [d for d in (result.get("documents") or []) if d]
    return "\n\n---\n\n".join(docs)


def delete_document(source: str) -> int:
    col = _collection()
    result = col.get(where={"source": source}, include=[])
    ids = result["ids"]

    if ids:
        col.delete(ids=ids)
    return len(ids)
