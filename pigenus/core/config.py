import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./pigenus.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    environment: str = "production"
    log_level: str = "INFO"
    worker_heartbeat_timeout_seconds: int = 60
    job_lease_timeout_seconds: int = 300
    admin_token: str = "change-admin-token-in-production"
    version: str = "0.1.0"
    cors_origins: list[str] = ["*"]

    model_config = {"env_prefix": "PIGENUS_"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
