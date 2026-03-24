"use client";

import { InvitationsSection } from "@/components/invitations/InvitationsSection";

export default function DashboardPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <h1
          className="text-2xl font-bold mb-1"
          style={{ color: "var(--foreground)" }}
        >
          Dashboard
        </h1>
        <p className="text-sm opacity-60" style={{ color: "var(--foreground)" }}>
          Your financial overview.
        </p>
      </div>

      <div>
        <h2 className="text-base font-semibold mb-3" style={{ color: "var(--foreground)" }}>
          Pending Invitations
        </h2>
        <InvitationsSection />
      </div>
    </div>
  );
}
