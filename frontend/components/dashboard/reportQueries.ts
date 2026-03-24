export const DASHBOARD_SUMMARY_QUERY = `
  query GetDashboardSummary($filters: DashboardFiltersInput!) {
    dashboardSummary(filters: $filters) {
      totalBalance
      periodIncome
      periodExpense
      topExpenseCategory
      topExpenseAmount
      expensesByCategory {
        categoryId
        categoryName
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
