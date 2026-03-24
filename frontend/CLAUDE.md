# Frontend — Guide for Claude Agents

## Purpose
FinanApp UI. Next.js 15 with App Router. All backend requests go through the `/api/backend` proxy.

## Structure
```
frontend/
├── app/
│   ├── (auth)/              # Public pages: /sign-in, /sign-up
│   ├── (dashboard)/         # Protected routes: /dashboard, /wallets, etc.
│   ├── api/backend/         # Proxy → backend GraphQL
│   ├── layout.tsx           # Root layout + Toaster
│   ├── globals.css          # CSS variables + Tailwind
│   └── page.tsx             # Landing page
├── components/
│   ├── shared/              # Reusable components (Button, Modal, etc.)
│   ├── ui/                  # Wrapped Radix UI primitives
│   ├── hooks/               # Custom hooks (useWallets, useTransactions, etc.)
│   ├── lib/
│   │   ├── graphql/         # client.ts — graphqlRequest()
│   │   └── toast.ts         # showSuccessToast, showErrorToast
│   ├── providers/           # QueryClientProvider, AuthProvider
│   └── [module]/            # Domain components (wallets/, transactions/)
└── middleware.ts             # JWT route protection
```

## Commands
```bash
cd frontend
pnpm install
pnpm dev       # Port 3000
pnpm build     # Production build
pnpm lint
```

## Environment Variables (`.env.local`)
```
BACKEND_GRAPHQL_URL=http://localhost:8000/graphql   # server-side only
NEXT_PUBLIC_APP_NAME=FinanApp
```

## Color Palette (CSS Variables)
Defined in `app/globals.css`:
- `--background: #FFFACA` — cream yellow
- `--primary: #004F39` — dark green
- `--foreground: #151613` — near black

Always use via Tailwind (`bg-primary`, `text-foreground`) or inline `style={{ color: "var(--primary)" }}`.

## Component Rules
1. All page components are `"use client"` unless explicitly a Server Component
2. Page structure: `Page` (minimal) → `Content` (logic) → sub-components
3. Loading states: always use skeletons, never return `null`
4. Errors: show toast + visible error state in UI
5. Forms: always use `react-hook-form` + `Zod` schema
