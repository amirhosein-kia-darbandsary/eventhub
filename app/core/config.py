from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class PostgresSettings(BaseModel):
    user: str
    password: str
    db: str
    port: str
    host: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseModel):
    host: str
    port: str

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter="__",
        extra='forbid'
    )

    app_name: str
    debug: bool = False
    environment: str = "dev"

    postgres: PostgresSettings
    redis: RedisSettings


@lru_cache
def get_settings() -> Settings:
    """
    So we use lru cache here to prevent make instance for every func tool
    This make the instance Cache for the response of this functions.
    """
    return Settings()
