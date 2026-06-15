from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer
from app.config import settings
from typing import List

# 1. Initialize the local embedding model
# This will download the model to your machine the very first time it runs
embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

# 2. Update the dimension size for this specific model
EMBED_DIM = 384  # BAAI/bge-small-en-v1.5 dimension size

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )

def ensure_collection():
    client = get_qdrant_client()
    collections = client.get_collections().collections
    names = {c.name for c in collections}
    
    if settings.qdrant_collection not in names:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=qmodels.VectorParams(
                size=EMBED_DIM,
                distance=qmodels.Distance.COSINE,
            ),
        )
    return client

def embed_texts(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Embeds a list of strings in small batches to prevent OOM (Out of Memory) crashes.
    """
    from sentence_transformers import SentenceTransformer
    
    # Load model (ensure this is cached/singleton in your real app)
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    
    all_embeddings = []
    
    # Process in chunks of 32
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        # show progress for large files
        print(f"  Embedding batch {i//batch_size + 1}...") 
        
        batch_vecs = model.encode(batch, convert_to_numpy=True).tolist()
        all_embeddings.extend(batch_vecs)
        
    return all_embeddings
