# FinanApp — Global Guide for Claude Agents

## Project Description
Personal finance app. Allows managing accounts/wallets, recording income and expenses, viewing balances, and sharing accounts with other users.

## Monorepo Structure
```
finanApp/
├── backend/       # FastAPI + Strawberry GraphQL + SQLAlchemy 2.0
├── frontend/      # Next.js 15 + React Query + Tailwind CSS
├── ROADMAP.md     # Phase status and pending tasks
└── docker-compose.yml  # Postgres + Redis
```

## Critical Global Rules
1. **NEVER** run `alembic upgrade/downgrade` — only create migration files
2. **NEVER** use `commit()` in repositories — only `flush()`
3. **ALWAYS** use Python 3.13 syntax: `list[str]`, `str | None` (not `List`, `Optional`)
4. **NEVER** add file header docstrings
5. Repositories: ONLY data access. Services: ONLY business logic
6. All dependencies injected via `aioinject` — no global state
7. **ALWAYS** add idempotency keys to create mutations — use `app/core/idempotency.py` with Redis (see `ARCHITECTURE_REFERENCE.md` §25b)
8. **ALWAYS** use CSS variables for colors — support light/dark themes via `[data-theme="dark"]`

## Technology Stack
- Backend: FastAPI, Strawberry GraphQL, SQLAlchemy 2.0 async, aioinject, Alembic, bcrypt, PyJWT
- Database: PostgreSQL (single schema), Redis (idempotency + cache)
- Frontend: Next.js 15, React Query 5, react-hook-form, Zod, Radix UI, Tailwind CSS, Sonner, Recharts
- Package managers: UV (backend), pnpm (frontend)
- Dark mode: CSS variables with `[data-theme="dark"]`, persisted in localStorage

## App Colors
- Background: `#FFFACA` (cream yellow)
- Primary: `#004F39` (dark green)
- Foreground: `#151613` (near black)

## Project Phases
See [ROADMAP.md](./ROADMAP.md) for current status and pending tasks.
