"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { WALLETS_QUERY } from "@/components/wallets/walletQueries";
import { CATEGORIES_QUERY } from "@/components/transactions/transactionQueries";
import { DASHBOARD_SUMMARY_QUERY, AVAILABLE_CURRENCIES_QUERY } from "@/components/dashboard/reportQueries";
import type { DashboardFilters, DashboardSummary, ReportPeriod } from "@/components/dashboard/types";
import type { Wallet } from "@/components/wallets/types";
import type { Category } from "@/components/transactions/types";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";

const PERIOD_LABEL_KEYS: Record<ReportPeriod, TranslationKey> = {
  THIS_MONTH: "dashboard.thisMonth",
  LAST_MONTH: "dashboard.lastMonth",
  LAST_3_MONTHS: "dashboard.last3Months",
  LAST_6_MONTHS: "dashboard.last6Months",
  THIS_YEAR: "dashboard.thisYear",
};

const MONTH_LABELS: Record<string, string> = {
  "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
  "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
  "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
};

function formatCurrency(amount: number, currency = "PYG") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div
      className="rounded-xl border p-4"
      style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
    >
      <p className="text-xs opacity-50 mb-1" style={{ color: "var(--foreground)" }}>
        {label}
      </p>
      <p
        className="text-xl font-bold"
        style={{ color: color ?? "var(--foreground)" }}
      >
        {value}
      </p>
    </div>
  );
}

