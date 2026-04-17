export type TransactionKind = "INCOME" | "EXPENSE";
export type CategoryKind = "INCOME" | "EXPENSE";
export type ValidationStatus = "PARSED" | "VALIDATED";

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

export interface ValidatedTransactionPreview {
  eventId: string | null;
  rawText: string;
  walletId: string | null;
  walletName: string | null;
  categoryId: string | null;
  categoryName: string | null;
  amount: number | null;
  currency: string | null;
  transactionKind: TransactionKind | null;
  description: string | null;
  date: string | null;
  confidence: number;
  requiresConfirmation: boolean;
  unresolvedFields: string[];
  validationStatus: ValidationStatus;
}

export type AiSessionStatus = "PREVIEWED" | "SAVED" | "CANCELLED";

export interface AiTransactionSessionEntry {
  id: string;
  rawText: string;
  preview: ValidatedTransactionPreview;
  status: AiSessionStatus;
  createdAt: string;
  transactionId?: string;
}
