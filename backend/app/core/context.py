from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_info import AuthInfo

# Shared per-request context variables.
# Set by GraphQLAuthMiddleware; read by DI providers in container.py.
session_var: ContextVar[AsyncSession | None] = ContextVar("session", default=None)
auth_info_var: ContextVar[AuthInfo | None] = ContextVar("auth_info", default=None)
