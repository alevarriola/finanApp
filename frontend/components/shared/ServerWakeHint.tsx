"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { useI18n } from "@/components/i18n/I18nProvider";

// A healthy backend answers well under this delay; only a cold start shows the hint.
const HINT_DELAY_MS = 2500;

export function ServerWakeHint() {
  const { t } = useI18n();
  const [isWaking, setIsWaking] = useState(false);

  useEffect(() => {
    let isActive = true;
    const hintTimer = setTimeout(() => {
      if (isActive) setIsWaking(true);
    }, HINT_DELAY_MS);

    fetch("/api/wake", { cache: "no-store" })
      .catch(() => undefined)
      .finally(() => {
        clearTimeout(hintTimer);
        if (isActive) setIsWaking(false);
      });

    return () => {
      isActive = false;
      clearTimeout(hintTimer);
    };
  }, []);

  if (!isWaking) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-start gap-2 rounded-lg border px-3 py-2 mb-4 text-sm"
      style={{
        backgroundColor: "var(--secondary)",
        borderColor: "var(--border)",
        color: "var(--secondary-foreground)",
      }}
    >
      <Loader2 size={16} className="animate-spin shrink-0 mt-0.5" />
      <span>{t("auth.serverWaking")}</span>
    </div>
  );
}
