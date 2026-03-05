from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer
from app.config import settings

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

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Use local sentence-transformers to embed texts."""
    # encode() returns a numpy array. We convert it to a standard Python list 
    # of lists so Qdrant can process it properly.
    embeddings = embedding_model.encode(texts).tolist()
    return embeddings
