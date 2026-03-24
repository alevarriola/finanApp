"use client";

import { Transaction, Category } from "./types";

interface TransactionListProps {
  transactions: Transaction[];
  categories: Category[];
  currency: string;
  onDelete: (id: string) => void;
}

export function TransactionList({
  transactions,
  categories,
  currency,
  onDelete,
}: TransactionListProps) {
  const categoryMap = Object.fromEntries(categories.map((c) => [c.id, c]));

  if (transactions.length === 0) {
    return (
      <div
        className="rounded-xl border-2 border-dashed p-10 text-center"
        style={{ borderColor: "var(--border)" }}
      >
        <p className="text-sm opacity-50" style={{ color: "var(--foreground)" }}>
          No transactions yet
        </p>
      </div>
    );
  }

  const grouped = groupByDate(transactions);

  return (
    <div className="space-y-4">
      {grouped.map(({ label, items }) => (
        <div key={label}>
          <p className="text-xs font-semibold uppercase tracking-wide opacity-40 mb-2" style={{ color: "var(--foreground)" }}>
            {label}
          </p>
          <div className="rounded-xl border divide-y overflow-hidden" style={{ borderColor: "var(--border)" }}>
            {items.map((txn) => {
              const category = txn.categoryId ? categoryMap[txn.categoryId] : null;
              const isIncome = txn.transactionKind === "INCOME";

              const formatted = new Intl.NumberFormat("es-PY", {
                style: "currency",
                currency,
                minimumFractionDigits: 0,
              }).format(txn.amount);

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
                    {category && txn.description && (
                      <p className="text-xs opacity-50 truncate" style={{ color: "var(--foreground)" }}>
                        {category.name}
                      </p>
                    )}
                  </div>
                  <span
                    className="text-sm font-semibold tabular-nums"
                    style={{ color: isIncome ? "#16a34a" : "#dc2626" }}
                  >
                    {isIncome ? "+" : "-"}{formatted}
                  </span>
                  <button
                    onClick={() => onDelete(txn.id)}
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
  );
}

function groupByDate(transactions: Transaction[]) {
  const map = new Map<string, Transaction[]>();
  for (const txn of transactions) {
    const label = formatDateLabel(txn.date);
    if (!map.has(label)) map.set(label, []);
    map.get(label)!.push(txn);
  }
  return Array.from(map.entries()).map(([label, items]) => ({ label, items }));
}

function formatDateLabel(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00");
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);

  if (date.toDateString() === today.toDateString()) return "Today";
  if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
  return date.toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" });
}
