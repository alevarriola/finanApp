import Link from "next/link";
import { cookies } from "next/headers";
import {
  LayoutDashboard,
  Wallet,
  ArrowLeftRight,
  Users,
  Settings,
  LogOut,
} from "lucide-react";
import { MobileNav } from "@/components/layout/MobileNav";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/wallets", label: "Wallets", icon: Wallet },
  { href: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { href: "/sharing", label: "Sharing", icon: Users },
  { href: "/settings", label: "Settings", icon: Settings },
];

async function getUser() {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;
  if (!token) return null;

  const res = await fetch(
    process.env.BACKEND_GRAPHQL_URL ?? "http://localhost:8000/graphql",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ query: "{ me { id name email isVerified } }" }),
      cache: "no-store",
    }
  );
  const json = await res.json();
  return json.data?.me ?? null;
}

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getUser();

  return (
    <div
      className="min-h-screen flex"
      style={{ backgroundColor: "var(--background)" }}
    >
      {/* Desktop sidebar — hidden on mobile */}
      <aside
        className="hidden md:flex w-56 flex-col border-r shrink-0"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
      >
        <div
          className="h-14 flex items-center px-5 border-b font-bold text-lg"
          style={{ borderColor: "var(--border)", color: "var(--primary)" }}
        >
          Kash
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium hover:opacity-80 transition-opacity"
                style={{ color: "var(--foreground)" }}
              >
                <Icon size={18} strokeWidth={2} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        {user && (
          <div
            className="px-5 py-4 border-t text-xs"
            style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            <p className="font-semibold truncate">{user.name}</p>
            <p className="opacity-60 truncate">{user.email}</p>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-auto">
        {/* Top header */}
        <header
          className="h-14 border-b flex items-center px-4 md:px-6 shrink-0"
          style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
        >
          {/* Mobile: show logo */}
          <span
            className="md:hidden font-bold text-lg"
            style={{ color: "var(--primary)" }}
          >
            Kash
          </span>
          <form action="/api/auth/logout" method="POST" className="ml-auto">
            <button
              type="submit"
              className="flex items-center gap-1.5 text-sm font-medium hover:opacity-70 transition-opacity"
              style={{ color: "var(--primary)" }}
            >
              <LogOut size={16} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          </form>
        </header>

        {/* Email verification banner */}
        {user && !user.isVerified && (
          <div
            className="px-4 md:px-6 py-3 text-sm flex items-center justify-between gap-2"
            style={{ backgroundColor: "#fef3c7", color: "#92400e" }}
          >
            <span className="text-xs sm:text-sm">Verify your email. Check your inbox.</span>
            <form action="/api/auth/resend-verification" method="POST">
              <button
                type="submit"
                className="text-xs font-semibold underline hover:opacity-70 whitespace-nowrap"
                style={{ color: "#92400e" }}
              >
                Resend
              </button>
            </form>
          </div>
        )}

        {/* Page content — extra bottom padding on mobile for nav bar */}
        <div className="flex-1 p-4 md:p-6 pb-20 md:pb-6">{children}</div>
      </main>

      {/* Mobile bottom nav */}
      <MobileNav />
    </div>
  );
}
