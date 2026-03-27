export const DASHBOARD_SUMMARY_QUERY = `
  query GetDashboardSummary($filters: DashboardFiltersInput!) {
    dashboardSummary(filters: $filters) {
      currency
      totalBalance
      periodIncome
      periodExpense
      topExpenseCategory
      topExpenseCategoryEs
      topExpenseAmount
      expensesByCategory {
        categoryId
        categoryName
        categoryNameEs
        color
        total
      }
      monthlyEvolution {
        month
        income
        expense
      }
    }
  }
`;

export const AVAILABLE_CURRENCIES_QUERY = `
  query GetAvailableCurrencies {
    availableCurrencies
  }
`;
