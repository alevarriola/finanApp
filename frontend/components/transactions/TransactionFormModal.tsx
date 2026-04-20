"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useI18n } from "@/components/i18n/I18nProvider";
import { Category } from "./types";

const schema = z.object({
  amount: z.coerce.number().positive("Amount must be positive"),
  transactionKind: z.enum(["INCOME", "EXPENSE"]),
  date: z.string().min(1, "Date is required"),
  description: z.string().max(500).optional(),
  categoryId: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface TransactionFormModalProps {
  open: boolean;
  categories: Category[];
  onClose: () => void;
  onSubmit: (values: FormValues) => Promise<void>;
}

export function TransactionFormModal({
  open,
  categories,
  onClose,
  onSubmit,
}: TransactionFormModalProps) {
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
      transactionKind: "EXPENSE",
      date: today,
      amount: undefined,
    },
  });

  const selectedKind = watch("transactionKind");
  const filteredCategories = categories.filter((c) => c.categoryKind === selectedKind);

  useEffect(() => {
    if (open) reset({ transactionKind: "EXPENSE", date: today, amount: undefined });
  }, [open, reset, today]);

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
          {t("txnForm.title")}
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-2">
            {(["EXPENSE", "INCOME"] as const).map((kind) => (
              <label
                key={kind}
                className="flex items-center justify-center gap-2 py-2 rounded-lg border cursor-pointer text-sm font-medium transition-colors"
                style={{
                  borderColor: selectedKind === kind ? "var(--primary)" : "var(--border)",
                  backgroundColor: selectedKind === kind ? "var(--primary)" : "transparent",
                  color: selectedKind === kind ? "var(--primary-foreground)" : "var(--foreground)",
                }}
              >
                <input
                  {...register("transactionKind")}
                  type="radio"
                  value={kind}
                  className="sr-only"
                />
                <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: kind === "EXPENSE" ? "#dc2626" : "#16a34a" }} />
                {kind === "EXPENSE" ? t("txnForm.expense") : t("txnForm.income")}
              </label>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
              {t("txnForm.amount")}
            </label>
            <input
              {...register("amount")}
              type="number"
              step="any"
              className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
              style={inputStyle}
              placeholder="0"
            />
            {errors.amount && <p className="text-xs mt-1 text-red-600">{errors.amount.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
                {t("txnForm.date")}
              </label>
              <input
                {...register("date")}
                type="date"
                className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                style={inputStyle}
              />
              {errors.date && <p className="text-xs mt-1 text-red-600">{errors.date.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
                {t("txnForm.category")}
              </label>
              <select
                {...register("categoryId")}
                className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
                style={inputStyle}
              >
                <option value="">{t("txnForm.noCategory")}</option>
                {filteredCategories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {locale === "es" && c.nameEs ? c.nameEs : c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1" style={{ color: "var(--foreground)" }}>
              {t("txnForm.description")}
            </label>
            <input
              {...register("description")}
              type="text"
              className="w-full px-3 py-2 rounded-lg border text-sm outline-none"
              style={inputStyle}
              placeholder={t("txnForm.descPlaceholder")}
            />
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
              {isSubmitting ? t("common.loading") : t("txnForm.add")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
