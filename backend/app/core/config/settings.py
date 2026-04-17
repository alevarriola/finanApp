import functools

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    database_url: str

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
    redis_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str
    jwt_access_token_expire_hours: int
    jwt_refresh_token_expire_days: int

    # Email (Resend)
    resend_api_key: str
    resend_from_email: str
    frontend_url: str

    # AI
    openai_api_key: str
    ai_primary_model: str
    ai_fallback_model: str
    ai_chat_enabled: bool
    ai_chat_allowlist_path: str
    ai_chat_blocklist_path: str
    ai_chat_beta_message: str
    ai_chat_blocked_message: str
    ai_chat_admin_alert_emails: list[str]
    ai_chat_max_requests_per_day: int
    ai_chat_max_input_chars: int

    # App
    environment: str
    app_name: str
    cors_origins: list[str]

    @model_validator(mode="after")
    def validate_required_strings(self) -> "Settings":
        required_fields = [
            "database_url",
            "redis_url",
            "jwt_secret",
            "jwt_algorithm",
            "resend_api_key",
            "resend_from_email",
            "frontend_url",
            "openai_api_key",
            "ai_primary_model",
            "ai_fallback_model",
            "ai_chat_allowlist_path",
            "ai_chat_blocklist_path",
            "ai_chat_beta_message",
            "ai_chat_blocked_message",
            "environment",
            "app_name",
        ]
        for field_name in required_fields:
            value = getattr(self, field_name)
            if not value or not value.strip():
                raise ValueError(f"{field_name} cannot be empty")
        if not self.cors_origins:
            raise ValueError("cors_origins cannot be empty")
        if not self.ai_chat_admin_alert_emails:
            raise ValueError("ai_chat_admin_alert_emails cannot be empty")
        if self.ai_chat_max_requests_per_day <= 0:
            raise ValueError("ai_chat_max_requests_per_day must be greater than zero")
        if self.ai_chat_max_input_chars <= 0:
            raise ValueError("ai_chat_max_input_chars must be greater than zero")
        return self

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@functools.cache
def get_settings() -> Settings:
    return Settings()
