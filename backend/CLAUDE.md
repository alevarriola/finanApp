# Backend — Guide for Claude Agents

## Purpose
GraphQL API for FinanApp. Exposes all business logic via Strawberry GraphQL on top of FastAPI.

## Structure
```
backend/
├── app/
│   ├── api/app.py          # App factory — entry point
│   ├── auth/               # JWT service, AuthInfo, auth middleware
│   ├── core/
│   │   ├── config/         # Settings with pydantic-settings
│   │   ├── container.py    # DI container (aioinject)
│   │   └── middleware/     # GraphQL middleware (auth + session)
│   ├── db/
│   │   ├── base.py         # BaseModel, HasPrimaryKey, HasCreatedAt, HasUpdatedAt
│   │   └── engine.py       # create_engine, session factory
│   └── graphql/
│       ├── schemas/schema.py   # Main schema, type merging
│       └── [module]/           # One directory per domain
├── alembic/                # Migrations
└── pyproject.toml          # UV dependencies
```

## Commands
```bash
cd backend
uv sync                                                          # Install deps
uv run uvicorn app.api.app:create_app --factory --reload --port 8000  # Dev server
uv run alembic revision --autogenerate -m "description"         # New migration
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

## Naming Conventions
```
app/graphql/wallets/
├── models/wallet.py                   # SQLAlchemy model
├── repositories/wallet_repository.py  # WalletRepository
├── services/wallet_service.py         # WalletService
├── types/wallet_types.py              # WalletType, CreateWalletInput
├── queries/wallet_queries.py          # WalletQueries
├── mutations/wallet_mutations.py      # WalletMutations
└── enums.py
```

## Repository Rules
- Receives `session: AsyncSession` via DI only
- Only uses `flush()`, NEVER `commit()`
- Uses `joinedload()` to prevent N+1 queries
- Uses `unique()` when collections are joinedloaded
- Returns domain objects, not raw rows

## Service Rules
- Does not access `session` directly — uses repositories
- Contains all business logic
- Raises typed exceptions (`NotFoundError`, `UnauthorizedError`)
- Receives `auth_info: AuthInfo` via DI for user context

## DI Registration (aioinject)
- `Object` → fixed values (Settings)
- `Singleton` → one instance per app (session factory, Redis)
- `Scoped` → one instance per request (repositories, services)
- Repositories and Services are auto-registered by class name suffix
