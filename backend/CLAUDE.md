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
│   │   └── middleware/     # GraphQLAuthMiddleware (JWT + DB session)
│   ├── db/
│   │   ├── base.py         # BaseModel, HasPrimaryKey, HasCreatedAt, HasUpdatedAt
│   │   ├── engine.py       # create_engine, session factory
│   │   └── types.py        # IntEnumType — stores IntEnum as SMALLINT
│   └── graphql/
│       ├── schemas/schema.py   # Root schema — merge all queries/mutations here
│       ├── users/              # Auth: register, login, me
│       └── wallets/            # Wallets CRUD with roles
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

## Adding a New Module (checklist)
1. Create `app/graphql/<module>/` with full structure
2. Add model imports to `alembic/env.py` (`from ... import Model` + `_ = (Model,)`)
3. Register repo and service in `app/core/container.py`
4. Add queries/mutations to `app/graphql/schemas/schema.py` (Query + Mutation classes)
5. Run `uv run alembic revision --autogenerate -m "description"`
