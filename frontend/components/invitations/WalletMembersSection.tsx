"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showSuccess, showError } from "@/components/lib/toast";
import { WalletRole } from "@/components/wallets/types";
import { Invitation } from "./types";
import {
  WALLET_MEMBERS_QUERY,
  SENT_INVITATIONS_QUERY,
  INVITE_USER_MUTATION,
  CANCEL_INVITATION_MUTATION,
} from "./invitationQueries";

interface WalletMember {
  userId: string;
  name: string;
  email: string;
  role: WalletRole;
  joinedAt: string;
}

interface Props {
  walletId: string;
  isOwner: boolean;
  currentUserId?: string;
}

const ROLE_LABELS: Record<WalletRole, string> = {
  OWNER: "Owner",
  EDITOR: "Editor",
  VIEWER: "Viewer",
};

export function WalletMembersSection({ walletId, isOwner }: Props) {
  const queryClient = useQueryClient();
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"EDITOR" | "VIEWER">("VIEWER");

  const { data: membersData, isLoading: membersLoading } = useQuery({
    queryKey: ["walletMembers", walletId],
    queryFn: () =>
      graphqlRequest<{ walletMembers: WalletMember[] }>(WALLET_MEMBERS_QUERY, {
        walletId,
      }),
    staleTime: 30_000,
  });

  const { data: sentData, isLoading: sentLoading } = useQuery({
    queryKey: ["sentInvitations", walletId],
    queryFn: () =>
      graphqlRequest<{ sentInvitations: Invitation[] }>(
        SENT_INVITATIONS_QUERY,
        { walletId }
      ),
    staleTime: 30_000,
    enabled: isOwner,
  });

  const inviteMutation = useMutation({
    mutationFn: (input: { walletId: string; invitedEmail: string; role: string }) =>
      graphqlRequest(INVITE_USER_MUTATION, { input }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sentInvitations", walletId] });
      showSuccess("Invitation sent");
      setEmail("");
    },
    onError: showError,
  });

  const cancelMutation = useMutation({
    mutationFn: (invitationId: string) =>
      graphqlRequest(CANCEL_INVITATION_MUTATION, { invitationId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sentInvitations", walletId] });
      showSuccess("Invitation cancelled");
    },
    onError: showError,
  });

  const members = membersData?.walletMembers ?? [];
  const pendingInvitations = (sentData?.sentInvitations ?? []).filter(
    (inv) => inv.status === "PENDING"
  );

  function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    inviteMutation.mutate({ walletId, invitedEmail: email.trim(), role });
  }

  return (
    <div className="space-y-6">
      {/* Members list */}
      <div>
        <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--foreground)" }}>
          Members
        </h3>
        {membersLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-12 rounded-xl animate-pulse"
                style={{ backgroundColor: "var(--muted)" }}
              />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {members.map((member) => (
              <div
                key={member.userId}
                className="rounded-xl border px-4 py-3 flex items-center gap-3"
                style={{
                  backgroundColor: "var(--card)",
                  borderColor: "var(--border)",
                }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                  style={{
                    backgroundColor: "var(--primary)",
                    color: "var(--primary-foreground)",
                  }}
                >
                  {member.name.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate" style={{ color: "var(--foreground)" }}>
                    {member.name}
                  </p>
                  <p className="text-xs opacity-50 truncate" style={{ color: "var(--foreground)" }}>
                    {member.email}
                  </p>
                </div>
                <span
                  className="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0"
                  style={{
                    backgroundColor:
                      member.role === "OWNER"
                        ? "var(--primary)"
                        : "var(--secondary)",
                    color:
                      member.role === "OWNER"
                        ? "var(--primary-foreground)"
                        : "var(--foreground)",
                  }}
                >
                  {ROLE_LABELS[member.role]}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Invite form — owner only */}
      {isOwner && (
        <div>
          <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--foreground)" }}>
            Invite someone
          </h3>
          <form onSubmit={handleInvite} className="flex gap-2">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              className="flex-1 text-sm rounded-lg border px-3 py-2 outline-none focus:ring-1"
              style={{
                backgroundColor: "var(--input)",
                borderColor: "var(--border)",
                color: "var(--foreground)",
              }}
            />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as "EDITOR" | "VIEWER")}
              className="text-sm rounded-lg border px-2 py-2 outline-none"
              style={{
                backgroundColor: "var(--input)",
                borderColor: "var(--border)",
                color: "var(--foreground)",
              }}
            >
              <option value="VIEWER">Viewer</option>
              <option value="EDITOR">Editor</option>
            </select>
            <button
              type="submit"
              disabled={inviteMutation.isPending || !email.trim()}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-opacity hover:opacity-80 disabled:opacity-40"
              style={{
                backgroundColor: "var(--primary)",
                color: "var(--primary-foreground)",
              }}
            >
              Invite
            </button>
          </form>
        </div>
      )}

      {/* Pending invitations — owner only */}
      {isOwner && (
        <div>
          <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--foreground)" }}>
            Pending invitations
          </h3>
          {sentLoading ? (
            <div className="h-10 rounded-xl animate-pulse" style={{ backgroundColor: "var(--muted)" }} />
          ) : pendingInvitations.length === 0 ? (
            <p className="text-xs opacity-50" style={{ color: "var(--foreground)" }}>
              No pending invitations
            </p>
          ) : (
            <div className="space-y-2">
              {pendingInvitations.map((inv) => (
                <div
                  key={inv.id}
                  className="rounded-xl border px-4 py-3 flex items-center gap-3"
                  style={{
                    backgroundColor: "var(--card)",
                    borderColor: "var(--border)",
                  }}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate" style={{ color: "var(--foreground)" }}>
                      {inv.invitedEmail}
                    </p>
                    <p className="text-xs opacity-50" style={{ color: "var(--foreground)" }}>
                      as {inv.role.toLowerCase()}
                    </p>
                  </div>
                  <button
                    onClick={() => cancelMutation.mutate(inv.id)}
                    disabled={cancelMutation.isPending}
                    className="text-xs px-3 py-1.5 rounded-lg font-medium border transition-opacity hover:opacity-70 disabled:opacity-40"
                    style={{
                      borderColor: "var(--border)",
                      color: "var(--foreground)",
                    }}
                  >
                    Cancel
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
