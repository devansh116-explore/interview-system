"""
Centralized application configuration, loaded from environment variables.
Keeping all tunables here means the rest of the codebase never hardcodes
paths, model names, or thresholds -- see README "Key Design Decisions".
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./data/app.db"

    knowledge_base_dir: str = "./knowledge_base"
    vector_store_dir: str = "./data/vector_store"
    chunk_size_words: int = 120
    chunk_overlap_words: int = 25
    top_k_retrieval: int = 4
    questions_per_interview: int = 5

    question_gen_mode: str = "template"  # "template" | "llm"
    llm_provider: str = "anthropic"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def frontend_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]
        defaults = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://aptitude-frontend-1.onrender.com",
        ]
        for origin in defaults:
            if origin not in origins:
                origins.append(origin)
        return origins

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent


settings = Settings()

if settings.database_url.startswith("postgres://"):
    settings.database_url = settings.database_url.replace("postgres://", "postgresql+psycopg2://", 1)
if settings.database_url.startswith("sqlite:///./"):
    sqlite_path = settings.base_dir / settings.database_url.removeprefix("sqlite:///./")
    settings.database_url = f"sqlite:///{sqlite_path.as_posix()}"

# Ensure runtime directories exist
Path(settings.base_dir / "data").mkdir(parents=True, exist_ok=True)
Path(settings.base_dir / settings.vector_store_dir.lstrip("./")).mkdir(parents=True, exist_ok=True)
