from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CallMate AI"
    app_env: str = "development"
    secret_key: str = Field(default="dev-secret-key-minimum-32-characters-long")
    debug: bool = False

    database_url: str = "postgresql+asyncpg://callmate:callmate123@localhost:5432/callmate_db"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "customer_profiles"

    jwt_secret_key: str = Field(default="dev-jwt-secret-key-minimum-32-chars!!")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    whisper_model: str = "large-v3"
    whisper_device: str = "cpu"
    whisper_language: str = "tr"

    audio_chunk_seconds: int = 3
    audio_sample_rate: int = 16000
    audio_channels: int = 1

    nlp_model: str = "dbmdz/bert-base-turkish-cased"
    sentiment_model: str = "savasy/bert-base-turkish-sentiment-cased"

    audio_encryption_key: str = "placeholder-32-byte-key-replace!!"

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "eu-central-1"
    s3_bucket_name: str = "callmate-audio-recordings"

    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    rate_limit_per_minute: int = 60

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
