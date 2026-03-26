"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { showError, showSuccess } from "@/components/lib/toast";

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(1, "Password is required"),
});

type FormValues = z.infer<typeof schema>;

export default function SignInPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    });

    if (!res.ok) {
      const data = await res.json();
      showError(new Error(data.error ?? "Login failed"));
      return;
    }

    showSuccess("Welcome back!");
    router.push("/dashboard");
    router.refresh();
  }

  return (
    <div
      className="rounded-2xl shadow-lg p-8 border"
      style={{
        backgroundColor: "var(--card)",
        borderColor: "var(--border)",
      }}
    >
      <h1
        className="text-2xl font-bold mb-1"
        style={{ color: "var(--primary)" }}
      >
        Kash
      </h1>
      <p className="text-sm mb-6" style={{ color: "var(--foreground)" }}>
        Sign in to your account
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label
            className="block text-sm font-medium mb-1"
            style={{ color: "var(--foreground)" }}
          >
            Email
          </label>
          <input
            {...register("email")}
            type="email"
            autoComplete="email"
            className="w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2"
            style={{
              borderColor: errors.email ? "#dc2626" : "var(--border)",
              backgroundColor: "var(--background)",
              color: "var(--foreground)",
            }}
          />
          {errors.email && (
            <p className="text-xs mt-1 text-red-600">{errors.email.message}</p>
          )}
        </div>

        <div>
          <label
            className="block text-sm font-medium mb-1"
            style={{ color: "var(--foreground)" }}
          >
            Password
          </label>
          <input
            {...register("password")}
            type="password"
            autoComplete="current-password"
            className="w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2"
            style={{
              borderColor: errors.password ? "#dc2626" : "var(--border)",
              backgroundColor: "var(--background)",
              color: "var(--foreground)",
            }}
          />
          {errors.password && (
            <p className="text-xs mt-1 text-red-600">
              {errors.password.message}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full py-2 px-4 rounded-lg text-sm font-semibold transition-opacity disabled:opacity-60"
          style={{
            backgroundColor: "var(--primary)",
            color: "var(--primary-foreground)",
          }}
        >
          {isSubmitting ? "Signing in..." : "Sign in"}
        </button>
      </form>

      <p className="text-sm text-center mt-4" style={{ color: "var(--foreground)" }}>
        No account?{" "}
        <Link
          href="/sign-up"
          className="font-medium hover:underline"
          style={{ color: "var(--primary)" }}
        >
          Create one
        </Link>
      </p>
    </div>
  );
}
