import json

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector

from backend.config import settings as cfg

_COLLECTION_NAME = "acerola_rag"


def _client() -> QdrantClient:
    return QdrantClient(host=cfg.qdrant_host, port=cfg.qdrant_port)


def list_documents(page: int = 1, page_size: int = 20, search: str = "") -> dict:
    client = _client()

    try:
        all_points = []
        offset = None
        while True:
            results, offset = client.scroll(
                collection_name=_COLLECTION_NAME,
                with_payload=True,
                with_vectors=False,
                limit=100,
                offset=offset,
            )
            all_points.extend(results)
            if offset is None:
                break
    except Exception:
        return {"total": 0, "items": []}

    seen: dict = {}
    for point in all_points:
        payload = point.payload or {}
        src = payload.get("source", "")
        if src and src not in seen:
            seen[src] = {k: v for k, v in payload.items() if not k.startswith("_")}

    if search:
        search_lower = search.lower()
        seen = {k: v for k, v in seen.items() if search_lower in k.lower()}

    items = sorted(seen.values(), key=lambda m: m.get("uploaded_at", ""), reverse=True)
    total = len(items)
    start = (page - 1) * page_size
    return {"total": total, "items": items[start : start + page_size]}


def get_document_content(source: str) -> str:
    client = _client()

    results, _ = client.scroll(
        collection_name=_COLLECTION_NAME,
        scroll_filter=Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=source))]
        ),
        with_payload=True,
        with_vectors=False,
        limit=1000,
    )

    texts = []
    for point in results:
        payload = point.payload or {}
        node_content = payload.get("_node_content", "")
        if node_content:
            try:
                node = json.loads(node_content)
                text = node.get("text", "")
                if text:
                    texts.append(text)
            except (json.JSONDecodeError, AttributeError):
                pass

    return "\n\n---\n\n".join(texts)


def delete_document(source: str) -> int:
    client = _client()

    results, _ = client.scroll(
        collection_name=_COLLECTION_NAME,
        scroll_filter=Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=source))]
        ),
        with_payload=False,
        with_vectors=False,
        limit=10000,
    )
    count = len(results)

    if count > 0:
        client.delete(
            collection_name=_COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[FieldCondition(key="source", match=MatchValue(value=source))]
                )
            ),
        )

    return count
