from pathlib import Path


from pydantic_settings import BaseSettings, SettingsConfigDict
BASE_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    HF_TOKEN: str
    ai_profilingagent_model: str = "deepseek-ai/DeepSeek-V4-Flash-0731"
    ai_profilingagent_provider: str = "deepinfra"
    GITHUB_TOKEN: str
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()