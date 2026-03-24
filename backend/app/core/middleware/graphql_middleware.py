import functools
from collections.abc import AsyncGenerator

from strawberry.extensions import SchemaExtension

from app.auth.jwt_service import JWTService
from app.core.config import get_settings
from app.core.context import auth_info_var, session_var
from app.db.engine import create_session_factory


def get_current_auth_info():
    return auth_info_var.get()


def get_current_session():
    session = session_var.get()
    if session is None:
        raise RuntimeError("No active DB session in context")
    return session


@functools.cache
def _get_jwt_service() -> JWTService:
    return JWTService(get_settings())


@functools.cache
def _get_session_factory():
    return create_session_factory(get_settings())


class GraphQLAuthMiddleware(SchemaExtension):
    async def on_operation(self) -> AsyncGenerator[None, None]:
        # --- Auth: extract and verify JWT ---
        request = self.execution_context.context["request"]
        auth_header = request.headers.get("Authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                auth_info = _get_jwt_service().verify_access_token(token)
                auth_info_var.set(auth_info)
            except ValueError:
                pass  # auth_info stays None; protected resolvers will raise 401

        # --- Session: open DB transaction ---
        factory = _get_session_factory()
        async with factory() as session:
            async with session.begin():
                session_var.set(session)
                yield
                # session.begin() auto-commits on success, auto-rollbacks on exception
