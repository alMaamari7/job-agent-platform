from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    HF_TOKEN: str | None = None
    GITHUB_TOKEN: str | None = None

    ai_profilingagent_model: str = "deepseek-ai/DeepSeek-V4-Flash-0731"
    ai_profilingagent_provider: str = "deepinfra"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()