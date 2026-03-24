export const WALLETS_QUERY = `
  query GetWallets {
    wallets {
      id
      name
      walletKind
      currency
      initialBalance
      currentBalance
      isArchived
      myRole
      createdAt
    }
  }
`;

export const CREATE_WALLET_MUTATION = `
  mutation CreateWallet($input: CreateWalletInput!) {
    createWallet(input: $input) {
      id
      name
      walletKind
      currency
      initialBalance
      currentBalance
      myRole
    }
  }
`;

export const UPDATE_WALLET_MUTATION = `
  mutation UpdateWallet($input: UpdateWalletInput!) {
    updateWallet(input: $input) {
      id
      name
      currency
    }
  }
`;

export const ARCHIVE_WALLET_MUTATION = `
  mutation ArchiveWallet($walletId: UUID!) {
    archiveWallet(walletId: $walletId) {
      id
      isArchived
    }
  }
`;
