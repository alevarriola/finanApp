# Frontend - Guide for Claude Agents

## Purpose
Kash UI. Next.js 16 with App Router. All backend requests go through the `/api/backend` proxy.

## Structure
```
frontend/
├── app/
│   ├── (auth)/              # Public pages: /sign-in, /sign-up
│   ├── (dashboard)/         # Protected routes: /dashboard, /wallets, etc.
│   │   ├── dashboard/       # Dashboard with charts and multi-currency tabs
│   │   ├── wallets/         # Wallet list + detail with transactions
│   │   ├── transactions/    # Global transactions with filters
│   │   ├── sharing/         # Manage shared wallets + invitations
│   │   └── settings/        # Profile, password, dark mode toggle
│   ├── api/                 # API routes (backend proxy, auth, logout)
│   ├── verify-email/        # Email verification page
│   ├── layout.tsx           # Root layout + Toaster + viewport
│   ├── globals.css          # CSS variables (light + dark) + Tailwind
│   └── page.tsx             # Landing page
├── components/
│   ├── shared/              # Reusable (PasswordInput, etc.)
│   ├── i18n/                # I18nProvider, locales (EN/ES), LanguageSwitcher
│   ├── layout/              # MobileNav, InstallBanner (PWA)
│   ├── lib/
│   │   ├── graphql/         # client.ts - graphqlRequest()
│   │   └── toast.ts         # showSuccess, showError
│   ├── providers/           # QueryClientProvider + I18nProvider
│   ├── dashboard/           # reportQueries, types
│   ├── wallets/             # WalletCard, WalletFormModal, types, queries
│   ├── transactions/        # Manual form + AI preview/confirm components, types, queries
│   └── invitations/         # InvitationsSection, WalletMembersSection, types, queries
├── public/                  # PWA: manifest.json, sw.js, logo.svg, icons
└── proxy.ts                  # JWT route protection (Next 16 proxy, formerly middleware)
```

## Commands
```bash
cd frontend
pnpm install
pnpm dev       # Port 3000
pnpm build     # Production build
pnpm lint      # ESLint (flat config in eslint.config.mjs)
```

## Environment Variables (`.env.local`)
```
BACKEND_GRAPHQL_URL=http://localhost:8000/graphql   # server-side only
```

## Color Palette (CSS Variables)
Defined in `app/globals.css`:
- `--background: #FFFACA` (light) / `#0f1117` (dark)
- `--primary: #004F39` (light) / `#34d399` (dark)
- `--foreground: #151613` (light) / `#e4e4e7` (dark)

Always use `style={{ color: "var(--primary)" }}`. Never hardcode colors.

## Icons
Use **Lucide React** for all icons. Already installed.
```tsx
import { Wallet, ArrowLeftRight, Settings } from "lucide-react";
<Wallet size={18} />
```

## i18n (Internationalization)
- `I18nProvider` wraps the app via `Providers`
- Translation keys in `components/i18n/locales.ts` (English + Spanish)
- Use `useI18n()` hook in Client Components:
```tsx
import { useI18n } from "@/components/i18n/I18nProvider";
const { t } = useI18n();
<h1>{t("dashboard.title")}</h1>
```
- Language switcher in the dashboard header
- Locale persisted in `localStorage("locale")`
- Server Components (layout.tsx) can't use `useI18n()` - leave those in English

## Responsive Layout
- Desktop (md+): sidebar with icons + labels
- Mobile: bottom nav bar with 5 tabs (MobileNav component)
- Content area has `pb-20 md:pb-6` for bottom nav spacing
- All pages must work on 375px width minimum

## PWA
- `public/manifest.json` with app name, icons, standalone display
- `public/sw.js` service worker with offline fallback
- `InstallBanner` component captures `beforeinstallprompt` (Android) and shows iOS hint
- Registered in root layout `<head>` script

## Dark Mode
- Toggle via `[data-theme="dark"]` on `<html>` element
- CSS variables auto-switch in `globals.css`
- Persisted in `localStorage("theme")`, loaded in `<head>` script to prevent flash
- Settings page provides Light/Dark toggle

## Component Rules
1. All page components are `"use client"` unless explicitly a Server Component
2. Loading states: always use skeletons, never return `null`
3. Errors: show toast via `showError(err)`
4. Forms: always use `react-hook-form` + `Zod` schema
5. Create mutations **must** include `idempotencyKey: crypto.randomUUID()` as a variable
6. Use `useI18n()` for user-visible text in Client Components
7. Use Lucide icons, never emojis
8. API route redirects: use `new URL("/path", request.url)`, never hardcode localhost

## AI Transaction Flow (Current State)

Current entry points:
- wallet detail page: `app/(dashboard)/wallets/[id]/page.tsx`
- dedicated AI workspace: `app/(dashboard)/chat/page.tsx`

Current components:
- `components/transactions/AiTransactionPanel.tsx` - natural-language input + preview
- `components/transactions/AiTransactionConfirmModal.tsx` - editable confirmation before save
- `components/transactions/AiTransactionWorkspace.tsx` - shared AI flow + session history wiring
- `components/transactions/TransactionFormModal.tsx` - existing manual fallback flow

Frontend contract:
- preview uses `validateTransaction`
- final save still uses the normal `createTransaction` mutation
- AI event completion uses `completeAiTransactionEvent`
- wallet/category/date/amount edits happen only in the confirm modal
- if AI preview fails, show clear inline feedback first; use generic toast only as fallback

GraphQL client note:
- `components/lib/graphql/client.ts` now preserves both `statusCode` and optional `errorType`
- use `errorType` for AI-specific UX branches instead of string-matching raw messages
