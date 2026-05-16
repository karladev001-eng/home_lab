from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://techdb:techdb@localhost:5432/tech_memory"
    redis_url: str = "redis://localhost:6379"

    llm_provider: Literal["claude", "openai"] = "claude"
    embedding_provider: Literal["claude", "openai"] = "claude"

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    claude_model: str = "claude-sonnet-4-6"
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    embedding_dim: int = 1536

    class Config:
        env_file = ".env"


settings = Settings()
