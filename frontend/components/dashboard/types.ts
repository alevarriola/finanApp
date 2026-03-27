export type ReportPeriod =
  | "THIS_MONTH"
  | "LAST_MONTH"
  | "LAST_3_MONTHS"
  | "LAST_6_MONTHS"
  | "THIS_YEAR";

export interface CategorySpend {
  categoryId: string | null;
  categoryName: string;
  color: string;
  total: number;
}

export interface MonthlyPoint {
  month: string; // "2026-01"
  income: number;
  expense: number;
}

export interface DashboardSummary {
  currency: string;
  totalBalance: number;
  periodIncome: number;
  periodExpense: number;
  topExpenseCategory: string | null;
  topExpenseAmount: number | null;
  expensesByCategory: CategorySpend[];
  monthlyEvolution: MonthlyPoint[];
}

export interface DashboardFilters {
  period: ReportPeriod;
  walletId: string | null;
  categoryId: string | null;
  currency: string | null;
}
