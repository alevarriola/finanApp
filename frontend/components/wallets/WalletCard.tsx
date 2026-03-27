"use client";

import Link from "next/link";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";
import { Wallet } from "./types";

interface WalletCardProps {
  wallet: Wallet;
  onEdit: (wallet: Wallet) => void;
  onArchive: (wallet: Wallet) => void;
}

export function WalletCard({ wallet, onEdit, onArchive }: WalletCardProps) {
  const { t } = useI18n();
  const canEdit = wallet.myRole === "OWNER" || wallet.myRole === "EDITOR";
  const canArchive = wallet.myRole === "OWNER";

  const formattedBalance = new Intl.NumberFormat("es-PY", {
    style: "currency",
    currency: wallet.currency,
    minimumFractionDigits: 0,
  }).format(wallet.currentBalance);

  return (
    <div
      className="rounded-xl border p-5 flex flex-col gap-3 hover:shadow-sm transition-shadow cursor-pointer"
      style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <p className="font-semibold text-sm leading-tight" style={{ color: "var(--foreground)" }}>
              {wallet.name}
            </p>
            <p className="text-xs opacity-50" style={{ color: "var(--foreground)" }}>
              {t(("walletKind." + wallet.walletKind) as TranslationKey)}
            </p>
          </div>
        </div>

        {(canEdit || canArchive) && (
          <div className="flex gap-1">
            {canEdit && (
              <button
                onClick={() => onEdit(wallet)}
                className="text-xs px-2 py-1 rounded-md hover:opacity-70 transition-opacity"
                style={{ color: "var(--primary)" }}
              >
                {t("wallets.edit")}
              </button>
            )}
            {canArchive && (
              <button
                onClick={() => onArchive(wallet)}
                className="text-xs px-2 py-1 rounded-md hover:opacity-70 transition-opacity opacity-40"
                style={{ color: "var(--foreground)" }}
              >
                {t("wallets.archive")}
              </button>
            )}
          </div>
        )}
      </div>

      <Link href={`/wallets/${wallet.id}`} className="block">
        <p className="text-xs opacity-50 mb-0.5" style={{ color: "var(--foreground)" }}>
          {t("wallets.balance")}
        </p>
        <p className="text-xl font-bold" style={{ color: "var(--primary)" }}>
          {formattedBalance}
        </p>
      </Link>

      <div className="flex items-center justify-between">
        <span
          className="text-xs px-2 py-0.5 rounded-full"
          style={{ backgroundColor: "var(--muted)", color: "var(--foreground)" }}
        >
          {wallet.currency}
        </span>
        {wallet.myRole !== "OWNER" && (
          <span className="text-xs opacity-40" style={{ color: "var(--foreground)" }}>
            {wallet.myRole.toLowerCase()}
          </span>
        )}
      </div>
    </div>
  );
}
