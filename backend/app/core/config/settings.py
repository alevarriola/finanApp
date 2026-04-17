import functools

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://finanapp:finanapp@localhost:5432/finanapp"

    @model_validator(mode="after")
    def fix_database_url(self) -> "Settings":
        if self.database_url.startswith("postgresql://"):
            self.database_url = self.database_url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )
        return self

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_hours: int = 24
    jwt_refresh_token_expire_days: int = 7

    # Email (Resend)
    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"
    frontend_url: str = "http://localhost:3000"

    # AI
    openai_api_key: str = ""
    ai_primary_model: str = "gpt-4.1-mini"
    ai_fallback_model: str = "gpt-4o-mini"

    # App
    environment: str = "dev"
    app_name: str = "Kash"
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )
@functools.cache
def get_settings() -> Settings:
    return Settings()
