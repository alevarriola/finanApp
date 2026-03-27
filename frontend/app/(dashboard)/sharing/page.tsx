"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showSuccess, showError } from "@/components/lib/toast";
import { useI18n } from "@/components/i18n/I18nProvider";
import { WalletMembersSection } from "@/components/invitations/WalletMembersSection";
import { Wallet } from "@/components/wallets/types";
import type { TranslationKey } from "@/components/i18n/locales";
import { WALLETS_QUERY, LEAVE_WALLET_MUTATION } from "@/components/wallets/walletQueries";

export default function SharingPage() {
  const { t } = useI18n();
  const queryClient = useQueryClient();
  const [expandedWalletId, setExpandedWalletId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["wallets"],
    queryFn: () => graphqlRequest<{ wallets: Wallet[] }>(WALLETS_QUERY),
  });

  const leaveMutation = useMutation({
    mutationFn: (walletId: string) =>
      graphqlRequest(LEAVE_WALLET_MUTATION, { walletId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      showSuccess(t("toast.leftWallet"));
    },
    onError: showError,
  });

  const wallets = data?.wallets ?? [];
  const sharedWithMe = wallets.filter((w) => w.myRole !== "OWNER");
  const myWallets = wallets.filter((w) => w.myRole === "OWNER");

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="h-8 w-40 rounded animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
        {[1, 2].map((i) => (
          <div key={i} className="h-20 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
        ))}
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-10">
      <div>
        <h1 className="text-2xl font-bold mb-1" style={{ color: "var(--foreground)" }}>
          {t("sharing.title")}
        </h1>
        <p className="text-sm opacity-60" style={{ color: "var(--foreground)" }}>
          {t("sharing.subtitle")}
        </p>
      </div>

      {/* Shared with me */}
      <section>
        <h2 className="text-base font-semibold mb-3" style={{ color: "var(--foreground)" }}>
          {t("sharing.sharedWithMe")}
        </h2>
        {sharedWithMe.length === 0 ? (
          <p className="text-sm opacity-50" style={{ color: "var(--foreground)" }}>
            {t("sharing.noShared")}
          </p>
        ) : (
          <div className="space-y-2">
            {sharedWithMe.map((wallet) => {
              const formatted = new Intl.NumberFormat("en-US", {
                style: "currency",
                currency: wallet.currency,
                minimumFractionDigits: 0,
              }).format(wallet.currentBalance);

              return (
                <div
                  key={wallet.id}
                  className="rounded-xl border px-4 py-3"
                  style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
                >
                  <div className="flex items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold truncate" style={{ color: "var(--foreground)" }}>
                        {wallet.name}
                      </p>
                      <p className="text-xs opacity-50" style={{ color: "var(--foreground)" }}>
                        {t(("walletKind." + wallet.walletKind) as TranslationKey)} · {wallet.myRole.toLowerCase()}
                      </p>
                    </div>
                    <p className="text-sm font-semibold flex-shrink-0" style={{ color: "var(--primary)" }}>
                      {formatted}
                    </p>
                  </div>
                  <div className="flex justify-end mt-2">
                    <button
                      onClick={() => leaveMutation.mutate(wallet.id)}
                      disabled={leaveMutation.isPending}
                      className="text-xs px-3 py-1.5 rounded-lg font-medium border transition-opacity hover:opacity-70 disabled:opacity-40"
                      style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
                    >
                      {t("sharing.leave")}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* My wallets - manage access */}
      <section>
        <h2 className="text-base font-semibold mb-3" style={{ color: "var(--foreground)" }}>
          {t("sharing.manageAccess")}
        </h2>
        {myWallets.length === 0 ? (
          <p className="text-sm opacity-50" style={{ color: "var(--foreground)" }}>
            {t("sharing.noWallets")}
          </p>
        ) : (
          <div className="space-y-3">
            {myWallets.map((wallet) => {
              const isExpanded = expandedWalletId === wallet.id;
              return (
                <div
                  key={wallet.id}
                  className="rounded-xl border overflow-hidden"
                  style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
                >
                  <button
                    onClick={() => setExpandedWalletId(isExpanded ? null : wallet.id)}
                    className="w-full px-4 py-3 flex items-center gap-3 text-left hover:opacity-80 transition-opacity"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold truncate" style={{ color: "var(--foreground)" }}>
                        {wallet.name}
                      </p>
                      <p className="text-xs opacity-50" style={{ color: "var(--foreground)" }}>
                        {t(("walletKind." + wallet.walletKind) as TranslationKey)}
                      </p>
                    </div>
                    <span
                      className="text-xs opacity-50 flex-shrink-0"
                      style={{ color: "var(--foreground)" }}
                    >
                      {isExpanded ? "▲" : "▼"}
                    </span>
                  </button>

                  {isExpanded && (
                    <div
                      className="px-4 pb-4 border-t pt-4"
                      style={{ borderColor: "var(--border)" }}
                    >
                      <WalletMembersSection walletId={wallet.id} isOwner />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
