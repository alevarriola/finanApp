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
│   ├── transactions/        # TransactionList, TransactionFormModal, types, queries
│   └── invitations/         # InvitationsSection, WalletMembersSection, types, queries
├── public/                  # PWA: manifest.json, sw.js, logo.svg, icons
└── middleware.ts             # JWT route protection
```

## Commands
```bash
cd frontend
pnpm install
pnpm dev       # Port 3000
pnpm build     # Production build
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
