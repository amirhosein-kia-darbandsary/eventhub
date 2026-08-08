from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class PostgresSettings(BaseModel):
    user: str
    password: str
    name: str
    port: str
    host: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class JwtSettings(BaseModel):
    private_key_path: str = "keys/private.pem"
    public_key_pasth: str = "keys/public.pem"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


class RedisSettings(BaseModel):
    host: str
    port: str
    name: str

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.name}"


class CORSSettings(BaseModel):
    allow_origins: list[str] = ["*"]  # default for development
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter="__",
        extra='forbid'
    )

    app_name: str = "eventhub"
    debug: bool = False
    environment: str = "dev"

    jwt: JwtSettings = JwtSettings()
    cors: CORSSettings = CORSSettings()
    postgres: PostgresSettings
    redis: RedisSettings


@lru_cache
def get_settings() -> Settings:
    """
    So we use lru cache here to prevent make instance for every func tool
    This make the instance Cache for the response of this functions.
    """
    return Settings()