export default function DashboardPage() {
  const { t, locale } = useI18n();
  const [filters, setFilters] = useState<DashboardFilters>({
    period: "THIS_MONTH",
    walletId: null,
    categoryId: null,
    currency: null,
  });

  const { data: currenciesData } = useQuery({
    queryKey: ["availableCurrencies"],
    queryFn: () => graphqlRequest<{ availableCurrencies: string[] }>(AVAILABLE_CURRENCIES_QUERY),
    staleTime: 60_000,
  });

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

  const { data: summaryData, isLoading } = useQuery({
    queryKey: ["dashboardSummary", filters],
    queryFn: () =>
      graphqlRequest<{ dashboardSummary: DashboardSummary }>(
        DASHBOARD_SUMMARY_QUERY,
        {
          filters: {
            period: filters.period,
            walletId: filters.walletId ?? null,
            categoryId: filters.categoryId ?? null,
            currency: filters.currency ?? null,
          },
        }
      ),
  });

  const currencies = currenciesData?.availableCurrencies ?? [];
  const wallets = walletsData?.wallets ?? [];
  const categories = catData?.categories ?? [];
  const summary = summaryData?.dashboardSummary;

  const activeCurrency = summary?.currency ?? filters.currency ?? currencies[0] ?? "PYG";

  const net = (summary?.periodIncome ?? 0) - (summary?.periodExpense ?? 0);

  const incomeLabel = t("chart.income");
  const expenseLabel = t("chart.expense");

  const monthlyChartData = (summary?.monthlyEvolution ?? []).map((p) => {
    const [year, month] = p.month.split("-");
    return {
      name: `${MONTH_LABELS[month]} ${year}`,
      [incomeLabel]: Number(p.income),
      [expenseLabel]: Number(p.expense),
    };
  });

  const pieData = (summary?.expensesByCategory ?? []).map((c) => ({
    name: locale === "es" && c.categoryNameEs ? c.categoryNameEs : c.categoryName,
    value: Number(c.total),
    color: c.color,
  }));

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-1" style={{ color: "var(--foreground)" }}>
          {t("dashboard.title")}
        </h1>
        <p className="text-sm opacity-60" style={{ color: "var(--foreground)" }}>
          {t("dashboard.subtitle")}
        </p>
      </div>

      {/* Currency tabs */}
      {currencies.length > 1 && (
        <div className="flex gap-2">
          {currencies.map((c) => (
            <button
              key={c}
              onClick={() => setFilters((f) => ({ ...f, currency: c, walletId: null }))}
              className="px-4 py-1.5 rounded-lg text-sm font-medium transition-opacity"
              style={{
                backgroundColor: (filters.currency ?? currencies[0]) === c ? "var(--primary)" : "var(--card)",
                color: (filters.currency ?? currencies[0]) === c ? "var(--primary-foreground)" : "var(--foreground)",
                borderWidth: 1,
                borderColor: "var(--border)",
              }}
            >
              {c}
            </button>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {/* Period */}
        <select
          value={filters.period}
          onChange={(e) => setFilters((f) => ({ ...f, period: e.target.value as ReportPeriod }))}
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
            color: "var(--foreground)",
          }}
        >
          {(Object.keys(PERIOD_LABEL_KEYS) as ReportPeriod[]).map((p) => (
            <option key={p} value={p}>
              {t(PERIOD_LABEL_KEYS[p])}
            </option>
          ))}
        </select>

        {/* Wallet */}
        <select
          value={filters.walletId ?? ""}
          onChange={(e) =>
            setFilters((f) => ({ ...f, walletId: e.target.value || null }))
          }
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
            color: "var(--foreground)",
          }}
        >
          <option value="">{t("dashboard.allWallets")}</option>
          {wallets.map((w) => (
            <option key={w.id} value={w.id}>
              {w.name}
            </option>
          ))}
        </select>

        {/* Category */}
        <select
          value={filters.categoryId ?? ""}
          onChange={(e) =>
            setFilters((f) => ({ ...f, categoryId: e.target.value || null }))
          }
          className="text-sm rounded-lg border px-3 py-2 outline-none"
          style={{
            backgroundColor: "var(--card)",
            borderColor: "var(--border)",
            color: "var(--foreground)",
          }}
        >
          <option value="">{t("dashboard.allCategories")}</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {/* Stat cards */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-20 rounded-xl animate-pulse"
              style={{ backgroundColor: "var(--muted)" }}
            />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard
            label={t("dashboard.totalBalance")}
            value={formatCurrency(summary?.totalBalance ?? 0, activeCurrency)}
            color="var(--primary)"
          />
          <StatCard
            label={t("dashboard.income")}
            value={formatCurrency(summary?.periodIncome ?? 0, activeCurrency)}
            color="#16a34a"
          />
          <StatCard
            label={t("dashboard.expenses")}
            value={formatCurrency(summary?.periodExpense ?? 0, activeCurrency)}
            color="#dc2626"
          />
          <StatCard
            label={t("dashboard.net")}
            value={formatCurrency(net, activeCurrency)}
            color={net >= 0 ? "#16a34a" : "#dc2626"}
          />
        </div>
      )}

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Expenses by category - Pie */}
        <div
          className="rounded-xl border p-5"
          style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
        >
          <h2 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>
            {t("dashboard.expensesByCategory")}
          </h2>
          {isLoading ? (
            <div className="h-48 rounded animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
          ) : pieData.length === 0 ? (
            <div className="h-48 flex items-center justify-center">
              <p className="text-sm opacity-40" style={{ color: "var(--foreground)" }}>
                {t("dashboard.noExpenses")}
              </p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {pieData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => formatCurrency(value, activeCurrency)}
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Legend
                  iconType="circle"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "12px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Monthly evolution - Area */}
        <div
          className="rounded-xl border p-5"
          style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
        >
          <h2 className="text-sm font-semibold mb-4" style={{ color: "var(--foreground)" }}>
            {t("dashboard.monthlyEvolution")}
          </h2>
          {isLoading ? (
            <div className="h-48 rounded animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={monthlyChartData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#16a34a" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorExpense" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#dc2626" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#dc2626" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 11, fill: "var(--foreground)", opacity: 0.6 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "var(--foreground)", opacity: 0.6 }}
                  axisLine={false}
                  tickLine={false}
                  width={40}
                  tickFormatter={(v) =>
                    v >= 1_000_000
                      ? `${(v / 1_000_000).toFixed(1)}M`
                      : v >= 1_000
                      ? `${(v / 1_000).toFixed(0)}K`
                      : String(v)
                  }
                />
                <Tooltip
                  formatter={(value: number) => formatCurrency(value, activeCurrency)}
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: "12px" }} />
                <Area
                  type="monotone"
                  dataKey={incomeLabel}
                  stroke="#16a34a"
                  strokeWidth={2}
                  fill="url(#colorIncome)"
                  dot={false}
                />
                <Area
                  type="monotone"
                  dataKey={expenseLabel}
                  stroke="#dc2626"
                  strokeWidth={2}
                  fill="url(#colorExpense)"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Top expense category */}
      {summary?.topExpenseCategory && (
        <div
          className="rounded-xl border px-5 py-4 flex items-center gap-4"
          style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
        >
          <div>
            <p className="text-xs opacity-50 mb-0.5" style={{ color: "var(--foreground)" }}>
              {t("dashboard.topCategory")}
            </p>
            <p className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
              {summary.topExpenseCategory}
            </p>
          </div>
          <p className="ml-auto text-sm font-bold" style={{ color: "#dc2626" }}>
            {formatCurrency(summary.topExpenseAmount ?? 0, activeCurrency)}
          </p>
        </div>
      )}
    </div>
  );
}
