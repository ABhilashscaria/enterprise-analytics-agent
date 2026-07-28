from typing import List, Dict, Any
from qdrant_client.http import models as qmodels
from app.rag.qdrant_client import ensure_collection, embed_texts
from app.config import settings
import math
from sentence_transformers import CrossEncoder

_cross_encoder = None

def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        _cross_encoder = CrossEncoder(settings.cross_encoder_model)
    return _cross_encoder

def retrieve_docs(
    query: str,
    top_k: int | None = None,
    max_context_chars: int | None = None,
) -> Dict[str, Any]:
    """
    Custom retriever:
    - Vector search in Qdrant (high recall)
    - Cross-Encoder reranking (high precision)
    - Packs best chunks into a context budget
    """
    top_k = top_k or settings.rag_top_k
    max_context_chars = max_context_chars or settings.rag_max_context_chars

    client = ensure_collection()
    query_vec = embed_texts([query])[0]

    # Stage 1: High Recall Vector Search
    search_result = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vec,
        limit=top_k * 3,  # fetch more, then rerank
        with_payload=True,
    )

    if not search_result:
        return {"docs": [], "debug": {"raw_hits": 0}}

    # Stage 2: Cross-Encoder Re-Ranking
    cross_encoder = get_cross_encoder()
    
    docs_to_score = []
    pairs = []
    for res in search_result:
        payload = res.payload or {}
        text = payload.get("text", "")
        if text:
            docs_to_score.append({
                "text": text,
                "vector_score": res.score or 0.0,
                "meta": {k: v for k, v in payload.items() if k != "text"},
            })
            pairs.append((query, text))
            
    if not pairs:
        return {"docs": [], "debug": {"raw_hits": len(search_result)}}

    # Calculate true relevance scores
    ce_scores = cross_encoder.predict(pairs)

    for doc, score in zip(docs_to_score, ce_scores):
        doc["combined_score"] = float(score)

    # Filter very low scores (CrossEncoder outputs logits, usually > 0 is good)
    filtered = [
        d for d in docs_to_score
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
