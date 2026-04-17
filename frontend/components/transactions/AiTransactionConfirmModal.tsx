"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";
import type { ValidatedTransactionPreview } from "./types";
import type { Wallet } from "../wallets/types";
import type { Category } from "./types";

const schema = z.object({
  walletId: z.string().min(1),
  amount: z.coerce.number().positive(),
  transactionKind: z.enum(["INCOME", "EXPENSE"]),
  date: z.string().min(1),
  description: z.string().max(500).optional(),
  categoryId: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface AiTransactionConfirmModalProps {
  open: boolean;
  preview: ValidatedTransactionPreview | null;
  wallets: Wallet[];
  categories: Category[];
  fallbackWalletId: string;
  onClose: () => void;
  onSubmit: (values: FormValues) => Promise<void>;
}

export function AiTransactionConfirmModal({
  open,
  preview,
  wallets,
  categories,
  fallbackWalletId,
  onClose,
  onSubmit,
}: AiTransactionConfirmModalProps) {
  const { t, locale } = useI18n();
  const today = new Date().toISOString().split("T")[0];
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      walletId: fallbackWalletId,
      transactionKind: "EXPENSE",
      date: today,
      amount: undefined,
      categoryId: "",
      description: "",
    },
  });

  const selectedKind = watch("transactionKind");
  const filteredCategories = categories.filter((category) => category.categoryKind === selectedKind);
  const editableWallets = wallets.filter(
    (wallet) => wallet.myRole === "OWNER" || wallet.myRole === "EDITOR"
  );

  useEffect(() => {
    if (!open) {
      return;
    }
    reset({
      walletId: preview?.walletId ?? fallbackWalletId,
      transactionKind: preview?.transactionKind ?? "EXPENSE",
      date: preview?.date ?? today,
      amount: preview?.amount ?? undefined,
      categoryId: preview?.categoryId ?? "",
      description: preview?.description ?? "",
    });
  }, [fallbackWalletId, open, preview, reset, today]);

  if (!open || !preview) {
    return null;
  }

  const inputStyle = {
    backgroundColor: "var(--background)",
    borderColor: "var(--border)",
    color: "var(--foreground)",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div
        className="relative z-10 w-full max-w-lg rounded-2xl border p-6 shadow-xl"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <div className="mb-4 space-y-1">
          <h2 className="text-lg font-bold" style={{ color: "var(--foreground)" }}>
            {t("aiChat.confirmTitle")}
          </h2>
          <p className="text-sm opacity-70" style={{ color: "var(--foreground)" }}>
            {t("aiChat.confirmSubtitle")}
          </p>
        </div>

        <div
          className="mb-4 rounded-xl border p-3"
          style={{ backgroundColor: "var(--background)", borderColor: "var(--border)" }}
        >
          <p className="text-xs uppercase tracking-wide opacity-60" style={{ color: "var(--foreground)" }}>
            {t("aiChat.originalText")}
          </p>
          <p className="mt-1 text-sm" style={{ color: "var(--foreground)" }}>
            {preview.rawText}
          </p>
          {preview.unresolvedFields.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {preview.unresolvedFields.map((field) => (
                <span
                  key={field}
                  className="rounded-full border px-2.5 py-1 text-xs font-medium"
                  style={{
                    borderColor: "color-mix(in srgb, #b45309 35%, var(--border))",
                    backgroundColor: "color-mix(in srgb, #f59e0b 12%, transparent)",
                    color: "var(--foreground)",
                  }}
                >
                  {t(`aiChat.unresolved.${field}` as TranslationKey)}
                </span>
              ))}
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium" style={{ color: "var(--foreground)" }}>
              {t("aiChat.field.wallet")}
            </label>
            <select
              {...register("walletId")}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={inputStyle}
            >
              {editableWallets.map((wallet) => (
                <option key={wallet.id} value={wallet.id}>
                  {wallet.name}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {(["EXPENSE", "INCOME"] as const).map((kind) => (
              <label
                key={kind}
                className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border py-2 text-sm font-medium transition-colors"
                style={{
                  borderColor: selectedKind === kind ? "var(--primary)" : "var(--border)",
                  backgroundColor: selectedKind === kind ? "var(--primary)" : "transparent",
                  color:
                    selectedKind === kind ? "var(--primary-foreground)" : "var(--foreground)",
                }}
              >
                <input
                  {...register("transactionKind")}
                  type="radio"
                  value={kind}
                  className="sr-only"
                />
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{ backgroundColor: kind === "EXPENSE" ? "#dc2626" : "#16a34a" }}
                />
                {kind === "EXPENSE" ? t("txnForm.expense") : t("txnForm.income")}
              </label>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium" style={{ color: "var(--foreground)" }}>
                {t("txnForm.amount")}
              </label>
              <input
                {...register("amount")}
                type="number"
                step="any"
                className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
                style={inputStyle}
                placeholder="0"
              />
              {errors.amount && (
                <p className="mt-1 text-xs text-red-600">{t("aiChat.validationAmount")}</p>
              )}
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium" style={{ color: "var(--foreground)" }}>
                {t("txnForm.date")}
              </label>
              <input
                {...register("date")}
                type="date"
                className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
                style={inputStyle}
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium" style={{ color: "var(--foreground)" }}>
              {t("txnForm.category")}
            </label>
            <select
              {...register("categoryId")}
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={inputStyle}
            >
              <option value="">{t("txnForm.noCategory")}</option>
              {filteredCategories.map((category) => (
                <option key={category.id} value={category.id}>
                  {locale === "es" && category.nameEs ? category.nameEs : category.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium" style={{ color: "var(--foreground)" }}>
              {t("txnForm.description")}
            </label>
            <input
              {...register("description")}
              type="text"
              className="w-full rounded-lg border px-3 py-2 text-sm outline-none"
              style={inputStyle}
              placeholder={t("txnForm.descPlaceholder")}
            />
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-lg border py-2 text-sm"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              {t("common.cancel")}
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 rounded-lg py-2 text-sm font-semibold disabled:opacity-60"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            >
              {isSubmitting ? t("common.loading") : t("aiChat.confirmSave")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
