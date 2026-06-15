from typing import List, Dict, Any
from qdrant_client.http import models as qmodels
from app.rag.qdrant_client import ensure_collection, embed_texts
from app.config import settings
import math


def _keyword_score(query: str, text: str) -> float:
    """
    Very simple keyword overlap score:
    intersection size / query token length.
    Not full BM25, but enough to talk about hybrid retrieval.
    """
    q_tokens = {t.lower() for t in query.split() if len(t) > 2}
    d_tokens = {t.lower() for t in text.split() if len(t) > 2}
    if not q_tokens or not d_tokens:
        return 0.0
    inter = q_tokens & d_tokens
    return len(inter) / len(q_tokens)


def retrieve_docs(
    query: str,
    top_k: int | None = None,
    max_context_chars: int | None = None,
) -> Dict[str, Any]:
    """
    Custom retriever:
    - Vector search in Qdrant
    - Keyword-aware reranking
    - Drops very low-score hits
    - Packs best chunks into a context budget
    """
    top_k = top_k or settings.rag_top_k
    max_context_chars = max_context_chars or settings.rag_max_context_chars

    client = ensure_collection()
    query_vec = embed_texts([query])[0]

    search_result = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vec,
        limit=top_k * 3,  # fetch more, then rerank
        with_payload=True,
    )

    scored_docs: List[Dict[str, Any]] = []
    for res in search_result:
        payload = res.payload or {}
        text = payload.get("text", "")
        vec_score = res.score or 0.0
        kw_score = _keyword_score(query, text)
        # combine scores (you can tweak weights)
        combined = 0.7 * vec_score + 0.3 * kw_score

        scored_docs.append(
            {
                "text": text,
                "vector_score": vec_score,
                "keyword_score": kw_score,
                "combined_score": combined,
                "meta": {k: v for k, v in payload.items() if k != "text"},
            }
        )

    # Filter very low combined scores
    filtered = [
        d for d in scored_docs
        if d["combined_score"] >= settings.rag_min_score
    ]

    # Sort by combined_score descending
    filtered.sort(key=lambda d: d["combined_score"], reverse=True)

    # Deduplicate & pack into context window budget
    seen_texts = set()
    packed_docs: List[Dict[str, Any]] = []
    total_chars = 0

    for d in filtered:
        t = d["text"].strip()
        if not t or t in seen_texts:
            continue
        # Check budget
        if total_chars + len(t) > max_context_chars:
            break
        seen_texts.add(t)
        packed_docs.append(d)
        total_chars += len(t)

        if len(packed_docs) >= top_k:
            break

    return {
        "docs": packed_docs,
        "debug": {
            "raw_hits": len(search_result),
            "filtered_hits": len(filtered),
            "returned_docs": len(packed_docs),
            "total_chars": total_chars,
        },
    }
