# Kash

Personal finance app. Track wallets, record income and expenses, share accounts with family, and visualize reports with charts.

**Live:** [kash-py.com](https://kash-py.com)

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.13, FastAPI, Strawberry GraphQL, SQLAlchemy 2.0 async, aioinject, Alembic |
| Frontend | Next.js 15, React Query 5, react-hook-form, Zod, Tailwind CSS, Recharts, Lucide React |
| Database | PostgreSQL 16, Redis 7 |
| Auth | JWT HS256, access token 24h, refresh token 7d, HttpOnly cookies |
| Email | Resend (noreply@kash-py.com) |
| Deploy | Railway (backend + DB + Redis), Vercel (frontend), Cloudflare (DNS) |
| PWA | manifest.json + service worker, installable on mobile |

---

## Features

- Multiple wallets (cash, bank, debit, credit) with per-wallet balance
- Income and expense tracking with categories
- Dashboard with charts: expenses by category (pie), monthly evolution (area)
- Multi-currency support (PYG, USD, etc.) with separate dashboards per currency
- Shared wallets: invite by email with roles (viewer/editor)
- Email verification via Resend
- Dark mode (CSS variables, persisted in localStorage)
- Responsive: desktop sidebar + mobile bottom nav
- PWA: installable on Android and iOS
- i18n: English and Spanish with language switcher

---

## Quick Start (local dev)

### 1. Infrastructure

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
cp .env.example .env    # edit JWT_SECRET and RESEND_API_KEY
uv sync
uv run alembic upgrade head
uv run uvicorn app.api.app:create_app --factory --reload --port 8000
```

GraphiQL: http://localhost:8000/graphql

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
pnpm install
pnpm dev
```

App: http://localhost:3000

---

## Project Structure

```
finanApp/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI app factory
│   │   ├── auth/            # JWT service, AuthInfo
│   │   ├── core/            # Config, DI container, middleware, idempotency, email
│   │   ├── db/              # SQLAlchemy base models + engine
│   │   └── graphql/         # Domain modules
│   │       ├── users/       # Auth: register, login, profile, email verification
│   │       ├── wallets/     # CRUD, roles, members, leave
│   │       ├── categories/  # Global defaults + per-user custom
│   │       ├── transactions/ # Income/expense with balance calc
│   │       ├── invitations/ # Invite, accept, reject, cancel
│   │       └── reports/     # Dashboard aggregations, multi-currency
│   ├── alembic/             # Database migrations
│   └── tests/               # pytest, 96 tests, 54% coverage
├── frontend/
│   ├── app/                 # Next.js pages (auth, dashboard, wallets, etc.)
│   ├── components/          # React components, hooks, i18n, GraphQL client
│   └── public/              # PWA manifest, icons, service worker
├── ROADMAP.md               # Phase plan (1-8)
└── docker-compose.yml       # PostgreSQL + Redis
```

---

## Phases

| Phase | Status |
|---|---|
| 1. Project foundation | Done |
| 2. Authentication | Done |
| 3. Wallets | Done |
| 4. Transactions and categories | Done |
| 5. Shared wallets and invitations | Done |
| 6. Dashboard and reports | Done |
| 7. Production deploy | Done (Railway + Vercel + Cloudflare) |
| 8. AI chat (planned) | See ROADMAP.md |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Secret for signing tokens |
| `RESEND_API_KEY` | Resend API key for email |
| `RESEND_FROM_EMAIL` | Sender address (noreply@kash-py.com) |
| `FRONTEND_URL` | Frontend URL for email links |
| `ENVIRONMENT` | dev / staging / production |
| `CORS_ORIGINS` | JSON array of allowed origins |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `BACKEND_GRAPHQL_URL` | Backend GraphQL URL (server-side only) |

---

## Tests

```bash
cd backend
uv run pytest           # run all tests
uv run pytest -v        # verbose
uv run pytest --tb=short # short tracebacks
```
