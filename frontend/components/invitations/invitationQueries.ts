const INVITATION_FIELDS = `
  id walletId walletName invitedByName invitedEmail role status createdAt
`;

export const RECEIVED_INVITATIONS_QUERY = `
  query GetReceivedInvitations {
    receivedInvitations {
      ${INVITATION_FIELDS}
    }
  }
`;

export const SENT_INVITATIONS_QUERY = `
  query GetSentInvitations($walletId: UUID!) {
    sentInvitations(walletId: $walletId) {
      ${INVITATION_FIELDS}
    }
  }
`;

export const WALLET_MEMBERS_QUERY = `
  query GetWalletMembers($walletId: UUID!) {
    walletMembers(walletId: $walletId) {
      userId name email role joinedAt
    }
  }
`;

export const INVITE_USER_MUTATION = `
  mutation InviteUser($input: InviteUserInput!) {
    inviteUser(input: $input) {
      ${INVITATION_FIELDS}
    }
  }
`;

export const ACCEPT_INVITATION_MUTATION = `
  mutation AcceptInvitation($invitationId: UUID!) {
    acceptInvitation(invitationId: $invitationId) {
      id status
    }
  }
`;

export const REJECT_INVITATION_MUTATION = `
  mutation RejectInvitation($invitationId: UUID!) {
    rejectInvitation(invitationId: $invitationId) {
      id status
    }
  }
`;

export const CANCEL_INVITATION_MUTATION = `
  mutation CancelInvitation($invitationId: UUID!) {
    cancelInvitation(invitationId: $invitationId)
  }
`;
