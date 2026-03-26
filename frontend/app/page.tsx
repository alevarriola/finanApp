import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: "var(--background)" }}>
      {/* Nav */}
      <header className="flex items-center justify-between px-8 py-5">
        <span className="text-lg font-bold tracking-tight" style={{ color: "var(--primary)" }}>
          Kash
        </span>
        <Link
          href="/sign-in"
          className="text-sm font-medium px-4 py-1.5 rounded-lg border transition-opacity hover:opacity-70"
          style={{ borderColor: "var(--primary)", color: "var(--primary)" }}
        >
          Sign in
        </Link>
      </header>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 text-center gap-8 pb-24">
        <div className="space-y-4 max-w-lg">
          <div
            className="inline-block text-xs font-semibold uppercase tracking-widest px-3 py-1 rounded-full mb-2"
            style={{ backgroundColor: "var(--secondary)", color: "var(--primary)" }}
          >
            Personal finance, simplified
          </div>
          <h1 className="text-5xl font-bold leading-tight tracking-tight" style={{ color: "var(--foreground)" }}>
            Take control of<br />
            <span style={{ color: "var(--primary)" }}>your money</span>
          </h1>
          <p className="text-base leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
            Track your wallets, categorize expenses, and understand where your money goes! all in one place.
          </p>
        </div>

        <div className="flex gap-3">
          <Link
            href="/sign-up"
            className="px-6 py-2.5 rounded-xl font-semibold text-sm transition-opacity hover:opacity-90"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            Get started free
          </Link>
          <Link
            href="/sign-in"
            className="px-6 py-2.5 rounded-xl font-semibold text-sm border transition-opacity hover:opacity-70"
            style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
          >
            Sign in
          </Link>
        </div>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-2 pt-2">
          {["Multiple wallets", "Transaction history", "Category tracking", "Shared wallets"].map((f) => (
            <span
              key={f}
              className="text-xs px-3 py-1.5 rounded-full border"
              style={{ borderColor: "var(--border)", color: "var(--muted-foreground)" }}
            >
              {f}
            </span>
          ))}
        </div>
      </main>
    </div>
  );
}
