# App Router — Guide for Claude Agents

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
│   ├── wallets/[id]/page.tsx     # Wallet detail: transactions + add form
│   ├── transactions/page.tsx     # Global transactions with wallet/kind/category/date filters
│   ├── sharing/page.tsx          # Manage shared wallets + invitations
│   └── settings/page.tsx         # Profile, password, dark mode toggle
│
└── api/
    ├── backend/route.ts          # Proxy → backend GraphQL (POST)
    └── auth/
        ├── login/route.ts        # POST: receives credentials, sets JWT cookie
        ├── logout/route.ts       # POST: clears cookies
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
- `POST /api/auth/login` → validates with backend, sets HttpOnly cookies
- `POST /api/auth/logout` → clears cookies
- `GET /api/auth/me` → returns current user data from cookie

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
