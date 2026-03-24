# Core — Guide for Claude Agents

## Purpose
Central configuration, DI container, and GraphQL authentication middleware.

## Config (pydantic-settings)

```python
# app/core/config/settings.py
from app.core.config import get_settings
settings = get_settings()   # Cached with @functools.cache
```

Environment variables (in `.env`):
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `JWT_SECRET` — secret for signing tokens
- `JWT_ALGORITHM` — default HS256
- `ENVIRONMENT` — "dev" | "staging" | "production"
- `CORS_ORIGINS` — JSON list of allowed origins

## DI Container (aioinject)

File: `app/core/container.py`

### Scopes
| Scope | Lifetime | Use for |
|-------|----------|---------|
| `aioinject.Object(value)` | Forever | Settings (already instantiated) |
| `aioinject.Singleton(factory)` | Whole app | Session factory, Redis, JWT service |
| `aioinject.Scoped(cls)` | Per request | Repositories, services, AuthInfo |

### Registering a new Singleton
```python
# In container.py
container.register(aioinject.Singleton(create_redis_service))

def create_redis_service(settings: Settings) -> RedisService:
    return RedisService(settings.redis_url)
```

### Repositories and Services — Auto-discovery
Repositories and services are auto-registered as `Scoped` if their class name ends in `Repository` or `Service`. Just create them with the correct name.

## GraphQL Auth Middleware

File: `app/core/middleware/graphql_middleware.py`

Flow:
1. Extracts `Authorization: Bearer <token>` from header
2. Verifies JWT with `JWTService`
3. Creates `AuthInfo(user_id, email)` and injects it into DI context
4. Opens DB session, executes resolvers
5. `commit()` on success, `rollback()` on exception

```python
# How to access AuthInfo in a service
class WalletService:
    def __init__(self, repository: WalletRepository, auth_info: AuthInfo) -> None:
        self.repository = repository
        self.auth_info = auth_info  # user_id available here
```

## Auth — JWT Service

File: `app/auth/jwt_service.py`

```python
# Create token
token = jwt_service.create_access_token(user_id=user.id)

# Verify token (done automatically by middleware)
auth_info = jwt_service.verify_token(token)
```

Tokens:
- Access token: 24h (configurable via `JWT_ACCESS_TOKEN_EXPIRE_HOURS`)
- Refresh token: 7 days (configurable via `JWT_REFRESH_TOKEN_EXPIRE_DAYS`)
