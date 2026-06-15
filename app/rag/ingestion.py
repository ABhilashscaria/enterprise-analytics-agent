import os
from typing import List
from app.rag.chunking import chunk_text
from app.rag.qdrant_client import ensure_collection, embed_texts
from app.config import settings
from qdrant_client.http import models as qmodels


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_docs_from_folder(folder: str) -> List[dict]:
    docs = []
    for root, _, files in os.walk(folder):
        for name in files:
            if not name.lower().endswith((".txt", ".md", ".pdf")):
                continue
            full_path = os.path.join(root, name)
            try:
                text = _read_text_file(full_path)
            except Exception:
                continue
            if not text.strip():
                continue
            docs.append(
                {
                    "path": full_path,
                    "text": text,
                }
            )
    return docs


# ... (previous code)

def ingest_folder(folder: str, max_chars: int = 800, overlap_chars: int = 120):
    client = ensure_collection()
    docs = load_docs_from_folder(folder)
    
    all_chunks = []
    for d in docs:
        chunks = chunk_text(d["text"], source=d["path"])
        all_chunks.extend(chunks)

    if not all_chunks:
        print("No chunks found.")
        return

    print(f"Generated {len(all_chunks)} chunks. Starting safe upload...")

    # Prepare points
    texts = [c["text"] for c in all_chunks]
    vectors = embed_texts(texts) # If this still kills it, see 'Batching' below

    points = [
        qmodels.PointStruct(
            id=chunk["id"],
            vector=vec,
            payload={"text": chunk["text"], **chunk["meta"]},
        )
        for chunk, vec in zip(all_chunks, vectors)
    ]

    # USE THIS: It handles batching automatically
    client.upload_points(
        collection_name=settings.qdrant_collection,
        points=points,
        batch_size=64, # Adjust this based on your RAM (32 or 64 is safe)
        parallel=2
    )

    print("Ingestion complete.")
    


