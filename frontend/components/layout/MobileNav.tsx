"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Wallet,
  ArrowLeftRight,
  Users,
  Settings,
} from "lucide-react";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";

const NAV_ITEMS = [
  { href: "/dashboard", labelKey: "nav.home" as TranslationKey, icon: LayoutDashboard },
  { href: "/wallets", labelKey: "nav.wallets" as TranslationKey, icon: Wallet },
  { href: "/transactions", labelKey: "nav.activity" as TranslationKey, icon: ArrowLeftRight },
  { href: "/sharing", labelKey: "nav.sharing" as TranslationKey, icon: Users },
  { href: "/settings", labelKey: "nav.settings" as TranslationKey, icon: Settings },
];

export function MobileNav() {
  const pathname = usePathname();
  const { t } = useI18n();

  return (
    <nav
      className="md:hidden fixed bottom-0 left-0 right-0 z-50 border-t flex items-center justify-around h-16 px-1"
      style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
    >
      {NAV_ITEMS.map((item) => {
        const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className="flex flex-col items-center justify-center gap-0.5 py-1 px-2 rounded-lg transition-opacity"
            style={{
              color: isActive ? "var(--primary)" : "var(--muted-foreground)",
              opacity: isActive ? 1 : 0.7,
            }}
          >
            <Icon size={20} strokeWidth={isActive ? 2.5 : 2} />
            <span className="text-[10px] font-medium">{t(item.labelKey)}</span>
          </Link>
        );
      })}
    </nav>
  );
}
