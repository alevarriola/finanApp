# Kash - Global Guide for Claude Agents

## Project Description
Personal finance app called **Kash** (domain: kash-py.com). Manage wallets, record income/expenses, view balances, share accounts, and get reports with charts.

## Monorepo Structure
```
finanApp/
├── backend/       # FastAPI + Strawberry GraphQL + SQLAlchemy 2.0
├── frontend/      # Next.js 16 + React Query + Tailwind CSS + Lucide Icons
└── docker-compose.yml  # Postgres + Redis
```

## Critical Global Rules
1. **NEVER** run `alembic upgrade/downgrade` - only create migration files
2. **NEVER** use `commit()` in repositories - only `flush()`
3. **ALWAYS** use Python 3.13 syntax: `list[str]`, `str | None` (not `List`, `Optional`)
4. **NEVER** add file header docstrings
5. Repositories: ONLY data access. Services: ONLY business logic
6. All dependencies injected via `aioinject` - no global state
7. **ALWAYS** add idempotency keys to create mutations - use `app/core/idempotency.py` with Redis (see `ARCHITECTURE_REFERENCE.md` §25b)
8. **ALWAYS** use CSS variables for colors - support light/dark themes via `[data-theme="dark"]`
9. **NEVER** use `pip install` - use `uv add` (backend) or `pnpm add` (frontend)
10. **NEVER** run `git add/commit` - always give user the commands to copy/paste

## Technology Stack
- Backend: FastAPI, Strawberry GraphQL, SQLAlchemy 2.0 async, aioinject, Alembic, bcrypt, PyJWT, Resend
- Database: PostgreSQL (single schema), Redis (idempotency + cache + email verification tokens)
- Frontend: Next.js 16, React Query 5, react-hook-form, Zod, Radix UI, Tailwind CSS, Sonner, Recharts, Lucide React
- Package managers: UV (backend), pnpm (frontend)
- Dark mode: CSS variables with `[data-theme="dark"]`, persisted in localStorage
- PWA: manifest.json + service worker, installable on mobile
- Email: Resend (noreply@kash-py.com)

## App Colors
- Background: `#FFFACA` (cream yellow) / dark: `#0f1117`
- Primary: `#004F39` (dark green) / dark: `#34d399`
- Foreground: `#151613` (near black) / dark: `#e4e4e7`

## Deploy
- Backend: Railway (auto-deploy from GitHub `main` branch)
- Frontend: Vercel (auto-deploy from GitHub `main` branch)
- DNS: Cloudflare (kash-py.com)
- Email: Resend (noreply@kash-py.com, domain verified)
- Staging branch: `staging` (test before merging to `main`)

## i18n (IMPORTANT - read before writing any UI text)
- Two languages: English (en) and Spanish (es)
- Translations in `frontend/components/i18n/locales.ts`
- **ALWAYS** add both EN and ES translations when creating new user-visible text
- **ALWAYS** use `const { t } = useI18n()` + `{t("key")}` in Client Components
- **NEVER** hardcode user-visible English strings in JSX
- Server Components (layout.tsx) cannot use `useI18n()` - leave those in English
- For wallet kind labels use `t(("walletKind." + value) as TranslationKey)` pattern
- Toast messages must also use `t()` (keys: `toast.*`)
- Spanish translations should be natural, not literal (ej: Wallets = "Cuentas", Transactions = "Movimientos")
- Language switcher is in: dashboard header, landing nav, auth layout
- Note: category names come from the DB and are NOT translated via i18n


## AI Chat Feature 
- Natural-language transaction capture is already implemented as a guided flow, not as an open chat bot.
- Current entry point: wallet detail page (`frontend/app/(dashboard)/wallets/[id]/page.tsx`).
- Current backend module: `backend/app/graphql/ai_chat/`.
- Active pipeline: `validateTransaction(text)` → preview → editable confirmation modal → existing `createTransaction`.
- `ai_chat` does not persist transactions directly; final persistence must go through the normal transactions module.
- Access is intentionally restricted for now:
  - global feature flag in backend settings
  - local email allowlist file at `backend/config/ai_chat_allowed_emails.txt`
  - daily rate limit in Redis
