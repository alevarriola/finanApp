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
│   ├── page.tsx                  # Redirect to /dashboard
│   ├── dashboard/page.tsx        # Dashboard: stats, charts, filters (Recharts)
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

## Auth Middleware

File: `middleware.ts` (at the root of `frontend/`)

```typescript
// Protected routes: redirects to /sign-in if no JWT cookie
export const config = {
    matcher: ["/(dashboard)/:path*"],
};
```

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

`app/(dashboard)/wallets/[id]/page.tsx` is now the main AI transaction entry point.

Current behavior:
- keeps the existing manual `TransactionFormModal`
- adds `AiTransactionPanel` for natural-language preview
- opens `AiTransactionConfirmModal` for editable confirmation
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
