"use client";

import Link from "next/link";
import {
  LayoutDashboard,
  Wallet,
  ArrowLeftRight,
  Users,
  Settings,
  Sparkles,
} from "lucide-react";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";

const NAV_ITEMS = [
  { href: "/dashboard", labelKey: "nav.dashboard" as TranslationKey, icon: LayoutDashboard },
  { href: "/wallets", labelKey: "nav.wallets" as TranslationKey, icon: Wallet },
  { href: "/transactions", labelKey: "nav.transactions" as TranslationKey, icon: ArrowLeftRight },
  { href: "/chat", labelKey: "nav.ai" as TranslationKey, icon: Sparkles },
  { href: "/sharing", labelKey: "nav.sharing" as TranslationKey, icon: Users },
  { href: "/settings", labelKey: "nav.settings" as TranslationKey, icon: Settings },
];

export function SidebarNav() {
  const { t } = useI18n();

  return (
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
            {t(item.labelKey)}
          </Link>
        );
      })}
    </nav>
  );
}
