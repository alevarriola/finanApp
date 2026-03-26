import Link from "next/link";
import {
  Wallet,
  ArrowLeftRight,
  PieChart,
  Users,
  Shield,
  Smartphone,
} from "lucide-react";

const FEATURES = [
  {
    icon: Wallet,
    title: "Multiple wallets",
    desc: "Cash, bank accounts, debit & credit cards — all in one place.",
  },
  {
    icon: ArrowLeftRight,
    title: "Income & expenses",
    desc: "Log transactions in seconds. See your balance update instantly.",
  },
  {
    icon: PieChart,
    title: "Reports & charts",
    desc: "Understand where your money goes with visual breakdowns.",
  },
  {
    icon: Users,
    title: "Shared wallets",
    desc: "Invite family or friends to collaborate on shared accounts.",
  },
  {
    icon: Shield,
    title: "Secure by design",
    desc: "JWT auth, email verification, and encrypted passwords.",
  },
  {
    icon: Smartphone,
    title: "Works on mobile",
    desc: "Install as an app on your phone. No app store needed.",
  },
];

export default function HomePage() {
  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: "var(--background)" }}
    >
      {/* Nav */}
      <header className="flex items-center justify-between px-6 md:px-10 py-5">
        <span
          className="text-xl font-bold tracking-tight"
          style={{ color: "var(--primary)" }}
        >
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
      <section className="flex-1 flex flex-col items-center justify-center px-6 text-center gap-8 pt-8 pb-16 md:pb-24">
        <div className="space-y-5 max-w-lg">
          <div
            className="inline-block text-xs font-semibold uppercase tracking-widest px-3 py-1 rounded-full"
            style={{
              backgroundColor: "var(--secondary)",
              color: "var(--primary)",
            }}
          >
            Personal finance, simplified
          </div>
          <h1
            className="text-4xl md:text-5xl font-bold leading-tight tracking-tight"
            style={{ color: "var(--foreground)" }}
          >
            Take control of
            <br />
            <span style={{ color: "var(--primary)" }}>your money</span>
          </h1>
          <p
            className="text-sm md:text-base leading-relaxed max-w-md mx-auto"
            style={{ color: "var(--muted-foreground)" }}
          >
            Track wallets, categorize expenses, share accounts with family, and
            see exactly where your money goes.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Link
            href="/sign-up"
            className="px-8 py-3 rounded-xl font-semibold text-sm transition-opacity hover:opacity-90"
            style={{
              backgroundColor: "var(--primary)",
              color: "var(--primary-foreground)",
            }}
          >
            Get started free
          </Link>
          <Link
            href="/sign-in"
            className="px-8 py-3 rounded-xl font-semibold text-sm border transition-opacity hover:opacity-70"
            style={{
              borderColor: "var(--border)",
              color: "var(--foreground)",
            }}
          >
            Sign in
          </Link>
        </div>
      </section>

      {/* Features grid */}
      <section
        className="px-6 md:px-10 py-16 md:py-20"
        style={{ backgroundColor: "var(--card)" }}
      >
        <div className="max-w-4xl mx-auto">
          <h2
            className="text-2xl md:text-3xl font-bold text-center mb-3"
            style={{ color: "var(--foreground)" }}
          >
            Everything you need
          </h2>
          <p
            className="text-sm text-center mb-12 max-w-md mx-auto"
            style={{ color: "var(--muted-foreground)" }}
          >
            Simple tools to manage your personal finances without the
            complexity.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => {
              const Icon = f.icon;
              return (
                <div
                  key={f.title}
                  className="rounded-xl border p-5 space-y-3"
                  style={{
                    borderColor: "var(--border)",
                    backgroundColor: "var(--background)",
                  }}
                >
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{
                      backgroundColor: "var(--secondary)",
                      color: "var(--primary)",
                    }}
                  >
                    <Icon size={20} />
                  </div>
                  <h3
                    className="font-semibold text-sm"
                    style={{ color: "var(--foreground)" }}
                  >
                    {f.title}
                  </h3>
                  <p
                    className="text-xs leading-relaxed"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    {f.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-16 md:py-20 text-center">
        <h2
          className="text-2xl md:text-3xl font-bold mb-3"
          style={{ color: "var(--foreground)" }}
        >
          Ready to start?
        </h2>
        <p
          className="text-sm mb-8 max-w-sm mx-auto"
          style={{ color: "var(--muted-foreground)" }}
        >
          Free to use. No credit card required.
        </p>
        <Link
          href="/sign-up"
          className="inline-block px-8 py-3 rounded-xl font-semibold text-sm transition-opacity hover:opacity-90"
          style={{
            backgroundColor: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          Create your account
        </Link>
      </section>

      {/* Footer */}
      <footer
        className="border-t px-6 py-6 text-center"
        style={{ borderColor: "var(--border)" }}
      >
        <p
          className="text-xs"
          style={{ color: "var(--muted-foreground)" }}
        >
          Kash &mdash; Personal finance management
        </p>
      </footer>
    </div>
  );
}
