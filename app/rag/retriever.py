import uuid
from typing import List, Dict, Any
from qdrant_client.http import models as qmodels
from app.rag.qdrant_client import ensure_collection, embed_texts
from app.config import settings


def ingest_chunks(chunks: List[Dict[str, Any]]):
    """
    chunks: list of { "id": str, "text": str, "meta": dict }
    """
    client = ensure_collection()
    vectors = embed_texts([c["text"] for c in chunks])

    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[
            qmodels.PointStruct(
                id=c["id"],
                vector=v,
                payload={
                    "text": c["text"],
                    **(c.get("meta") or {}),
                },
            )
            for c, v in zip(chunks, vectors)
        ],
    )


def retrieve_docs(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    client = ensure_collection()
    query_vec = embed_texts([query])[0]

    response = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vec,  # Note: The parameter is now 'query', not 'query_vector'
        limit=top_k,
        with_payload=True,
    )
    search_result = response.points

    docs = []
    for res in search_result:
        payload = res.payload or {}
        docs.append(
            {
                "text": payload.get("text", ""),
                "score": res.score,
                "meta": {k: v for k, v in payload.items() if k != "text"},
            }
        )
    return docs


# Convenience helper for later ingestion
def make_chunks_from_text(text: str, source: str = "manual", max_chars: int = 600) -> List[Dict[str, Any]]:
    paragraphs = []
    buf = ""
    for line in text.splitlines():
        if not line.strip():
            continue
        if len(buf) + len(line) > max_chars:
            paragraphs.append(buf)
            buf = line
        else:
            buf = (buf + " " + line).strip()
    if buf:
        paragraphs.append(buf)

    return [
        {
            "id": str(uuid.uuid4()),
            "text": para,
            "meta": {"source": source},
        }
        for para in paragraphs
    ]
