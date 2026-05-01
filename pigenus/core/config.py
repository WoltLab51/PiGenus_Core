from functools import lru_cache
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./pigenus.db"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    environment: str = "production"
    log_level: str = "INFO"
    worker_heartbeat_timeout_seconds: int = 60
    job_lease_timeout_seconds: int = 300
    admin_token: str
    version: str = "0.1.0"
    cors_origins: list[str] = Field(default_factory=list)

    model_config = {"env_prefix": "PIGENUS_"}

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment == "production":
            placeholder_secret_keys = {"", "change-me-in-production"}
            placeholder_admin_tokens = {"", "change-admin-token-in-production"}
            if self.secret_key in placeholder_secret_keys:
                raise ValueError(
                    "PIGENUS_SECRET_KEY must be set to a non-placeholder value in production."
                )
            if self.admin_token in placeholder_admin_tokens:
                raise ValueError(
                    "PIGENUS_ADMIN_TOKEN must be set to a non-placeholder value in production."
                )
            if "*" in self.cors_origins:
                raise ValueError(
                    "PIGENUS_CORS_ORIGINS must not allow '*' in production."
                )
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()
