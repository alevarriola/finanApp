"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { Sparkles } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useI18n } from "@/components/i18n/I18nProvider";
import type { TranslationKey } from "@/components/i18n/locales";
import type { ValidatedTransactionPreview } from "./types";

const schema = z.object({
  text: z.string().trim().min(1).max(400),
});

type FormValues = z.infer<typeof schema>;

interface AiTransactionPanelProps {
  walletCurrency: string;
  preview: ValidatedTransactionPreview | null;
  isLoading: boolean;
  onAnalyze: (text: string) => Promise<void>;
  onOpenConfirm: () => void;
}

export function AiTransactionPanel({
  walletCurrency,
  preview,
  isLoading,
  onAnalyze,
  onOpenConfirm,
}: AiTransactionPanelProps) {
  const { t, locale } = useI18n();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      text: "",
    },
  });

  useEffect(() => {
    if (!preview) {
      return;
    }
    reset({ text: preview.rawText });
  }, [preview, reset]);

  const inputStyle = {
    backgroundColor: "var(--background)",
    borderColor: "var(--border)",
    color: "var(--foreground)",
  };

  async function submit(values: FormValues) {
    await onAnalyze(values.text);
  }

  const effectiveCurrency = preview?.currency ?? walletCurrency;
  const amount =
    preview?.amount == null
      ? "—"
      : new Intl.NumberFormat(locale === "es" ? "es-PY" : "en-US", {
          style: "currency",
          currency: effectiveCurrency,
          minimumFractionDigits: 0,
          maximumFractionDigits: 2,
        }).format(preview.amount);

  return (
    <section
      className="rounded-2xl border p-5 space-y-4"
      style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ backgroundColor: "color-mix(in srgb, var(--primary) 14%, transparent)" }}
        >
          <Sparkles size={18} style={{ color: "var(--primary)" }} />
        </div>
        <div className="space-y-1">
          <h3 className="text-base font-semibold" style={{ color: "var(--foreground)" }}>
            {t("aiChat.title")}
          </h3>
          <p className="text-sm opacity-70" style={{ color: "var(--foreground)" }}>
            {t("aiChat.subtitle")}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit(submit)} className="space-y-3">
        <div>
          <textarea
            {...register("text")}
            rows={4}
            className="w-full resize-none rounded-xl border px-3 py-3 text-sm outline-none"
            style={inputStyle}
            placeholder={t("aiChat.placeholder")}
          />
          {errors.text && (
            <p className="mt-1 text-xs text-red-600">{t("aiChat.validation")}</p>
          )}
        </div>

        <div className="flex items-center justify-between gap-3">
          <p className="text-xs opacity-70" style={{ color: "var(--foreground)" }}>
            {t("aiChat.previewOnly")}
          </p>
          <button
            type="submit"
            disabled={isLoading}
            className="rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-60"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            {isLoading ? t("common.loading") : t("aiChat.analyze")}
          </button>
        </div>
      </form>

      {preview && (
        <div
          className="rounded-2xl border p-4 space-y-4"
          style={{ backgroundColor: "var(--background)", borderColor: "var(--border)" }}
        >
          <div className="flex items-center justify-between gap-3">
            <div>
              <h4 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
                {t("aiChat.previewTitle")}
              </h4>
              <p className="text-xs opacity-70" style={{ color: "var(--foreground)" }}>
                {preview.rawText}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs opacity-60" style={{ color: "var(--foreground)" }}>
                {t("aiChat.confidence")}
              </p>
              <p className="text-sm font-semibold" style={{ color: "var(--primary)" }}>
                {Math.round(preview.confidence * 100)}%
              </p>
            </div>
          </div>

          <dl className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {[
              ["aiChat.field.wallet", preview.walletName ?? "—"],
              [
                "aiChat.field.kind",
                preview.transactionKind
                  ? t(
                      preview.transactionKind === "EXPENSE"
                        ? "transactions.expense"
                        : "transactions.income"
                    )
                  : "—",
              ],
              ["aiChat.field.amount", amount],
              ["aiChat.field.category", preview.categoryName ?? "—"],
              [
                "aiChat.field.date",
                preview.date
                  ? new Intl.DateTimeFormat(locale === "es" ? "es-PY" : "en-US").format(
                      new Date(preview.date)
                    )
                  : "—",
              ],
              ["aiChat.field.description", preview.description ?? "—"],
            ].map(([labelKey, value]) => (
              <div key={labelKey as string} className="space-y-1">
                <dt className="text-xs uppercase tracking-wide opacity-60" style={{ color: "var(--foreground)" }}>
                  {t(labelKey as TranslationKey)}
                </dt>
                <dd className="text-sm font-medium" style={{ color: "var(--foreground)" }}>
                  {value}
                </dd>
              </div>
            ))}
          </dl>

          {preview.unresolvedFields.length > 0 ? (
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-wide opacity-60" style={{ color: "var(--foreground)" }}>
                {t("aiChat.needsReview")}
              </p>
              <div className="flex flex-wrap gap-2">
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
            </div>
          ) : (
            <p className="text-sm font-medium" style={{ color: "var(--primary)" }}>
              {t("aiChat.ready")}
            </p>
          )}

          <div className="flex justify-end">
            <button
              type="button"
              onClick={onOpenConfirm}
              className="rounded-lg px-4 py-2 text-sm font-semibold"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            >
              {t("aiChat.reviewAndSave")}
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
