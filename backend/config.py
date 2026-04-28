from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Yordamchi AI — NamDTU Transport fakulteti"
    app_version: str = "0.1.0"
    environment: str = "local"

    # Optional OpenAI-compatible provider. The app works without this key by
    # returning retrieval-based answers with citations.
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    min_relevance_score: float = 0.08
    max_context_chunks: int = 5
    knowledge_base_dir: str = "knowledge_base"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]
