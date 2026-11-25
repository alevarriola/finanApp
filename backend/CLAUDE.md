# Backend - Guide for Claude Agents

## Purpose
GraphQL API for Kash. Exposes all business logic via Strawberry GraphQL on top of FastAPI.

## Structure
```
backend/
├── app/
│   ├── api/app.py          # App factory - entry point
│   ├── auth/               # JWT service, AuthInfo
│   ├── core/
│   │   ├── config/         # Settings (pydantic-settings)
│   │   ├── context.py      # Shared per-request ContextVars (session, auth_info)
│   │   ├── container.py    # DI container (aioinject)
│   │   ├── exceptions.py   # NotFoundError, UnauthorizedError, DuplicateError
│   │   ├── idempotency.py  # Redis-based idempotency keys for create mutations
│   │   └── middleware/     # GraphQLAuthMiddleware (JWT + DB session)
│   ├── db/
│   │   ├── base.py         # BaseModel, HasPrimaryKey, HasCreatedAt, HasUpdatedAt
│   │   ├── engine.py       # create_engine, session factory
│   │   └── types.py        # IntEnumType - stores IntEnum as SMALLINT
│   └── graphql/
│       ├── schemas/schema.py   # Root schema - merge all queries/mutations here
│       ├── ai_chat/            # AI parse/validate flow for natural-language transactions
│       ├── users/              # Auth: register, login, me
│       ├── wallets/            # Wallets CRUD with roles + walletMembers query
│       ├── categories/         # Categories (global defaults + per-user), no icon field
│       ├── transactions/       # Income/expense transactions with balance calc
│       ├── invitations/        # Wallet invitations (invite, accept, reject, cancel)
│       └── reports/            # Dashboard summary, aggregations (read-only, no models)
├── alembic/                # Migrations
└── pyproject.toml
```

## Commands
```bash
cd backend
uv sync
uv run uvicorn app.api.app:create_app --factory --reload --port 8000
uv run alembic revision --autogenerate -m "description"
```

Do not run `alembic upgrade/downgrade` manually in this repo unless the user explicitly asks for it outside the normal guidance.

## GraphQL Request Flow
```
HTTP Request
  → AioInjectMiddleware (DI)
  → CORSMiddleware
  → GraphQLRouter
    → GraphQLAuthMiddleware (verifies JWT, opens DB session)
      → Resolver (@strawberry.field / @strawberry.mutation)
        → Service (business logic)
          → Repository (data access, flush())
        ← returns Strawberry type
      ← automatic commit() or rollback()
```

## Module Naming Conventions
```
app/graphql/wallets/
├── enums.py                           # IntEnum classes (WalletKind, WalletRole)
├── models/wallet.py                   # SQLAlchemy model
├── repositories/wallet_repository.py  # WalletRepository
├── services/wallet_service.py         # WalletService
├── types/wallet_types.py              # WalletType, CreateWalletInput
├── queries/wallet_queries.py          # WalletQueries
└── mutations/wallet_mutations.py      # WalletMutations
```

## Repository Rules
- Receives `session: AsyncSession` via DI only
- Only uses `flush()`, NEVER `commit()`
- Uses `selectinload()` for 1:N collections to avoid N+1
- Uses `.unique()` on result when collections are loaded

## Service Rules
- Does not access `session` directly - uses repositories
- Contains all business logic and permission checks
- Raises typed exceptions (`NotFoundError`, `UnauthorizedError`, `DuplicateError`)
- Receives `auth_info: AuthInfo` via DI for current user context

## DI Registration (aioinject)
- `Object` → fixed values (Settings)
- `Singleton` → one instance per app (session factory, JWTService)
- `Scoped` → one instance per request (repositories, services, session, auth_info)
- Register new repos/services in `app/core/container.py`

## AI Chat Module (`app/graphql/ai_chat`)

Purpose:
- parse one natural-language income/expense message
- validate it against the current user's wallets/categories
- return a safe preview for confirmation

Current flow:
1. `parseTransaction(text)` → LLM structured parse (`ParsedTransaction`)
2. `validateTransaction(text)` → Python-side resolution (`ValidatedTransaction`) + `ai_transaction_events` draft record
3. Frontend confirmation modal edits values
4. Final save uses `transactions.create_transaction`, not `ai_chat`
5. `completeAiTransactionEvent(...)` records whether the user confirmed, edited, or cancelled

