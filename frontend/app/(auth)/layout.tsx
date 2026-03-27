"use client";

import { LanguageSwitcher } from "@/components/i18n/LanguageSwitcher";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{ backgroundColor: "var(--background)" }}
    >
      <div className="w-full max-w-md px-4">
        <div className="flex justify-end mb-4"><LanguageSwitcher /></div>
        {children}
      </div>
    </div>
  );
}
