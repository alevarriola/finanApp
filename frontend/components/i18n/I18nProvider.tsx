"use client";

import { createContext, useContext, useCallback } from "react";
import { useStoredChoice } from "@/components/lib/useStoredChoice";
import { type Locale, type TranslationKey, locales } from "./locales";

const LOCALES: readonly Locale[] = ["en", "es"];

interface I18nContextType {
  locale: Locale;
  t: (key: TranslationKey) => string;
  setLocale: (locale: Locale) => void;
}

const I18nContext = createContext<I18nContextType>({
  locale: "en",
  t: (key) => key,
  setLocale: () => {},
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useStoredChoice("locale", LOCALES, "en");

  const t = useCallback(
    (key: TranslationKey): string => {
      return locales[locale][key] ?? key;
    },
    [locale]
  );

  return (
    <I18nContext.Provider value={{ locale, t, setLocale }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
