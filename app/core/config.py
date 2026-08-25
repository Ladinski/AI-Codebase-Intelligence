from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    ollama_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen2.5-coder:3b"
    pinecone_api_key: str
    pinecone_index_name: str = "codebase-intelligence"
    redis_url: str = "redis://redis:6379/0"
    rag_cache_ttl_seconds: int = 900
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        
    )


settings = Settings()