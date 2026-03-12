from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM/vLLM
    llm_base_url: str = "https://api.groq.com/openai/v1"
    # change to vLLM url later 
    llm_api_key: str = "dummy"

    small_model_name: str = "llama-3.1-8b-versatile"
    large_model_name: str = "llama-3.3-70b-instant"


    # Langfuse
    langfuse_host: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None


    #Qdrant / DB

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "analytics_docs"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    
    
     #RAG tuning
    rag_top_k: int = 8
    rag_max_context_chars: int = 4000
    rag_min_score: float = 0.2  # drop very low-score hits


    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
