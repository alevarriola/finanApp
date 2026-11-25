"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import { Download, X } from "lucide-react";
import { useI18n } from "@/components/i18n/I18nProvider";

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

const DISMISSED_KEY = "pwa-dismissed";

function isStandalone() {
  return window.matchMedia("(display-mode: standalone)").matches;
}

function wasDismissedThisSession() {
  return sessionStorage.getItem(DISMISSED_KEY) !== null;
}

// These browser facts don't change while the page is open, so there is nothing to subscribe to.
function subscribeNever() {
  return () => {};
}

// iOS Safari has no install prompt, so we show manual instructions instead.
function getIOSHintSnapshot() {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  return isIOS && !isStandalone() && !wasDismissedThisSession();
}

export function InstallBanner() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);
  const isIOSHintEligible = useSyncExternalStore(subscribeNever, getIOSHintSnapshot, () => false);
  const showIOSHint = isIOSHintEligible && !dismissed;

  useEffect(() => {
    if (isStandalone() || wasDismissedThisSession()) return;

    // Android/Chrome: capture the install prompt
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", handler);

    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  function handleInstall() {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then(() => {
        setDeferredPrompt(null);
      });
    }
  }

  function handleDismiss() {
    setDismissed(true);
    setDeferredPrompt(null);
    sessionStorage.setItem(DISMISSED_KEY, "1");
  }

  const { t } = useI18n();

  if (dismissed) return null;
  if (!deferredPrompt && !showIOSHint) return null;

  return (
    <div
      className="fixed bottom-20 md:bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-80 z-50 rounded-xl border p-4 shadow-lg"
      style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
    >
      <button
        onClick={handleDismiss}
        className="absolute top-2 right-2 opacity-40 hover:opacity-70"
        style={{ color: "var(--foreground)" }}
      >
        <X size={16} />
      </button>

      {deferredPrompt ? (
        // Android/Chrome
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            <Download size={20} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
              {t("install.title")}
            </p>
            <p className="text-xs opacity-60" style={{ color: "var(--foreground)" }}>
              {t("install.subtitle")}
            </p>
          </div>
          <button
            onClick={handleInstall}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold flex-shrink-0"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            {t("install.button")}
          </button>
        </div>
      ) : (
        // iOS Safari
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Download size={18} style={{ color: "var(--primary)" }} />
            <p className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
              {t("install.title")}
            </p>
          </div>
          <p className="text-xs leading-relaxed opacity-70" style={{ color: "var(--foreground)" }}>
            {t("install.iosHint")}
          </p>
        </div>
      )}
    </div>
  );
}
