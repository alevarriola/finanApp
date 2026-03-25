# Backend — Guide for Claude Agents

## Purpose
GraphQL API for FinanApp. Exposes all business logic via Strawberry GraphQL on top of FastAPI.

## Structure
```
backend/
├── app/
│   ├── api/app.py          # App factory — entry point
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
│   │   └── types.py        # IntEnumType — stores IntEnum as SMALLINT
│   └── graphql/
│       ├── schemas/schema.py   # Root schema — merge all queries/mutations here
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
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "description"
```

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
- Does not access `session` directly — uses repositories
- Contains all business logic and permission checks
- Raises typed exceptions (`NotFoundError`, `UnauthorizedError`, `DuplicateError`)
- Receives `auth_info: AuthInfo` via DI for current user context

## DI Registration (aioinject)
- `Object` → fixed values (Settings)
- `Singleton` → one instance per app (session factory, JWTService)
- `Scoped` → one instance per request (repositories, services, session, auth_info)
- Register new repos/services in `app/core/container.py`

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

## Adding a New Module (checklist)
1. Create `app/graphql/<module>/` with full structure
2. Add model imports to `alembic/env.py` (`from ... import Model` + `_ = (Model,)`)
3. Register repo and service in `app/core/container.py`
4. Add queries/mutations to `app/graphql/schemas/schema.py` (Query + Mutation classes)
5. Add idempotency keys to create mutations (see above)
6. Run `uv run alembic revision --autogenerate -m "description"`
