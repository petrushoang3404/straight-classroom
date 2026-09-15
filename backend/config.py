from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str

    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8")


settings = Settings()
