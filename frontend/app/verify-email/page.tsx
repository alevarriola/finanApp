"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing verification token.");
      return;
    }

    async function verify() {
      try {
        const res = await fetch("/api/backend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: `mutation VerifyEmail($token: UUID!) { verifyEmail(token: $token) }`,
            variables: { token },
          }),
        });
        const json = await res.json();
        if (json.errors?.length) {
          setStatus("error");
          setMessage(json.errors[0].message);
        } else {
          setStatus("success");
        }
      } catch {
        setStatus("error");
        setMessage("Something went wrong. Please try again.");
      }
    }

    verify();
  }, [token]);

  return (
    <div
      className="min-h-screen flex items-center justify-center p-6"
      style={{ backgroundColor: "var(--background)" }}
    >
      <div
        className="max-w-sm w-full rounded-2xl border p-8 text-center"
        style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
      >
        {status === "loading" && (
          <>
            <div
              className="w-12 h-12 rounded-full mx-auto mb-4 animate-pulse"
              style={{ backgroundColor: "var(--muted)" }}
            />
            <p className="text-sm" style={{ color: "var(--foreground)" }}>
              Verifying your email...
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <div
              className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center text-xl font-bold"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            >
              ✓
            </div>
            <h1 className="text-lg font-bold mb-2" style={{ color: "var(--foreground)" }}>
              Email verified
            </h1>
            <p className="text-sm opacity-60 mb-6" style={{ color: "var(--foreground)" }}>
              Your email has been verified successfully.
            </p>
            <Link
              href="/dashboard"
              className="inline-block px-6 py-2.5 rounded-lg text-sm font-semibold"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            >
              Go to Dashboard
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <div
              className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center text-xl font-bold"
              style={{ backgroundColor: "#fef2f2", color: "#dc2626" }}
            >
              ✕
            </div>
            <h1 className="text-lg font-bold mb-2" style={{ color: "var(--foreground)" }}>
              Verification failed
            </h1>
            <p className="text-sm opacity-60 mb-6" style={{ color: "var(--foreground)" }}>
              {message || "Invalid or expired verification link."}
            </p>
            <Link
              href="/dashboard"
              className="inline-block px-6 py-2.5 rounded-lg text-sm font-semibold border"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              Go to Dashboard
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
