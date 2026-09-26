from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # Defaulted so the app runs out of the box in dev; override in .env for
    # anything that isn't a throwaway local database.
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 60 * 24

    # Object storage for classroom materials. The endpoint is what gets baked
    # into presigned URLs, so it must be reachable from the browser too.
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "classroom-materials"
    minio_secure: bool = False

    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8")


settings = Settings()
