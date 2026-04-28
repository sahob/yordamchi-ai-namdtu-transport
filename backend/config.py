from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Yordamchi AI — NamDTU Transport fakulteti"
    app_version: str = "0.2.1-render-ready"
    environment: str = "local"

    # RAG platforma uchun AI modeli talab qilinadi. OPENAI_API_KEY bo'lmasa,
    # tizim faqat manba topadi, lekin AI javob yaratmaydi.
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # Qidiruv sozlamalari
    max_context_chunks: int = 8
    min_keyword_score: float = 0.03
    min_vector_score: float = 0.20
    use_vector_search: bool = True

    # Render/free hostingda server tez start bo'lishi uchun vektor indeksni
    # avtomatik qurmaymiz. Agar .cache/vector_index.json oldindan tayyor bo'lsa,
    # tizim uni tez yuklaydi. Indeksni lokalda scripts/build_vector_index.py bilan quring.
    build_vector_index_on_startup: bool = False

    knowledge_base_dir: str = "knowledge_base"
    vector_index_path: str = ".cache/vector_index.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]
