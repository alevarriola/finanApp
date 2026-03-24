from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://finanapp:finanapp@localhost:5432/finanapp"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_hours: int = 24
    jwt_refresh_token_expire_days: int = 7

    # App
    environment: str = "dev"
    app_name: str = "FinanApp"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


import functools


@functools.cache
def get_settings() -> Settings:
    return Settings()
