export const TRANSACTIONS_QUERY = `
  query GetTransactions($walletId: UUID!, $transactionKind: TransactionKind, $dateFrom: Date, $dateTo: Date) {
    transactions(walletId: $walletId, transactionKind: $transactionKind, dateFrom: $dateFrom, dateTo: $dateTo) {
      id
      walletId
      amount
      transactionKind
      date
      description
      categoryId
      createdAt
    }
  }
`;

export const CATEGORIES_QUERY = `
  query GetCategories {
    categories {
      id
      name
      nameEs
      categoryKind
      color
      isGlobal
    }
  }
`;

export const CREATE_TRANSACTION_MUTATION = `
  mutation CreateTransaction($input: CreateTransactionInput!, $idempotencyKey: UUID) {
    createTransaction(input: $input, idempotencyKey: $idempotencyKey) {
      id
      walletId
      amount
      transactionKind
      date
      description
      categoryId
      createdAt
    }
  }
`;

export const UPDATE_TRANSACTION_MUTATION = `
  mutation UpdateTransaction($input: UpdateTransactionInput!) {
    updateTransaction(input: $input) {
      id
      amount
      transactionKind
      date
      description
      categoryId
    }
  }
`;

export const DELETE_TRANSACTION_MUTATION = `
  mutation DeleteTransaction($transactionId: UUID!) {
    deleteTransaction(transactionId: $transactionId)
  }
`;
