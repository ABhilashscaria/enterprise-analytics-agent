from app.rag.chunking import chunk_text
from app.rag.qdrant_client import ensure_collection, embed_texts
from app.config import settings
from qdrant_client.http import models as qmodels

TEXT = """
A data warehouse is a central repository of integrated data from various sources.
It stores current and historical data used for reporting and analysis.
The warehouse typically includes fact tables and dimension tables.
"""

def ingest_sample():
    client = ensure_collection()
    # Phase 1: Explicitly tracking the source metadata
    chunks = chunk_text(TEXT, source="sample_data_warehouse.txt")
    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)
    
    points = [
        qmodels.PointStruct(
            id=chunk["id"],
            vector=vec,
            payload={"text": chunk["text"], **chunk["meta"]},
        )
        for chunk, vec in zip(chunks, vectors)
    ]
    
    client.upload_points(
        collection_name=settings.qdrant_collection,
        points=points,
    )
    print(f"Ingested {len(chunks)} chunks into Qdrant with source metadata.")

if __name__ == "__main__":
    ingest_sample()
