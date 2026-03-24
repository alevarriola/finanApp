import { WalletRole } from "@/components/wallets/types";

export type InvitationStatus = "PENDING" | "ACCEPTED" | "REJECTED" | "CANCELLED";

export interface Invitation {
  id: string;
  walletId: string;
  walletName: string;
  invitedByName: string | null;
  invitedEmail: string;
  role: WalletRole;
  status: InvitationStatus;
  createdAt: string;
}
