import Link from "next/link";
import { cookies } from "next/headers";

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
      {/* Sidebar */}
      <aside
        className="w-56 flex flex-col border-r shrink-0"
        style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
      >
        <div
          className="h-14 flex items-center px-5 border-b font-bold text-lg"
          style={{ borderColor: "var(--border)", color: "var(--primary)" }}
        >
          FinanApp
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {[
            { href: "/dashboard", label: "Dashboard" },
            { href: "/wallets", label: "Wallets" },
            { href: "/transactions", label: "Transactions" },
            { href: "/sharing", label: "Sharing" },
            { href: "/settings", label: "Settings" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block px-3 py-2 rounded-lg text-sm font-medium hover:opacity-80 transition-opacity"
              style={{ color: "var(--foreground)" }}
            >
              {item.label}
            </Link>
          ))}
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
        <header
          className="h-14 border-b flex items-center px-6"
          style={{ borderColor: "var(--border)", backgroundColor: "var(--card)" }}
        >
          <form action="/api/auth/logout" method="POST" className="ml-auto">
            <button
              type="submit"
              className="text-sm font-medium hover:underline"
              style={{ color: "var(--primary)" }}
            >
              Sign out
            </button>
          </form>
        </header>
        {user && !user.isVerified && (
          <div
            className="px-6 py-3 text-sm flex items-center justify-between"
            style={{ backgroundColor: "#fef3c7", color: "#92400e" }}
          >
            <span>Please verify your email address. Check your inbox for a verification link.</span>
            <form action="/api/auth/resend-verification" method="POST">
              <button
                type="submit"
                className="text-xs font-semibold underline hover:opacity-70"
                style={{ color: "#92400e" }}
              >
                Resend email
              </button>
            </form>
          </div>
        )}
        <div className="flex-1 p-6">{children}</div>
      </main>
    </div>
  );
}
