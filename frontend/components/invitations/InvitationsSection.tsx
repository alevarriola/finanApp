"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { graphqlRequest } from "@/components/lib/graphql/client";
import { showSuccess, showError } from "@/components/lib/toast";
import { Invitation } from "./types";
import {
  RECEIVED_INVITATIONS_QUERY,
  ACCEPT_INVITATION_MUTATION,
  REJECT_INVITATION_MUTATION,
} from "./invitationQueries";
import { useI18n } from "@/components/i18n/I18nProvider";

export function InvitationsSection() {
  const { t } = useI18n();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["receivedInvitations"],
    queryFn: () =>
      graphqlRequest<{ receivedInvitations: Invitation[] }>(
        RECEIVED_INVITATIONS_QUERY
      ),
    staleTime: 30_000,
  });

  const acceptMutation = useMutation({
    mutationFn: (invitationId: string) =>
      graphqlRequest(ACCEPT_INVITATION_MUTATION, { invitationId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["receivedInvitations"] });
      queryClient.invalidateQueries({ queryKey: ["wallets"] });
      showSuccess(t("toast.invitationAccepted"));
    },
    onError: showError,
  });

  const rejectMutation = useMutation({
    mutationFn: (invitationId: string) =>
      graphqlRequest(REJECT_INVITATION_MUTATION, { invitationId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["receivedInvitations"] });
      showSuccess(t("toast.invitationRejected"));
    },
    onError: showError,
  });

  const invitations = data?.receivedInvitations ?? [];

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div
            key={i}
            className="h-16 rounded-xl animate-pulse"
            style={{ backgroundColor: "var(--muted)" }}
          />
        ))}
      </div>
    );
  }

  if (invitations.length === 0) {
    return (
      <div
        className="rounded-xl border-2 border-dashed p-8 text-center"
        style={{ borderColor: "var(--border)" }}
      >
        <p className="text-sm opacity-50" style={{ color: "var(--foreground)" }}>
          {t("invitations.noPending")}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {invitations.map((inv) => (
        <div
          key={inv.id}
          className="rounded-xl border px-4 py-3 flex items-center gap-4"
          style={{ backgroundColor: "var(--card)", borderColor: "var(--border)" }}
        >
          <div
            className="w-2 h-8 rounded-full flex-shrink-0"
            style={{ backgroundColor: "var(--primary)" }}
          />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium" style={{ color: "var(--foreground)" }}>
              {inv.walletName}
            </p>
            <p className="text-xs opacity-50" style={{ color: "var(--foreground)" }}>
              {inv.invitedByName
                ? `${t("invitations.invitedBy")} ${inv.invitedByName}`
                : ""}{" "}
              · {t("invitations.asRole")} {inv.role.toLowerCase()}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => acceptMutation.mutate(inv.id)}
              disabled={acceptMutation.isPending}
              className="text-xs px-3 py-1.5 rounded-lg font-medium transition-opacity hover:opacity-80"
              style={{ backgroundColor: "var(--primary)", color: "var(--primary-foreground)" }}
            >
              {t("invitations.accept")}
            </button>
            <button
              onClick={() => rejectMutation.mutate(inv.id)}
              disabled={rejectMutation.isPending}
              className="text-xs px-3 py-1.5 rounded-lg font-medium border transition-opacity hover:opacity-70"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
            >
              {t("invitations.reject")}
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