Important rules:
- `AiChatService` must stay orchestration-only; do not bypass `TransactionService` for persistence
- access control lives in `AiChatService.ensure_access()`
- current restrictions include:
  - `AI_CHAT_ENABLED`
  - email allowlist path (`AI_CHAT_ALLOWLIST_PATH`)
  - email blocklist path (`AI_CHAT_BLOCKLIST_PATH`)
  - daily rate limit in Redis
  - max input length guard
- suspicious or non-transaction prompts should be rejected before calling the LLM when possible
- provider failures should be converted to safe app-level errors (`AiProviderError`), not leaked raw to GraphQL clients

Current settings used by `ai_chat`:
- `OPENAI_API_KEY`
- `AI_PRIMARY_MODEL`
- `AI_FALLBACK_MODEL`
- `AI_CHAT_ENABLED`
- `AI_CHAT_ALLOWLIST_PATH`
- `AI_CHAT_BLOCKLIST_PATH`
- `AI_CHAT_BETA_MESSAGE`
- `AI_CHAT_BLOCKED_MESSAGE`
- `AI_CHAT_ADMIN_ALERT_EMAILS`
- `AI_CHAT_MAX_REQUESTS_PER_DAY`
- `AI_CHAT_MAX_INPUT_CHARS`

Local beta access files:
- tracked example: `backend/config/ai_chat_allowed_emails.example.txt`
- tracked example: `backend/config/ai_chat_blocked_emails.example.txt`
- real local file: `backend/config/ai_chat_allowed_emails.txt`
- real local file: `backend/config/ai_chat_blocked_emails.txt`
- the real allow/block files are intentionally ignored by git

## Idempotency Keys (create mutations)
- **Always** add `idempotency_key: uuid.UUID | None = None` to create mutations
- Use `check_idempotency()` before creating, `save_idempotency()` after
- Redis-based, 5-minute TTL, key format: `idempotency:{user_id}:{key}`
- Frontend generates `crypto.randomUUID()` per submit

```python
from app.core.idempotency import check_idempotency, raise_duplicate, save_idempotency

if idempotency_key:
    if await check_idempotency(user_id, idempotency_key):
        raise_duplicate()  # → 409 error
# ... create resource ...
if idempotency_key:
    await save_idempotency(user_id, idempotency_key, {"id": str(resource.id)})
```

## Email Service (`app/core/email_service.py`)
- Uses Resend API to send emails (verification, etc.)
- Verification tokens stored in Redis with 24h TTL
- Key format: `email_verify:{token}`
- Functions: `create_verification_token()`, `get_verification_data()`, `send_verification_email()`

## Settings Auto-Fix
- `Settings.fix_database_url` validator auto-converts `postgresql://` to `postgresql+asyncpg://`
- Neon connection strings still need `sslmode`/`channel_binding` replaced with `?ssl=require` (asyncpg rejects them)

## Deploy
- **Render**: backend web service, Docker, root `backend/` (auto-deploy from GitHub main branch)
- **Neon**: PostgreSQL (`production` branch for the deploy, `dev` branch for local work)
- **Upstash**: Redis over TLS (`rediss://`)
- **Dockerfile**: Python 3.13 + uv, runs `alembic upgrade head` on startup
- **.dockerignore**: keeps `.env`, real AI allow/block lists, `.venv` and tests out of the image
- GraphiQL is served only when `ENVIRONMENT` is not `production` (`create_graphql_router(..., enable_ide=...)`)
- Environment variables set in the Render dashboard

## SQLAlchemy + MappedAsDataclass Warning
- NEVER use `from __future__ import annotations` in model files
- NEVER define scalar relationships (many-to-one) with `default=None` on `MappedAsDataclass` models
  (it clears FK columns during `__init__`). Use JOINs in the repository instead.
- For forward references in relationships, use string literals: `Mapped["Wallet"]`

## Adding a New Module (checklist)
1. Create `app/graphql/<module>/` with full structure
2. Add model imports to `tests/conftest.py` (for test DB schema creation)
3. Register repo and service in `app/core/container.py`
4. Add queries/mutations to `app/graphql/schemas/schema.py` (Query + Mutation classes)
5. Add idempotency keys to create mutations (see above)
6. Run `uv run alembic revision --autogenerate -m "description"`
7. Write tests in `tests/<module>/`
