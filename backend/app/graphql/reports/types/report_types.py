import uuid
from decimal import Decimal

import strawberry

from app.graphql.reports.enums import ReportPeriod


@strawberry.type
class CategorySpend:
    category_id: uuid.UUID | None
    category_name: str
    category_name_es: str | None
    color: str
    total: Decimal


@strawberry.type
class MonthlyPoint:
    month: str  # "2026-01"
    income: Decimal
    expense: Decimal


@strawberry.type
class DashboardSummary:
    currency: str
    total_balance: Decimal
    period_income: Decimal
    period_expense: Decimal
    top_expense_category: str | None
    top_expense_category_es: str | None
    top_expense_amount: Decimal | None
    expenses_by_category: list[CategorySpend]
    monthly_evolution: list[MonthlyPoint]


@strawberry.input
class DashboardFiltersInput:
    period: ReportPeriod = ReportPeriod.THIS_MONTH
    wallet_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    currency: str | None = None
