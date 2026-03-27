"use client";

import { useI18n } from "./I18nProvider";
import type { Locale } from "./locales";

const LANGUAGES: { code: Locale; flag: string; label: string }[] = [
  { code: "en", flag: "🇺🇸", label: "EN" },
  { code: "es", flag: "🇪🇸", label: "ES" },
];

export function LanguageSwitcher() {
  const { locale, setLocale } = useI18n();

  return (
    <div className="flex items-center gap-1">
      {LANGUAGES.map((lang) => (
        <button
          key={lang.code}
          onClick={() => setLocale(lang.code)}
          className="px-2 py-1 rounded text-xs font-medium transition-opacity"
          style={{
            opacity: locale === lang.code ? 1 : 0.4,
            color: "var(--foreground)",
          }}
          title={lang.code === "en" ? "English" : "Español"}
        >
          {lang.flag} {lang.label}
        </button>
      ))}
    </div>
  );
}
