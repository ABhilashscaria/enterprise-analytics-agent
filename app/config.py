from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLM/vLLM
    llm_base_url: str = "https://api.openai.com/v1"
    # change to vLLM url later 
    llm_api_key: str = "dummy"

    small_model_name: str = "llama-3.3-70b-versatile"
    large_model_name: str = "llama-3.1-8b-instant"


    # Langfuse
    langfuse_host: str | None = None
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None


    #Qdrant / DB

    qdrant_url: str | None = None
    qdrant_api_key: str | None = None


    class Config:
        env_file = ".env"

settings = Settings()
