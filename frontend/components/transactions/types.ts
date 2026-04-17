export type TransactionKind = "INCOME" | "EXPENSE";
export type CategoryKind = "INCOME" | "EXPENSE";

export interface Transaction {
  id: string;
  walletId: string;
  amount: number;
  transactionKind: TransactionKind;
  date: string;
  description: string | null;
  categoryId: string | null;
  createdById: string | null;
  createdAt: string;
}

export interface Category {
  id: string;
  name: string;
  nameEs: string | null;
  categoryKind: CategoryKind;
  color: string;
  isGlobal: boolean;
}

