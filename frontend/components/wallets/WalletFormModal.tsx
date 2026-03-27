"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";
import { Wallet, WalletKind } from "./types";

const schema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  walletKind: z.enum(["CASH", "BANK", "DEBIT", "CREDIT"]),
  currency: z.string().min(1).max(10),
  initialBalance: z.coerce.number().default(0),
});

type FormValues = z.infer<typeof schema>;

interface WalletFormModalProps {
  open: boolean;
  wallet?: Wallet | null;
  onClose: () => void;
  onSubmit: (values: FormValues) => Promise<void>;
}

const CURRENCIES = ["PYG", "USD", "EUR", "BRL", "ARS"];
const WALLET_KINDS: WalletKind[] = ["CASH", "BANK", "DEBIT", "CREDIT"];

export function WalletFormModal({ open, wallet, onClose, onSubmit }: WalletFormModalProps) {
  const { t } = useI18n();
  const isEdit = Boolean(wallet);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      walletKind: "CASH",
      currency: "PYG",
      initialBalance: 0,
    },
  });

  useEffect(() => {
    if (wallet) {
      reset({
        name: wallet.name,
        walletKind: wallet.walletKind,
        currency: wallet.currency,
        initialBalance: wallet.initialBalance,
      });
    } else {
      reset({ name: "", walletKind: "CASH", currency: "PYG", initialBalance: 0 });
    }
  }, [wallet, reset]);

  if (!open) return null;

  const inputStyle = {
    backgroundColor: "var(--background)",
    borderColor: "var(--border)",
    color: "var(--foreground)",
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />
      <div
        className="relative w-full max-w-md rounded-2xl border shadow-xl p-6 z-10"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <h2 className="text-lg font-bold mb-4" style={{ color: "var(--foreground)" }}>
          {isEdit ? t("walletForm.editTitle") : t("walletForm.createTitle")}
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
              {t("walletForm.name")}
            </label>
            <input
              {...register("name")}
              className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
              style={inputStyle}
              placeholder={t("walletForm.namePlaceholder")}
            />
            {errors.name && <p className="text-xs mt-1 text-red-600">{errors.name.message}</p>}
          </div>

          {!isEdit && (
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
                {t("walletForm.type")}
              </label>
              <select
                {...register("walletKind")}
                className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                style={inputStyle}
              >
                {WALLET_KINDS.map((k) => (
                  <option key={k} value={k}>{t(("walletKind." + k) as TranslationKey)}</option>
                ))}
              </select>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
                {t("walletForm.currency")}
              </label>
              <select
                {...register("currency")}
                className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                style={inputStyle}
              >
                {CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            {!isEdit && (
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
                  {t("walletForm.initialBalance")}
                </label>
                <input
                  {...register("initialBalance")}
                  type="number"
                  step="any"
                  className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                  style={inputStyle}
                  placeholder="0"
                />
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded-lg text-sm border"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              {t("common.cancel")}
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 py-2 rounded-lg text-sm font-semibold disabled:opacity-60"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            >
              {isSubmitting ? t("common.loading") : isEdit ? t("walletForm.save") : t("walletForm.create")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
