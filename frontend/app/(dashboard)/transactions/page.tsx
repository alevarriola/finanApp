"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showSuccess, showError } from "@/components/lib/toast";
import { WALLETS_QUERY } from "@/components/wallets/walletQueries";
import { CATEGORIES_QUERY, DELETE_TRANSACTION_MUTATION } from "@/components/transactions/transactionQueries";
import type { Transaction, Category, TransactionKind } from "@/components/transactions/types";
import type { Wallet } from "@/components/wallets/types";
import { useI18n } from "@/components/i18n/I18nProvider";

const ALL_TRANSACTIONS_QUERY = `
  query AllTransactions(
    $walletId: UUID,
    $transactionKind: TransactionKind,
    $categoryId: UUID,
    $dateFrom: Date,
    $dateTo: Date
  ) {
    allTransactions(
      walletId: $walletId,
      transactionKind: $transactionKind,
      categoryId: $categoryId,
      dateFrom: $dateFrom,
      dateTo: $dateTo
    ) {
      id walletId walletName walletCurrency amount transactionKind date description categoryId createdAt
    }
  }
`;

type GlobalTransaction = Transaction & { walletName: string | null; walletCurrency: string | null };

function formatCurrency(amount: number, currency = "PYG") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
  }).format(amount);
}

function formatDateLabel(dateStr: string, t: (key: string) => string): string {
  const date = new Date(dateStr + "T00:00:00");
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === today.toDateString()) return t("transactions.today");
  if (date.toDateString() === yesterday.toDateString()) return t("transactions.yesterday");
  return date.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}

export default function TransactionsPage() {
  const { t, locale } = useI18n();
  const queryClient = useQueryClient();
  const [walletId, setWalletId] = useState<string | null>(null);
  const [kind, setKind] = useState<TransactionKind | "">("");
  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data: walletsData } = useQuery({
    queryKey: ["wallets"],
    queryFn: () => graphqlRequest<{ wallets: Wallet[] }>(WALLETS_QUERY),
    staleTime: 60_000,
  });

  const { data: catData } = useQuery({
    queryKey: ["categories"],
    queryFn: () => graphqlRequest<{ categories: Category[] }>(CATEGORIES_QUERY),
    staleTime: 5 * 60_000,
  });

  const { data: txnData, isLoading } = useQuery({
    queryKey: ["allTransactions", walletId, kind, categoryId, dateFrom, dateTo],
    queryFn: () =>
      graphqlRequest<{ allTransactions: GlobalTransaction[] }>(ALL_TRANSACTIONS_QUERY, {
        walletId: walletId || null,
        transactionKind: kind || null,
        categoryId: categoryId || null,
        dateFrom: dateFrom || null,
        dateTo: dateTo || null,
      }),
  });

  const deleteMutation = useMutation({
    mutationFn: (transactionId: string) =>
      graphqlRequest(DELETE_TRANSACTION_MUTATION, { transactionId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["allTransactions"] });
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      showSuccess("Transaction deleted");
    },
    onError: showError,
  });

  const wallets = walletsData?.wallets ?? [];
  const categories = catData?.categories ?? [];
  const transactions = txnData?.allTransactions ?? [];
  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]));

  const grouped = new Map<string, GlobalTransaction[]>();
  for (const txn of transactions) {
    const label = formatDateLabel(txn.date, t as (key: string) => string);
    if (!grouped.has(label)) grouped.set(label, []);
    grouped.get(label)!.push(txn);
  }

  const selectedWallet = wallets.find((w) => w.id === walletId);
  const currency = selectedWallet?.currency ?? wallets[0]?.currency ?? "PYG";

  const selectStyle = {
    backgroundColor: "var(--card)",
    borderColor: "var(--border)",
    color: "var(--foreground)",
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold mb-1" style={{ color: "var(--foreground)" }}>
          {t("transactions.title")}
        </h1>
        <p className="text-sm opacity-60" style={{ color: "var(--foreground)" }}>
          {t("transactions.subtitle")}
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <select
          value={walletId ?? ""}
          onChange={(e) => setWalletId(e.target.value || null)}
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={selectStyle}
        >
          <option value="">{t("transactions.allWallets")}</option>
          {wallets.map((w) => (
            <option key={w.id} value={w.id}>{w.name}</option>
          ))}
        </select>

        <select
          value={kind}
          onChange={(e) => setKind(e.target.value as TransactionKind | "")}
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={selectStyle}
        >
          <option value="">{t("transactions.allTypes")}</option>
          <option value="INCOME">{t("transactions.income")}</option>
          <option value="EXPENSE">{t("transactions.expense")}</option>
        </select>

        <select
          value={categoryId ?? ""}
          onChange={(e) => setCategoryId(e.target.value || null)}
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={selectStyle}
        >
          <option value="">{t("transactions.allCategories")}</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{locale === "es" && c.nameEs ? c.nameEs : c.name}</option>
          ))}
        </select>

        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={selectStyle}
          placeholder="From"
        />
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={selectStyle}
          placeholder="To"
        />

        {(walletId || kind || categoryId || dateFrom || dateTo) && (
          <button
            onClick={() => { setWalletId(null); setKind(""); setCategoryId(null); setDateFrom(""); setDateTo(""); }}
            className="text-xs px-3 py-2 rounded-lg font-medium hover:opacity-70 transition-opacity"
            style={{ color: "var(--primary)" }}
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Transaction list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-14 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
          ))}
        </div>
      ) : transactions.length === 0 ? (
        <div className="rounded-xl border-2 border-dashed p-10 text-center" style={{ borderColor: "var(--border)" }}>
          <p className="text-sm opacity-50" style={{ color: "var(--foreground)" }}>
            {t("transactions.empty")}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {Array.from(grouped.entries()).map(([label, items]) => (
            <div key={label}>
              <p className="text-xs font-semibold uppercase tracking-wide opacity-40 mb-2" style={{ color: "var(--foreground)" }}>
                {label}
              </p>
              <div className="rounded-xl border divide-y overflow-hidden" style={{ borderColor: "var(--border)" }}>
                {items.map((txn) => {
                  const category = txn.categoryId ? categoryMap[txn.categoryId] : null;
                  const isIncome = txn.transactionKind === "INCOME";

                  return (
                    <div
                      key={txn.id}
                      className="flex items-center gap-3 px-4 py-3 hover:opacity-80 transition-opacity"
                      style={{ backgroundColor: "var(--card)" }}
                    >
                      <div
                        className="w-2 h-8 rounded-full flex-shrink-0"
                        style={{ backgroundColor: category?.color ?? (isIncome ? "#16a34a" : "#dc2626") }}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate" style={{ color: "var(--foreground)" }}>
                          {txn.description ?? category?.name ?? (isIncome ? "Income" : "Expense")}
                        </p>
                        <p className="text-xs opacity-50 truncate" style={{ color: "var(--foreground)" }}>
                          {[category?.name, txn.walletName].filter(Boolean).join(" · ")}
                        </p>
                      </div>
                      <span
                        className="text-sm font-semibold tabular-nums"
                        style={{ color: isIncome ? "#16a34a" : "#dc2626" }}
                      >
                        {isIncome ? "+" : "-"}{formatCurrency(txn.amount, txn.walletCurrency ?? "PYG")}
                      </span>
                      <button
                        onClick={() => deleteMutation.mutate(txn.id)}
                        className="text-xs px-2 py-1 rounded opacity-30 hover:opacity-70 transition-opacity"
                        style={{ color: "var(--foreground)" }}
                        title="Delete"
                      >
                        ✕
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
