"use client";

import Link from "next/link";
import { useI18n } from "@/components/i18n/I18nProvider";
import { LanguageSwitcher } from "@/components/i18n/LanguageSwitcher";
import {
  Wallet,
  ArrowLeftRight,
  PieChart,
  Users,
  Shield,
  Smartphone,
} from "lucide-react";

import type { TranslationKey } from "@/components/i18n/locales";

const FEATURES: { icon: typeof Wallet; titleKey: TranslationKey; descKey: TranslationKey }[] = [
  { icon: Wallet, titleKey: "landing.features.wallets.title", descKey: "landing.features.wallets.desc" },
  { icon: ArrowLeftRight, titleKey: "landing.features.transactions.title", descKey: "landing.features.transactions.desc" },
  { icon: PieChart, titleKey: "landing.features.reports.title", descKey: "landing.features.reports.desc" },
  { icon: Users, titleKey: "landing.features.sharing.title", descKey: "landing.features.sharing.desc" },
  { icon: Shield, titleKey: "landing.features.security.title", descKey: "landing.features.security.desc" },
  { icon: Smartphone, titleKey: "landing.features.mobile.title", descKey: "landing.features.mobile.desc" },
];

export default function HomePage() {
  const { t } = useI18n();

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
        <div className="flex items-center gap-3">
          <LanguageSwitcher />
          <Link
          href="/sign-in"
          className="text-sm font-medium px-4 py-1.5 rounded-lg border transition-opacity hover:opacity-70"
          style={{ borderColor: "var(--primary)", color: "var(--primary)" }}
        >
          {t("common.signIn")}
          </Link>
        </div>
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
            {t("landing.badge")}
          </div>
          <h1
            className="text-4xl md:text-5xl font-bold leading-tight tracking-tight"
            style={{ color: "var(--foreground)" }}
          >
            {t("landing.title1")}
            <br />
            <span style={{ color: "var(--primary)" }}>{t("landing.title2")}</span>
          </h1>
          <p
            className="text-sm md:text-base leading-relaxed max-w-md mx-auto"
            style={{ color: "var(--muted-foreground)" }}
          >
            {t("landing.subtitle")}
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
            {t("landing.cta")}
          </Link>
          <Link
            href="/sign-in"
            className="px-8 py-3 rounded-xl font-semibold text-sm border transition-opacity hover:opacity-70"
            style={{
              borderColor: "var(--border)",
              color: "var(--foreground)",
            }}
          >
            {t("common.signIn")}
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
            {t("landing.everythingTitle")}
          </h2>
          <p
            className="text-sm text-center mb-12 max-w-md mx-auto"
            style={{ color: "var(--muted-foreground)" }}
          >
            {t("landing.everythingSubtitle")}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f) => {
              const Icon = f.icon;
              return (
                <div
                  key={f.titleKey}
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
                    {t(f.titleKey)}
                  </h3>
                  <p
                    className="text-xs leading-relaxed"
                    style={{ color: "var(--muted-foreground)" }}
                  >
                    {t(f.descKey)}
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
          {t("landing.readyTitle")}
        </h2>
        <p
          className="text-sm mb-8 max-w-sm mx-auto"
          style={{ color: "var(--muted-foreground)" }}
        >
          {t("landing.readySubtitle")}
        </p>
        <Link
          href="/sign-up"
          className="inline-block px-8 py-3 rounded-xl font-semibold text-sm transition-opacity hover:opacity-90"
          style={{
            backgroundColor: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          {t("landing.readyCta")}
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
          {t("landing.footer")}
        </p>
      </footer>
    </div>
  );
}
