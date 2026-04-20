"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";
import {
  GraphQLClientError,
  graphqlRequest,
} from "@/components/lib/graphql/client";
import { showError, showSuccess } from "@/components/lib/toast";
import { WALLETS_QUERY } from "@/components/wallets/walletQueries";
import type { Wallet } from "@/components/wallets/types";
import { AiTransactionConfirmModal } from "./AiTransactionConfirmModal";
import { AiTransactionPanel } from "./AiTransactionPanel";
import {
  CATEGORIES_QUERY,
  COMPLETE_AI_TRANSACTION_EVENT_MUTATION,
  CREATE_TRANSACTION_MUTATION,
  VALIDATE_TRANSACTION_MUTATION,
} from "./transactionQueries";
import type {
  AiSessionStatus,
  AiTransactionSessionEntry,
  Category,
  TransactionKind,
  ValidatedTransactionPreview,
} from "./types";

interface AiTransactionWorkspaceProps {
  defaultWalletId?: string;
  defaultWalletCurrency?: string;
  showSessionHistory?: boolean;
}

interface ConfirmValues {
  walletId: string;
  amount: number;
  transactionKind: TransactionKind;
  date: string;
  description?: string;
  categoryId?: string;
}

export function AiTransactionWorkspace({
  defaultWalletId,
  defaultWalletCurrency,
  showSessionHistory = false,
}: AiTransactionWorkspaceProps) {
  const queryClient = useQueryClient();
  const { t, locale } = useI18n();
  const [preview, setPreview] = useState<ValidatedTransactionPreview | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [history, setHistory] = useState<AiTransactionSessionEntry[]>([]);

  const { data: walletsData } = useQuery({
    queryKey: ["wallets"],
    queryFn: () => graphqlRequest<{ wallets: Wallet[] }>(WALLETS_QUERY),
    staleTime: 5 * 60_000,
  });

  const { data: categoriesData } = useQuery({
    queryKey: ["categories"],
    queryFn: () => graphqlRequest<{ categories: Category[] }>(CATEGORIES_QUERY),
    staleTime: 5 * 60_000,
  });

  const validateMutation = useMutation({
    mutationFn: (text: string) =>
      graphqlRequest<{ validateTransaction: ValidatedTransactionPreview }>(
        VALIDATE_TRANSACTION_MUTATION,
        { text }
      ),
    onSuccess: () => {
      setFeedbackMessage(null);
    },
    onError: (error) => {
      setPreview(null);
      setConfirmOpen(false);
      if (error instanceof Error && "errorType" in error) {
        setFeedbackMessage(getAiFeedbackMessage(error as GraphQLClientError, t));
        return;
      }
      showError(error);
    },
  });

  const createMutation = useMutation({
    mutationFn: (input: Record<string, unknown>) =>
      graphqlRequest<{ createTransaction: { id: string; walletId: string } }>(
        CREATE_TRANSACTION_MUTATION,
        { input, idempotencyKey: crypto.randomUUID() }
      ),
  });

  const completeEventMutation = useMutation({
    mutationFn: (input: Record<string, unknown>) =>
      graphqlRequest<{ completeAiTransactionEvent: boolean }>(
        COMPLETE_AI_TRANSACTION_EVENT_MUTATION,
        { input }
      ),
  });

  const wallets = walletsData?.wallets ?? [];
  const categories = categoriesData?.categories ?? [];
  const editableWallets = wallets.filter(
    (wallet) => wallet.myRole === "OWNER" || wallet.myRole === "EDITOR"
  );
  const resolvedDefaultWalletId =
    defaultWalletId ?? editableWallets[0]?.id ?? wallets[0]?.id ?? "";
  const resolvedDefaultWalletCurrency =
    defaultWalletCurrency ??
    wallets.find((wallet) => wallet.id === resolvedDefaultWalletId)?.currency ??
    editableWallets[0]?.currency ??
    "PYG";

  async function handleAnalyze(text: string) {
    if (preview) {
      await markPreviewAsCancelled(preview);
    }

    const data = await validateMutation.mutateAsync(text);
    const nextPreview = data.validateTransaction;
    setPreview(nextPreview);
    setHistory((current) => [
      {
        id: crypto.randomUUID(),
        rawText: nextPreview.rawText,
        preview: nextPreview,
        status: "PREVIEWED",
        createdAt: new Date().toISOString(),
      },
      ...current,
    ]);
  }

  async function handleConfirmSubmit(values: ConfirmValues) {
    if (!preview) {
      return;
    }

    const correctedFields = getCorrectedFields(preview, values);
    const transaction = await createMutation.mutateAsync({
      walletId: values.walletId,
      amount: values.amount,
      transactionKind: values.transactionKind,
      date: values.date,
      categoryId: values.categoryId || null,
      description: values.description || null,
    });

    await completeEventSafely(preview, {
      status: correctedFields.length > 0 ? "EDITED" : "CONFIRMED",
      correctedFields,
      transactionId: transaction.createTransaction.id,
      walletId: values.walletId,
      categoryId: values.categoryId || null,
      amount: values.amount,
      currency: preview.currency,
      transactionKind: values.transactionKind,
      description: values.description || null,
      date: values.date,
    });

    updateHistoryStatus(preview.eventId, "SAVED", transaction.createTransaction.id);

    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["transactions", values.walletId] }),
      queryClient.invalidateQueries({ queryKey: ["wallet", values.walletId] }),
      queryClient.invalidateQueries({ queryKey: ["wallets"] }),
      queryClient.invalidateQueries({ queryKey: ["dashboardSummary"] }),
      resolvedDefaultWalletId
        ? queryClient.invalidateQueries({ queryKey: ["wallet", resolvedDefaultWalletId] })
        : Promise.resolve(),
    ]);

    showSuccess(t("toast.transactionAdded"));
    setConfirmOpen(false);
    setPreview(null);
    setFeedbackMessage(null);
  }

  async function handleConfirmClose() {
    if (preview) {
      await markPreviewAsCancelled(preview);
    }
    setConfirmOpen(false);
    setPreview(null);
  }

  async function markPreviewAsCancelled(currentPreview: ValidatedTransactionPreview) {
    await completeEventSafely(currentPreview, {
      status: "CANCELLED",
      correctedFields: [],
      walletId: currentPreview.walletId,
      categoryId: currentPreview.categoryId,
      amount: currentPreview.amount,
      currency: currentPreview.currency,
      transactionKind: currentPreview.transactionKind,
      description: currentPreview.description,
      date: currentPreview.date,
    });
    updateHistoryStatus(currentPreview.eventId, "CANCELLED");
  }

  async function completeEventSafely(
    currentPreview: ValidatedTransactionPreview,
    input: {
      status: "CONFIRMED" | "EDITED" | "CANCELLED";
      correctedFields: string[];
      transactionId?: string;
      walletId?: string | null;
      categoryId?: string | null;
      amount?: number | null;
      currency?: string | null;
      transactionKind?: TransactionKind | null;
      description?: string | null;
      date?: string | null;
    }
  ) {
    if (!currentPreview.eventId) {
      return;
    }

    try {
      await completeEventMutation.mutateAsync({
        eventId: currentPreview.eventId,
        status: input.status,
        correctedFields: input.correctedFields,
        transactionId: input.transactionId ?? null,
        walletId: input.walletId ?? null,
        categoryId: input.categoryId ?? null,
        amount: input.amount ?? null,
        currency: input.currency ?? null,
        transactionKind: input.transactionKind ?? null,
        description: input.description ?? null,
        date: input.date ?? null,
      });
    } catch (error) {
      console.error("Failed to complete AI transaction event", error);
    }
  }

  function updateHistoryStatus(eventId: string | null, status: AiSessionStatus, transactionId?: string) {
    if (!eventId) {
      return;
    }
    setHistory((current) =>
      current.map((entry) =>
        entry.preview.eventId === eventId
          ? { ...entry, status, transactionId }
          : entry
      )
    );
  }

  return (
    <div className="space-y-4">
      <AiTransactionPanel
        walletCurrency={resolvedDefaultWalletCurrency}
        preview={preview}
        isLoading={validateMutation.isPending}
        feedbackMessage={feedbackMessage}
        onAnalyze={handleAnalyze}
        onOpenConfirm={() => setConfirmOpen(true)}
      />

      <AiTransactionConfirmModal
        open={confirmOpen}
        preview={preview}
        wallets={wallets}
        categories={categories}
        fallbackWalletId={resolvedDefaultWalletId}
        onClose={handleConfirmClose}
        onSubmit={handleConfirmSubmit}
      />

      {showSessionHistory && (
        <section
          className="rounded-2xl border p-5 space-y-4"
          style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
        >
          <div>
            <h3 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
              {t("aiChat.historyTitle")}
            </h3>
            <p className="text-sm opacity-70" style={{ color: "var(--foreground)" }}>
              {t("aiChat.historySubtitle")}
            </p>
          </div>

          {history.length === 0 ? (
            <p className="text-sm opacity-70" style={{ color: "var(--foreground)" }}>
              {t("aiChat.historyEmpty")}
            </p>
          ) : (
            <div className="space-y-3">
              {history.map((entry) => (
                <div
                  key={entry.id}
                  className="rounded-xl border p-4 space-y-2"
                  style={{
                    backgroundColor: "var(--background)",
                    borderColor: "var(--border)",
                  }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium" style={{ color: "var(--foreground)" }}>
                        {entry.rawText}
                      </p>
                      <p className="text-xs opacity-60" style={{ color: "var(--foreground)" }}>
                        {new Intl.DateTimeFormat(locale === "es" ? "es-PY" : "en-US", {
                          dateStyle: "short",
                          timeStyle: "short",
                        }).format(new Date(entry.createdAt))}
                      </p>
                    </div>
                    <span
                      className="rounded-full px-2.5 py-1 text-xs font-semibold"
                      style={getStatusStyle(entry.status)}
                    >
                      {t(`aiChat.historyStatus.${entry.status}` as TranslationKey)}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 gap-2 text-sm md:grid-cols-3">
                    <p style={{ color: "var(--foreground)" }}>
                      <span className="opacity-60">{t("aiChat.field.wallet")}:</span>{" "}
                      {entry.preview.walletName ?? "—"}
                    </p>
                    <p style={{ color: "var(--foreground)" }}>
                      <span className="opacity-60">{t("aiChat.field.amount")}:</span>{" "}
                      {formatHistoryAmount(entry.preview, locale)}
                    </p>
                    <p style={{ color: "var(--foreground)" }}>
                      <span className="opacity-60">{t("aiChat.field.category")}:</span>{" "}
                      {entry.preview.categoryName ?? "—"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}

function getCorrectedFields(
  preview: ValidatedTransactionPreview,
  values: ConfirmValues
): string[] {
  const correctedFields: string[] = [];

  if ((preview.walletId ?? "") !== values.walletId) {
    correctedFields.push("wallet");
  }
  if ((preview.categoryId ?? "") !== (values.categoryId ?? "")) {
    correctedFields.push("category");
  }
  if (preview.amount !== values.amount) {
    correctedFields.push("amount");
  }
  if ((preview.date ?? "") !== values.date) {
    correctedFields.push("date");
  }
  if ((preview.description ?? "") !== (values.description ?? "")) {
    correctedFields.push("description");
  }
  if (preview.transactionKind !== values.transactionKind) {
    correctedFields.push("transaction_kind");
  }

  return correctedFields;
}

function getAiFeedbackMessage(
  error: GraphQLClientError,
  t: (key: TranslationKey) => string
): string {
  switch (error.errorType) {
    case "RateLimitError":
      return t("aiChat.feedback.rateLimit");
    case "SuspiciousPromptError":
      return t("aiChat.feedback.suspicious");
    case "AiProviderError":
      return t("aiChat.feedback.provider");
    case "AiInputError":
      return t("aiChat.feedback.input");
    case "FeatureLockedError":
      return t("aiChat.feedback.locked");
    default:
      return t("aiChat.feedback.generic");
  }
}

function formatHistoryAmount(preview: ValidatedTransactionPreview, locale: "en" | "es") {
  if (preview.amount == null || !preview.currency) {
    return "—";
  }

  return new Intl.NumberFormat(locale === "es" ? "es-PY" : "en-US", {
    style: "currency",
    currency: preview.currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(preview.amount);
}

function getStatusStyle(status: AiSessionStatus) {
  switch (status) {
    case "SAVED":
      return {
        backgroundColor: "color-mix(in srgb, #16a34a 14%, transparent)",
        color: "#166534",
      };
    case "CANCELLED":
      return {
        backgroundColor: "color-mix(in srgb, #f59e0b 14%, transparent)",
        color: "#92400e",
      };
    default:
      return {
        backgroundColor: "color-mix(in srgb, var(--primary) 14%, transparent)",
        color: "var(--primary)",
      };
  }
}
