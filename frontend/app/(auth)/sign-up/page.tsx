"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showError, showSuccess } from "@/components/lib/toast";
import { PasswordInput } from "@/components/shared/PasswordInput";

const REGISTER_MUTATION = `
  mutation Register($input: RegisterInput!) {
    register(input: $input) {
      accessToken
      refreshToken
      user {
        id
        email
        name
      }
    }
  }
`;

const schema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type FormValues = z.infer<typeof schema>;

interface RegisterData {
  register: {
    accessToken: string;
    refreshToken: string;
    user: { id: string; email: string; name: string };
  };
}

export default function SignUpPage() {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    try {
      const { confirmPassword: _, ...input } = values;
      const data = await graphqlRequest<RegisterData>(REGISTER_MUTATION, {
        input,
      });

      // Set cookies via login endpoint reusing tokens
      await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: values.email, password: values.password }),
      });

      showSuccess(`Welcome, ${data.register.user.name}!`);
      router.push("/dashboard");
      router.refresh();
    } catch (err) {
      showError(err);
    }
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
        Create your account
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label
            className="block text-sm font-medium mb-1"
            style={{ color: "var(--foreground)" }}
          >
            Name
          </label>
          <input
            {...register("name")}
            type="text"
            autoComplete="name"
            className="w-full px-3 py-2 rounded-lg border text-sm outline-none focus:ring-2"
            style={{
              borderColor: errors.name ? "#dc2626" : "var(--border)",
              backgroundColor: "var(--background)",
              color: "var(--foreground)",
            }}
          />
          {errors.name && (
            <p className="text-xs mt-1 text-red-600">{errors.name.message}</p>
          )}
        </div>

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
          <PasswordInput
            {...register("password")}
            autoComplete="new-password"
            hasError={!!errors.password}
          />
          {errors.password && (
            <p className="text-xs mt-1 text-red-600">
              {errors.password.message}
            </p>
          )}
        </div>

        <div>
          <label
            className="block text-sm font-medium mb-1"
            style={{ color: "var(--foreground)" }}
          >
            Confirm password
          </label>
          <PasswordInput
            {...register("confirmPassword")}
            autoComplete="new-password"
            hasError={!!errors.confirmPassword}
          />
          {errors.confirmPassword && (
            <p className="text-xs mt-1 text-red-600">
              {errors.confirmPassword.message}
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
          {isSubmitting ? "Creating account..." : "Create account"}
        </button>
      </form>

      <p className="text-sm text-center mt-4" style={{ color: "var(--foreground)" }}>
        Already have an account?{" "}
        <Link
          href="/sign-in"
          className="font-medium hover:underline"
          style={{ color: "var(--primary)" }}
        >
          Sign in
        </Link>
      </p>
    </div>
  );
}
