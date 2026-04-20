export type WalletKind = "CASH" | "BANK" | "DEBIT" | "CREDIT";
export type WalletRole = "OWNER" | "EDITOR" | "VIEWER";

export interface Wallet {
  id: string;
  name: string;
  walletKind: WalletKind;
  currency: string;
  initialBalance: number;
  currentBalance: number;
  isArchived: boolean;
  myRole: WalletRole;
  createdAt: string;
}


