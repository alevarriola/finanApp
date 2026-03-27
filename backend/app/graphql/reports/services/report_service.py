import datetime
import uuid
from decimal import Decimal

from app.auth.auth_info import AuthInfo
from app.graphql.reports.enums import ReportPeriod
from app.graphql.reports.repositories.report_repository import ReportRepository
from app.graphql.reports.types.report_types import (
    CategorySpend,
    DashboardFiltersInput,
    DashboardSummary,
    MonthlyPoint,
)


def _get_date_range(period: ReportPeriod) -> tuple[datetime.date, datetime.date]:
    today = datetime.date.today()

    def subtract_months(n: int) -> datetime.date:
        month = today.month - n
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        return datetime.date(year, month, 1)

    if period == ReportPeriod.THIS_MONTH:
        return today.replace(day=1), today
    if period == ReportPeriod.LAST_MONTH:
        first_current = today.replace(day=1)
        last_prev = first_current - datetime.timedelta(days=1)
        return last_prev.replace(day=1), last_prev
    if period == ReportPeriod.LAST_3_MONTHS:
        return subtract_months(2), today
    if period == ReportPeriod.LAST_6_MONTHS:
        return subtract_months(5), today
    # THIS_YEAR
    return datetime.date(today.year, 1, 1), today


def _six_months_start() -> datetime.date:
    today = datetime.date.today()
    month = today.month - 5
    year = today.year
    while month <= 0:
        month += 12
        year -= 1
    return datetime.date(year, month, 1)


def _build_monthly_evolution(
    income_rows: list[tuple],
    expense_rows: list[tuple],
) -> list[MonthlyPoint]:
    income_map = {(r[0].year, r[0].month): r[1] for r in income_rows}
    expense_map = {(r[0].year, r[0].month): r[1] for r in expense_rows}

    today = datetime.date.today()
    points: list[MonthlyPoint] = []
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        points.append(
            MonthlyPoint(
                month=f"{year}-{month:02d}",
                income=income_map.get((year, month), Decimal(0)),
                expense=expense_map.get((year, month), Decimal(0)),
            )
        )
    return points


class ReportService:
    def __init__(self, repository: ReportRepository, auth_info: AuthInfo) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def get_available_currencies(self) -> list[str]:
        return await self.repository.get_user_currencies(self.auth_info.user_id)

    async def get_dashboard_summary(self, filters: DashboardFiltersInput) -> DashboardSummary:
        user_id = self.auth_info.user_id
        wallet_id: uuid.UUID | None = filters.wallet_id
        category_id: uuid.UUID | None = filters.category_id
        currency: str | None = filters.currency
        start, end = _get_date_range(filters.period)
        monthly_start = _six_months_start()

        # Auto-detect currency if not specified
        if not currency and not wallet_id:
            currencies = await self.repository.get_user_currencies(user_id)
            currency = currencies[0] if currencies else "PYG"

        total_balance = await self.repository.get_total_balance(user_id, wallet_id, currency)
        income, expense = await self.repository.get_period_stats(
            user_id, start, end, wallet_id, category_id, currency
        )
        cat_rows = await self.repository.get_expenses_by_category(
            user_id, start, end, wallet_id, currency
        )
        income_rows = await self.repository.get_monthly_income(
            user_id, monthly_start, wallet_id, category_id, currency
        )
        expense_rows = await self.repository.get_monthly_expense(
            user_id, monthly_start, wallet_id, category_id, currency
        )

        expenses_by_category = [
            CategorySpend(
                category_id=row[0],
                category_name=row[1] or "Uncategorized",
                category_name_es=row[2] or "Sin categoria",
                color=row[3] or "#94a3b8",
                total=row[4],
            )
            for row in cat_rows
        ]
        monthly_evolution = _build_monthly_evolution(income_rows, expense_rows)

        return DashboardSummary(
            currency=currency or "PYG",
            total_balance=total_balance,
            period_income=income,
            period_expense=expense,
            top_expense_category=expenses_by_category[0].category_name if expenses_by_category else None,
            top_expense_amount=expenses_by_category[0].total if expenses_by_category else None,
            expenses_by_category=expenses_by_category,
            monthly_evolution=monthly_evolution,
        )
