# Core - Guide for Claude Agents

## Purpose
Central configuration, DI container, shared ContextVars, and GraphQL auth middleware.

## Config (`app/core/config/settings.py`)

```python
from app.core.config import get_settings
settings = get_settings()  # cached with @functools.cache
```

Environment variables (in `backend/.env`):
- `DATABASE_URL` - PostgreSQL async connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - secret for signing tokens
- `JWT_ALGORITHM` - default HS256
- `JWT_ACCESS_TOKEN_EXPIRE_HOURS` - default 24
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` - default 7
- `ENVIRONMENT` - "dev" | "staging" | "production"
- `CORS_ORIGINS` - JSON list of allowed origins

AI-related variables currently required by `Settings`:
- `OPENAI_API_KEY`
- `AI_PRIMARY_MODEL`
- `AI_FALLBACK_MODEL`
- `AI_CHAT_ENABLED`
- `AI_CHAT_ALLOWLIST_PATH`
- `AI_CHAT_BETA_MESSAGE`
- `AI_CHAT_MAX_REQUESTS_PER_DAY`
- `AI_CHAT_MAX_INPUT_CHARS`

Settings in this repo are intentionally strict:
- no silent fallback defaults for secrets or feature-critical values
- missing required values should fail app startup early
- local dev must keep `backend/.env` aligned with `backend/.env.example`

## Redis Helpers

Current Redis-backed helpers:
- `app/core/idempotency.py` - create mutation deduplication
- `app/core/rate_limit.py` - lightweight per-user counters (currently used by `ai_chat`)

If you add new Redis-backed controls:
- keep keys explicit and namespaced
- close Redis clients after use
- prefer small focused helpers over embedding Redis logic directly in services

## Shared ContextVars (`app/core/context.py`)

```python
from app.core.context import session_var, auth_info_var
```

Set by `GraphQLAuthMiddleware` at the start of each request. Read by DI providers in `container.py`.
Never import and set these manually - only the middleware should write to them.

## DI Container (`app/core/container.py`)

| Scope | Lifetime | Used for |
|-------|----------|---------|
| `aioinject.Object(value)` | Forever | Settings (pre-instantiated) |
| `aioinject.Singleton(factory)` | Whole app | JWTService, session factory |
| `aioinject.Scoped(cls)` | Per request | Repositories, Services, session, auth_info |

To register a new repo/service, add to `create_container()`:

```python
from app.graphql.transactions.repositories.transaction_repository import TransactionRepository
from app.graphql.transactions.services.transaction_service import TransactionService

container.register(aioinject.Scoped(TransactionRepository))
container.register(aioinject.Scoped(TransactionService))
```

## GraphQL Auth Middleware (`app/core/middleware/graphql_middleware.py`)

Flow per request:
1. Extracts `Authorization: Bearer <token>` from header
2. Verifies JWT → sets `auth_info_var` (stays None if no/invalid token)
3. Opens `session.begin()` → sets `session_var`
4. Yields (resolvers execute)
5. Auto-commit on success, auto-rollback on exception

Public operations (register, login) don't inject `AuthInfo` so they work without a token.
Protected operations inject `AuthInfo` from DI → get 401 automatically if no valid token.

## Exceptions (`app/core/exceptions.py`)

```python
from app.core.exceptions import NotFoundError, UnauthorizedError, DuplicateError

raise NotFoundError("Wallet not found")
raise UnauthorizedError("Only the owner can archive a wallet")
raise DuplicateError("Email already registered")
```

Catch these in mutations and convert to `GraphQLError` with appropriate `statusCode`.
