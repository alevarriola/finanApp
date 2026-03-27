"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showSuccess, showError } from "@/components/lib/toast";
import { WalletCard } from "./WalletCard";
import { WalletFormModal } from "./WalletFormModal";
import { Wallet } from "./types";
import {
  WALLETS_QUERY,
  CREATE_WALLET_MUTATION,
  UPDATE_WALLET_MUTATION,
  ARCHIVE_WALLET_MUTATION,
} from "./walletQueries";
import { useI18n } from "@/components/i18n/I18nProvider";

export default function WalletsContent() {
  const queryClient = useQueryClient();
  const { t } = useI18n();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingWallet, setEditingWallet] = useState<Wallet | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ["wallets"],
    queryFn: () => graphqlRequest<{ wallets: Wallet[] }>(WALLETS_QUERY),
  });

  const createMutation = useMutation({
    mutationFn: (input: Record<string, unknown>) =>
      graphqlRequest(CREATE_WALLET_MUTATION, { input, idempotencyKey: crypto.randomUUID() }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      showSuccess(t("toast.walletCreated"));
      setModalOpen(false);
    },
    onError: showError,
  });

  const updateMutation = useMutation({
    mutationFn: (input: Record<string, unknown>) =>
      graphqlRequest(UPDATE_WALLET_MUTATION, { input }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      showSuccess(t("toast.profileUpdated"));
      setEditingWallet(null);
    },
    onError: showError,
  });

  const archiveMutation = useMutation({
    mutationFn: (walletId: string) =>
      graphqlRequest(ARCHIVE_WALLET_MUTATION, { walletId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      showSuccess(t("wallets.archive"));
    },
    onError: showError,
  });

  async function handleFormSubmit(values: Record<string, unknown>) {
    if (editingWallet) {
      await updateMutation.mutateAsync({ walletId: editingWallet.id, ...values });
    } else {
      await createMutation.mutateAsync(values);
    }
  }

  function openEdit(wallet: Wallet) {
    setEditingWallet(wallet);
  }

  function closeModal() {
    setModalOpen(false);
    setEditingWallet(null);
  }

  const wallets = data?.wallets ?? [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
            {t("wallets.title")}
          </h1>
          <p className="text-sm opacity-50" style={{ color: "var(--foreground)" }}>
            {wallets.length} {t("wallets.count")}
          </p>
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="px-4 py-2 rounded-lg text-sm font-semibold"
          style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
        >
          {t("wallets.create")}
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-lg text-sm text-red-700 bg-red-50 mb-4">
          Failed to load wallets.
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
          ))}
        </div>
      ) : wallets.length === 0 ? (
        <div
          className="rounded-xl border-2 border-dashed p-12 text-center"
          style={{ borderColor: "var(--border)" }}
        >
          <p className="text-lg font-medium mb-4" style={{ color: "var(--foreground)" }}>
            {t("wallets.empty")}
          </p>
          <button
            onClick={() => setModalOpen(true)}
            className="px-4 py-2 rounded-lg text-sm font-semibold"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            {t("wallets.create")}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {wallets.map((wallet) => (
            <WalletCard
              key={wallet.id}
              wallet={wallet}
              onEdit={openEdit}
              onArchive={(w) => archiveMutation.mutate(w.id)}
            />
          ))}
        </div>
      )}

      <WalletFormModal
        open={modalOpen || Boolean(editingWallet)}
        wallet={editingWallet}
        onClose={closeModal}
        onSubmit={handleFormSubmit}
      />
    </div>
  );
}
