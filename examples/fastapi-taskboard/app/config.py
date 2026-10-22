from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./taskboard.sqlite"
    jwt_secret: SecretStr = Field(min_length=32)
    token_minutes: int = Field(default=15, ge=1, le=60)
    cors_origins: list[str] = []


@lru_cache
def get_settings() -> Settings:
    return Settings()
