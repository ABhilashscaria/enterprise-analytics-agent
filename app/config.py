from pydantic import Basesettings

class Settings(BaseSettings):
    # LLM/vLLM
    llm_base_url: str = "https://api.openai.com/v1"
    # change to vLLM url later 
    llm_api_key: str = "dummy"

    small_model_name: str = "gpt-4o-mini"
    large_model_name: str = "gpt-4.1"


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
