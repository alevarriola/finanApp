"use client";

import { Sparkles } from "lucide-react";
import { useI18n } from "@/components/i18n/I18nProvider";
import { AiTransactionWorkspace } from "@/components/transactions/AiTransactionWorkspace";

export default function ChatPage() {
  const { t } = useI18n();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <section
        className="rounded-3xl border p-6 md:p-8"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <div className="flex items-start gap-4">
          <div
            className="flex h-12 w-12 items-center justify-center rounded-2xl"
            style={{ backgroundColor: "color-mix(in srgb, var(--primary) 14%, transparent)" }}
          >
            <Sparkles size={20} style={{ color: "var(--primary)" }} />
          </div>
          <div className="space-y-1">
            <h1 className="text-2xl font-bold" style={{ color: "var(--foreground)" }}>
              {t("aiChat.pageTitle")}
            </h1>
            <p className="text-sm opacity-70" style={{ color: "var(--foreground)" }}>
              {t("aiChat.pageSubtitle")}
            </p>
          </div>
        </div>
      </section>

      <AiTransactionWorkspace showSessionHistory />
    </div>
  );
}
