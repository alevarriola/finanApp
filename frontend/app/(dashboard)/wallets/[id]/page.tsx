"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showSuccess, showError } from "@/components/lib/toast";
import { AiTransactionConfirmModal } from "@/components/transactions/AiTransactionConfirmModal";
import { AiTransactionPanel } from "@/components/transactions/AiTransactionPanel";
import { TransactionFormModal } from "@/components/transactions/TransactionFormModal";
import { TransactionList } from "@/components/transactions/TransactionList";
import {
  Transaction,
  Category,
  ValidatedTransactionPreview,
} from "@/components/transactions/types";
import { Wallet } from "@/components/wallets/types";
import { WALLETS_QUERY } from "@/components/wallets/walletQueries";
import {
  TRANSACTIONS_QUERY,
  CATEGORIES_QUERY,
  CREATE_TRANSACTION_MUTATION,
  DELETE_TRANSACTION_MUTATION,
  VALIDATE_TRANSACTION_MUTATION,
} from "@/components/transactions/transactionQueries";
import { useI18n } from "@/components/i18n/I18nProvider";

const WALLET_QUERY = `
  query GetWallet($walletId: UUID!) {
    wallet(walletId: $walletId) {
      id name walletKind currency initialBalance currentBalance isArchived myRole createdAt
    }
  }
`;

export default function WalletDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { t } = useI18n();
  const walletId = params.id as string;
  const [modalOpen, setModalOpen] = useState(false);
  const [aiConfirmOpen, setAiConfirmOpen] = useState(false);
  const [aiPreview, setAiPreview] = useState<ValidatedTransactionPreview | null>(null);

  const { data: walletData, isLoading: walletLoading } = useQuery({
    queryKey: ["wallet", walletId],
    queryFn: () => graphqlRequest<{ wallet: Wallet }>(WALLET_QUERY, { walletId }),
  });

  const { data: txnData, isLoading: txnLoading } = useQuery({
    queryKey: ["transactions", walletId],
    queryFn: () =>
      graphqlRequest<{ transactions: Transaction[] }>(TRANSACTIONS_QUERY, { walletId }),
  });

  const { data: catData } = useQuery({
    queryKey: ["categories"],
    queryFn: () => graphqlRequest<{ categories: Category[] }>(CATEGORIES_QUERY),
    staleTime: 5 * 60 * 1000,
  });

  const { data: walletsData } = useQuery({
    queryKey: ["wallets"],
    queryFn: () => graphqlRequest<{ wallets: Wallet[] }>(WALLETS_QUERY),
    staleTime: 5 * 60 * 1000,
  });

  const createMutation = useMutation({
    mutationFn: (input: Record<string, unknown>) =>
      graphqlRequest(CREATE_TRANSACTION_MUTATION, { input, idempotencyKey: crypto.randomUUID() }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions", walletId] });
      queryClient.invalidateQueries({ queryKey: ["wallet", walletId] });
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      queryClient.invalidateQueries({ queryKey: ["dashboardSummary"] });
      showSuccess(t("toast.transactionAdded"));
      setModalOpen(false);
      setAiConfirmOpen(false);
      setAiPreview(null);
    },
    onError: showError,
  });

  const deleteMutation = useMutation({
    mutationFn: (transactionId: string) =>
      graphqlRequest(DELETE_TRANSACTION_MUTATION, { transactionId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions", walletId] });
      queryClient.invalidateQueries({ queryKey: ["wallet", walletId] });
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      showSuccess(t("toast.transactionDeleted"));
    },
    onError: showError,
  });

  const validateMutation = useMutation({
    mutationFn: (text: string) =>
      graphqlRequest<{ validateTransaction: ValidatedTransactionPreview }>(
        VALIDATE_TRANSACTION_MUTATION,
        { text }
      ),
    onError: (error) => {
      setAiPreview(null);
      showError(error);
    },
  });

  const wallet = walletData?.wallet;
  const wallets = walletsData?.wallets ?? [];
  const transactions = txnData?.transactions ?? [];
  const categories = catData?.categories ?? [];

  const canEdit = wallet?.myRole === "OWNER" || wallet?.myRole === "EDITOR";

  async function handleFormSubmit(values: Record<string, unknown>) {
    await createMutation.mutateAsync({
      walletId,
      amount: values.amount,
      transactionKind: values.transactionKind,
      date: values.date,
      categoryId: values.categoryId || null,
      description: values.description || null,
    });
  }

  async function handleAiAnalyze(text: string) {
    const data = await validateMutation.mutateAsync(text);
    setAiPreview(data.validateTransaction);
  }

  async function handleAiConfirmSubmit(values: Record<string, unknown>) {
    await createMutation.mutateAsync({
      walletId: values.walletId,
      amount: values.amount,
      transactionKind: values.transactionKind,
      date: values.date,
      categoryId: values.categoryId || null,
      description: values.description || null,
    });
  }

  if (walletLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 rounded animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
        <div className="h-24 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
      </div>
    );
  }

  if (!wallet) {
    return (
      <div className="text-center py-12">
        <p style={{ color: "var(--foreground)" }}>{t("wallets.notFound")}</p>
        <button onClick={() => router.push("/wallets")} className="mt-4 text-sm underline" style={{ color: "var(--primary)" }}>
          {t("wallets.backToWallets")}
        </button>
      </div>
    );
  }

  const formattedBalance = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: wallet.currency,
    minimumFractionDigits: 0,
  }).format(wallet.currentBalance);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push("/wallets")}
          className="text-sm opacity-50 hover:opacity-80 transition-opacity"
          style={{ color: "var(--foreground)" }}
        >
          ← {t("wallets.backToWallets")}
        </button>
      </div>

      <div
        className="rounded-xl border p-6"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-bold" style={{ color: "var(--foreground)" }}>
              {wallet.name}
            </h1>
            <p className="text-sm opacity-50 mt-0.5" style={{ color: "var(--foreground)" }}>
              {wallet.currency}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs opacity-50 mb-0.5" style={{ color: "var(--foreground)" }}>
              {t("wallets.balance")}
            </p>
            <p className="text-2xl font-bold" style={{ color: "var(--primary)" }}>
              {formattedBalance}
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
          {t("wallets.transactions")}
        </h2>
        {canEdit && (
          <button
            onClick={() => setModalOpen(true)}
            className="px-4 py-2 rounded-lg text-sm font-semibold"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            {t("transactions.add")}
          </button>
        )}
      </div>

      {canEdit && (
        <AiTransactionPanel
          walletCurrency={wallet.currency}
          preview={aiPreview}
          isLoading={validateMutation.isPending}
          onAnalyze={handleAiAnalyze}
          onOpenConfirm={() => setAiConfirmOpen(true)}
        />
      )}

      {txnLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-14 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
          ))}
        </div>
      ) : (
        <TransactionList
          transactions={transactions}
          categories={categories}
          currency={wallet.currency}
          onDelete={(id) => deleteMutation.mutate(id)}
        />
      )}

      <TransactionFormModal
        open={modalOpen}
        categories={categories}
        onClose={() => setModalOpen(false)}
        onSubmit={handleFormSubmit}
      />

      <AiTransactionConfirmModal
        open={aiConfirmOpen}
        preview={aiPreview}
        wallets={wallets}
        categories={categories}
        fallbackWalletId={wallet.id}
        onClose={() => setAiConfirmOpen(false)}
        onSubmit={handleAiConfirmSubmit}
      />

    </div>
  );
}
