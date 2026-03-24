# FinanApp

Personal finance manager. Track accounts/wallets, income, expenses, and balances — shareable with other users.

Self-hosted on a home server.

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python · FastAPI · Strawberry GraphQL · SQLAlchemy 2 async · aioinject · Alembic |
| Frontend | Next.js 15 App Router · React Query 5 · react-hook-form · Zod · Radix UI · Tailwind |
| Database | PostgreSQL 16 · Redis 7 |
| Auth | JWT HS256 — access token 24h · refresh token 7d · HttpOnly cookies |

---

## Project Structure

```
finanApp/
├── backend/          # GraphQL API (FastAPI + Strawberry)
├── frontend/         # Next.js 15 App Router UI
├── docker-compose.yml
└── ROADMAP.md
```

---

## Quick Start

### 1. Start infrastructure

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
cp .env.example .env          # edit JWT_SECRET at minimum
uv sync
uv run alembic upgrade head
uv run uvicorn app.api.app:create_app --factory --reload --port 8000
```

GraphiQL explorer: http://localhost:8000/graphql

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
pnpm install
pnpm dev
```

App: http://localhost:3000

---

## Development

```
backend/
├── app/
│   ├── api/app.py              # App factory
│   ├── auth/                   # JWT service, AuthInfo
│   ├── core/
│   │   ├── config/             # Settings (pydantic-settings)
│   │   ├── context.py          # Shared per-request ContextVars
│   │   ├── container.py        # DI container (aioinject)
│   │   └── middleware/         # GraphQL auth + session middleware
│   ├── db/                     # SQLAlchemy base models + engine
│   └── graphql/
│       ├── schemas/schema.py   # Root schema
│       └── users/              # User module (model/repo/service/types/queries/mutations)
```

### Adding a new domain module

Follow the pattern in `backend/app/graphql/users/`. Each module has:
- `models/` — SQLAlchemy model
- `repositories/` — DB access only, `flush()` never `commit()`
- `services/` — business logic, raises typed exceptions
- `types/` — Strawberry input/output types
- `queries/` — `@strawberry.field` resolvers
- `mutations/` — `@strawberry.mutation` resolvers

Register the new queries/mutations in `backend/app/graphql/schemas/schema.py`.

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full phase plan.

| Phase | Status |
|---|---|
| Phase 1 — Project Structure | ✅ Done |
| Phase 2 — Authentication | ✅ Done |
| Phase 3 — Wallets | Pending |
| Phase 4 — Transactions & Categories | Pending |
| Phase 5 — Sharing & Invitations | Pending |
| Phase 6 — Reports & Charts | Pending |
| Phase 7 — Production Deploy | Pending |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async connection string | — |
| `REDIS_URL` | Redis connection string | — |
| `JWT_SECRET` | Secret for signing tokens — **change in production** | — |
| `JWT_ALGORITHM` | Signing algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_HOURS` | Access token lifetime | `24` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `ENVIRONMENT` | `dev` / `staging` / `production` | `dev` |
| `CORS_ORIGINS` | JSON array of allowed origins | `["http://localhost:3000"]` |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `BACKEND_GRAPHQL_URL` | Internal backend URL (server-side only) |
| `NEXT_PUBLIC_APP_NAME` | App name shown in UI |
