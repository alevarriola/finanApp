# App Router - Guide for Claude Agents

## Route Structure

```
app/
├── layout.tsx                    # Root: fonts, Toaster, Providers
├── page.tsx                      # Public landing
├── globals.css                   # CSS variables and base styles
│
├── (auth)/                       # Group without dashboard layout
│   ├── sign-in/page.tsx
│   └── sign-up/page.tsx
│
├── (dashboard)/                  # JWT-protected group
│   ├── layout.tsx                # DashboardShell: sidebar + topbar
│   ├── dashboard/page.tsx        # Dashboard: stats, charts, filters (Recharts)
│   ├── chat/page.tsx             # Dedicated AI workspace + session history
│   ├── wallets/page.tsx          # Wallets list
│   ├── wallets/[id]/page.tsx     # Wallet detail: transactions + manual form + AI preview/confirm flow
│   ├── transactions/page.tsx     # Global transactions with wallet/kind/category/date filters
│   ├── sharing/page.tsx          # Manage shared wallets + invitations
│   └── settings/page.tsx         # Profile, password, dark mode toggle
│
├── verify-email/page.tsx        # Email verification (uses Suspense for useSearchParams)
│
└── api/
    ├── backend/route.ts          # Proxy -> backend GraphQL (POST)
    └── auth/
        ├── login/route.ts        # POST: validates credentials, sets JWT cookies
        ├── logout/route.ts       # POST: clears cookies, redirects to /
        ├── resend-verification/  # POST: resends verification email
        └── refresh/route.ts      # POST: renews access token
```

## Page Pattern

```tsx
// app/(dashboard)/wallets/page.tsx
import { Suspense } from "react";
import WalletsContent from "@/components/wallets/WalletsContent";
import LoadingSkeleton from "@/components/shared/LoadingSkeleton";

export default function WalletsPage() {
    return (
        <Suspense fallback={<LoadingSkeleton />}>
            <WalletsContent />
        </Suspense>
    );
}
```

## Auth Proxy

File: `proxy.ts` (at the root of `frontend/`; Next 16 renamed `middleware` to `proxy`)

```typescript
// Protected routes: redirects to /sign-in if no JWT cookie.
// Route groups like (dashboard) are not part of the URL, so every
// protected top-level path must be listed explicitly.
export const config = {
    matcher: [
        "/dashboard/:path*",
        "/wallets/:path*",
        "/transactions/:path*",
        "/sharing/:path*",
        "/settings/:path*",
        "/chat/:path*",
    ],
};
```

When adding a new page under `(dashboard)/`, add its path to the matcher.

## API Routes

### Backend Proxy (`/api/backend`)
- Reads the `access_token` cookie from the request
- Forwards to backend with `Authorization: Bearer <token>`
- Transparent to the client

### Auth Routes
- `POST /api/auth/login` - validates with backend, sets HttpOnly cookies
- `POST /api/auth/logout` - clears cookies, redirects to `/` using `request.url`
- `POST /api/auth/resend-verification` - resends email verification, redirects to `/dashboard`

**Important:** Never hardcode `localhost` in redirect URLs. Always use `new URL("/path", request.url)`.

## Wallet Detail Route Notes

AI routes:
- `app/(dashboard)/wallets/[id]/page.tsx` keeps AI capture close to a concrete wallet
- `app/(dashboard)/chat/page.tsx` is the global AI workspace with session history

Current behavior:
- keeps the existing manual `TransactionFormModal`
- uses `AiTransactionWorkspace` to drive preview, confirmation, and event completion
- the dashboard page links users into `/chat`
- invalidates `transactions`, `wallet`, `wallets`, and `dashboardSummary` after successful AI-driven save

When editing this route:
- keep the manual and AI flows independent
- do not remove the manual fallback form
- prefer small extracted components over growing the page file further

## Auth Cookies
```typescript
// HttpOnly, SameSite=lax, Secure in production
cookies().set("access_token", token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24,  // 24h
});
```
