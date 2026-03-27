"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showSuccess, showError } from "@/components/lib/toast";
import { useI18n } from "@/components/i18n/I18nProvider";

const ME_QUERY = `query { me { id email name createdAt } }`;

const UPDATE_PROFILE_MUTATION = `
  mutation UpdateProfile($name: String!) {
    updateProfile(name: $name) { id name email }
  }
`;

const CHANGE_PASSWORD_MUTATION = `
  mutation ChangePassword($currentPassword: String!, $newPassword: String!) {
    changePassword(currentPassword: $currentPassword, newPassword: $newPassword)
  }
`;

interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}

function useTheme() {
  const [theme, setThemeState] = useState<"light" | "dark">("light");

  useEffect(() => {
    const stored = localStorage.getItem("theme") as "light" | "dark" | null;
    const initial = stored ?? "light";
    setThemeState(initial);
    document.documentElement.setAttribute("data-theme", initial);
  }, []);

  function setTheme(t: "light" | "dark") {
    setThemeState(t);
    localStorage.setItem("theme", t);
    document.documentElement.setAttribute("data-theme", t);
  }

  return { theme, setTheme };
}

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { t, locale } = useI18n();
  const { theme, setTheme } = useTheme();

  const { data: meData, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: () => graphqlRequest<{ me: User }>(ME_QUERY),
  });

  const [name, setName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  useEffect(() => {
    if (meData?.me) setName(meData.me.name);
  }, [meData]);

  const profileMutation = useMutation({
    mutationFn: (newName: string) =>
      graphqlRequest(UPDATE_PROFILE_MUTATION, { name: newName }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
      showSuccess(t("toast.profileUpdated"));
    },
    onError: showError,
  });

  const passwordMutation = useMutation({
    mutationFn: (vars: { currentPassword: string; newPassword: string }) =>
      graphqlRequest(CHANGE_PASSWORD_MUTATION, vars),
    onSuccess: () => {
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      showSuccess(t("toast.passwordChanged"));
    },
    onError: showError,
  });

  function handleProfileSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    profileMutation.mutate(name.trim());
  }

  function handlePasswordSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      showError("Passwords do not match");
      return;
    }
    if (newPassword.length < 6) {
      showError("Password must be at least 6 characters");
      return;
    }
    passwordMutation.mutate({ currentPassword, newPassword });
  }

  const user = meData?.me;

  const inputStyle = {
    backgroundColor: "var(--input)",
    borderColor: "var(--border)",
    color: "var(--foreground)",
  };

  if (isLoading) {
    return (
      <div className="max-w-xl mx-auto space-y-6">
        <div className="h-8 w-40 rounded animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
        ))}
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1" style={{ color: "var(--foreground)" }}>
          {t("settings.title")}
        </h1>
        <p className="text-sm opacity-60" style={{ color: "var(--foreground)" }}>
          {t("settings.subtitle")}
        </p>
      </div>

      {/* Profile */}
      <div
        className="rounded-xl border p-5 space-y-4"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <h2 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
          {t("settings.profile")}
        </h2>
        <form onSubmit={handleProfileSubmit} className="space-y-3">
          <div>
            <label className="text-xs opacity-50 mb-1 block" style={{ color: "var(--foreground)" }}>
              {t("settings.email")}
            </label>
            <input
              type="email"
              value={user?.email ?? ""}
              disabled
              className="w-full text-sm rounded-lg border px-3 py-2 opacity-50"
              style={inputStyle}
            />
          </div>
          <div>
            <label className="text-xs opacity-50 mb-1 block" style={{ color: "var(--foreground)" }}>
              {t("settings.name")}
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full text-sm rounded-lg border px-3 py-2 outline-none focus:ring-1"
              style={inputStyle}
            />
          </div>
          <button
            type="submit"
            disabled={profileMutation.isPending || name.trim() === user?.name}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-opacity hover:opacity-80 disabled:opacity-40"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            {t("settings.updateProfile")}
          </button>
        </form>
      </div>

      {/* Change password */}
      <div
        className="rounded-xl border p-5 space-y-4"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <h2 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
          {t("settings.changePassword")}
        </h2>
        <form onSubmit={handlePasswordSubmit} className="space-y-3">
          <div>
            <label className="text-xs opacity-50 mb-1 block" style={{ color: "var(--foreground)" }}>
              {t("settings.currentPassword")}
            </label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full text-sm rounded-lg border px-3 py-2 outline-none focus:ring-1"
              style={inputStyle}
            />
          </div>
          <div>
            <label className="text-xs opacity-50 mb-1 block" style={{ color: "var(--foreground)" }}>
              {t("settings.newPassword")}
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full text-sm rounded-lg border px-3 py-2 outline-none focus:ring-1"
              style={inputStyle}
            />
          </div>
          <div>
            <label className="text-xs opacity-50 mb-1 block" style={{ color: "var(--foreground)" }}>
              {t("settings.newPassword")}
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full text-sm rounded-lg border px-3 py-2 outline-none focus:ring-1"
              style={inputStyle}
            />
          </div>
          <button
            type="submit"
            disabled={passwordMutation.isPending || !currentPassword || !newPassword}
            className="px-4 py-2 rounded-lg text-sm font-medium transition-opacity hover:opacity-80 disabled:opacity-40"
            style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
          >
            {t("settings.changePassword")}
          </button>
        </form>
      </div>

      {/* Appearance */}
      <div
        className="rounded-xl border p-5 space-y-4"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <h2 className="text-sm font-semibold" style={{ color: "var(--foreground)" }}>
          {t("settings.appearance")}
        </h2>
        <div className="flex gap-3">
          <button
            onClick={() => setTheme("light")}
            className="flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-all"
            style={{
              backgroundColor: theme === "light" ? "var(--primary)" : "var(--card)",
              color: theme === "light" ? "var(--primary-foreground)" : "var(--foreground)",
              borderColor: theme === "light" ? "var(--primary)" : "var(--border)",
            }}
          >
            {t("settings.light")}
          </button>
          <button
            onClick={() => setTheme("dark")}
            className="flex-1 rounded-lg border px-4 py-3 text-sm font-medium transition-all"
            style={{
              backgroundColor: theme === "dark" ? "var(--primary)" : "var(--card)",
              color: theme === "dark" ? "var(--primary-foreground)" : "var(--foreground)",
              borderColor: theme === "dark" ? "var(--primary)" : "var(--border)",
            }}
          >
            {t("settings.dark")}
          </button>
        </div>
      </div>

      {/* Account info */}
      <div
        className="rounded-xl border p-5"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        <h2 className="text-sm font-semibold mb-2" style={{ color: "var(--foreground)" }}>
          {t("settings.account")}
        </h2>
        <p className="text-xs opacity-50" style={{ color: "var(--foreground)" }}>
          {t("settings.memberSince")}{" "}
          {user?.createdAt
            ? new Date(user.createdAt).toLocaleDateString(locale === "es" ? "es-PY" : "en-US", {
                month: "long",
                year: "numeric",
              })
            : "—"}
        </p>
      </div>
    </div>
  );
}
