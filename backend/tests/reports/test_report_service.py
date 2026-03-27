import datetime
from decimal import Decimal

import pytest

from app.auth.auth_info import AuthInfo
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.models.category import Category
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.reports.repositories.report_repository import ReportRepository
from app.graphql.reports.services.report_service import ReportService
from app.graphql.reports.types.report_types import DashboardFiltersInput
from app.graphql.reports.enums import ReportPeriod
from app.graphql.transactions.enums import TransactionKind
from app.graphql.transactions.models.transaction import Transaction
from app.graphql.transactions.repositories.transaction_repository import TransactionRepository
from app.graphql.wallets.enums import WalletKind
from app.graphql.wallets.repositories.wallet_repository import WalletRepository
from app.graphql.wallets.services.wallet_service import WalletService
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService

TODAY = datetime.date.today()


async def _make_user(session, email: str):
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(email=email, name=email.split("@")[0], password="pass123")


def _wallet_service(session, user):
    return WalletService(WalletRepository(session), AuthInfo(user_id=user.id, email=user.email))


def _report_service(session, user):
    return ReportService(ReportRepository(session), AuthInfo(user_id=user.id, email=user.email))


async def _create_wallet(session, user, name="Test Wallet", currency="PYG", initial=Decimal("0")):
    svc = _wallet_service(session, user)
    return await svc.create_wallet(name=name, wallet_kind=WalletKind.CASH, currency=currency, initial_balance=initial)


async def _create_transaction(session, wallet_id, amount, kind, date=None, category_id=None):
    tx = Transaction(
        wallet_id=wallet_id,
        amount=amount,
        transaction_kind=kind,
        date=date or TODAY,
        category_id=category_id,
    )
    session.add(tx)
    await session.flush()
    return tx


async def _create_category(session, name, kind=CategoryKind.EXPENSE, color="#ff0000"):
    cat = Category(name=name, category_kind=kind, color=color)
    session.add(cat)
    await session.flush()
    return cat


@pytest.fixture
async def owner(test_user):
    return test_user


@pytest.fixture
async def wallet(session, owner):
    return await _create_wallet(session, owner, "PYG Wallet", "PYG", Decimal("1000000"))


# ── available_currencies ──────────────────────────────────────────────────────

async def test_available_currencies_single(session, owner, wallet):
    svc = _report_service(session, owner)
    currencies = await svc.get_available_currencies()
    assert currencies == ["PYG"]


async def test_available_currencies_multiple(session, owner, wallet):
    await _create_wallet(session, owner, "USD Wallet", "USD", Decimal("500"))
    svc = _report_service(session, owner)
    currencies = await svc.get_available_currencies()
    assert set(currencies) == {"PYG", "USD"}


# ── dashboard_summary basic ──────────────────────────────────────────────────

async def test_summary_empty_wallet(session, owner, wallet):
    svc = _report_service(session, owner)
    summary = await svc.get_dashboard_summary(DashboardFiltersInput(period=ReportPeriod.THIS_MONTH))

    assert summary.currency == "PYG"
    assert summary.total_balance == Decimal("1000000")
    assert summary.period_income == Decimal("0")
    assert summary.period_expense == Decimal("0")
    assert summary.expenses_by_category == []
    assert summary.top_expense_category is None


async def test_summary_with_transactions(session, owner, wallet):
    await _create_transaction(session, wallet.id, Decimal("500000"), TransactionKind.INCOME)
    await _create_transaction(session, wallet.id, Decimal("200000"), TransactionKind.EXPENSE)

    svc = _report_service(session, owner)
    summary = await svc.get_dashboard_summary(DashboardFiltersInput(period=ReportPeriod.THIS_MONTH))

    assert summary.total_balance == Decimal("1300000")  # 1M + 500k - 200k
    assert summary.period_income == Decimal("500000")
    assert summary.period_expense == Decimal("200000")


# ── multi-currency isolation ─────────────────────────────────────────────────

async def test_summary_filters_by_currency(session, owner, wallet):
    usd_wallet = await _create_wallet(session, owner, "USD Wallet", "USD", Decimal("1000"))
    await _create_transaction(session, wallet.id, Decimal("500000"), TransactionKind.INCOME)
    await _create_transaction(session, usd_wallet.id, Decimal("100"), TransactionKind.INCOME)

    svc = _report_service(session, owner)

    # PYG dashboard
    pyg_summary = await svc.get_dashboard_summary(
        DashboardFiltersInput(period=ReportPeriod.THIS_MONTH, currency="PYG")
    )
    assert pyg_summary.currency == "PYG"
    assert pyg_summary.total_balance == Decimal("1500000")  # 1M + 500k
    assert pyg_summary.period_income == Decimal("500000")

    # USD dashboard
    usd_summary = await svc.get_dashboard_summary(
        DashboardFiltersInput(period=ReportPeriod.THIS_MONTH, currency="USD")
    )
    assert usd_summary.currency == "USD"
    assert usd_summary.total_balance == Decimal("1100")  # 1000 + 100
    assert usd_summary.period_income == Decimal("100")


async def test_summary_auto_detects_first_currency(session, owner, wallet):
    svc = _report_service(session, owner)
    summary = await svc.get_dashboard_summary(DashboardFiltersInput(period=ReportPeriod.THIS_MONTH))
    assert summary.currency == "PYG"


# ── expenses_by_category ─────────────────────────────────────────────────────

async def test_summary_expenses_by_category(session, owner, wallet):
    food = await _create_category(session, "Food", CategoryKind.EXPENSE, "#4ade80")
    transport = await _create_category(session, "Transport", CategoryKind.EXPENSE, "#f87171")

    await _create_transaction(session, wallet.id, Decimal("100000"), TransactionKind.EXPENSE, category_id=food.id)
    await _create_transaction(session, wallet.id, Decimal("150000"), TransactionKind.EXPENSE, category_id=food.id)
    await _create_transaction(session, wallet.id, Decimal("50000"), TransactionKind.EXPENSE, category_id=transport.id)

    svc = _report_service(session, owner)
    summary = await svc.get_dashboard_summary(DashboardFiltersInput(period=ReportPeriod.THIS_MONTH))

    assert len(summary.expenses_by_category) == 2
    assert summary.expenses_by_category[0].category_name == "Food"
    assert summary.expenses_by_category[0].total == Decimal("250000")
    assert summary.expenses_by_category[1].category_name == "Transport"
    assert summary.expenses_by_category[1].total == Decimal("50000")
    assert summary.top_expense_category == "Food"
    assert summary.top_expense_amount == Decimal("250000")


# ── monthly_evolution ─────────────────────────────────────────────────────────

async def test_summary_monthly_evolution_has_6_months(session, owner, wallet):
    svc = _report_service(session, owner)
    summary = await svc.get_dashboard_summary(DashboardFiltersInput(period=ReportPeriod.THIS_MONTH))
    assert len(summary.monthly_evolution) == 6


async def test_summary_monthly_evolution_current_month(session, owner, wallet):
    await _create_transaction(session, wallet.id, Decimal("300000"), TransactionKind.INCOME)
    await _create_transaction(session, wallet.id, Decimal("100000"), TransactionKind.EXPENSE)

    svc = _report_service(session, owner)
    summary = await svc.get_dashboard_summary(DashboardFiltersInput(period=ReportPeriod.THIS_MONTH))

    current_month = summary.monthly_evolution[-1]
    assert current_month.month == TODAY.strftime("%Y-%m")
    assert current_month.income == Decimal("300000")
    assert current_month.expense == Decimal("100000")


# ── wallet_id filter ─────────────────────────────────────────────────────────

async def test_summary_wallet_filter(session, owner, wallet):
    wallet2 = await _create_wallet(session, owner, "Savings", "PYG", Decimal("500000"))
    await _create_transaction(session, wallet.id, Decimal("100000"), TransactionKind.INCOME)
    await _create_transaction(session, wallet2.id, Decimal("200000"), TransactionKind.INCOME)

    svc = _report_service(session, owner)

    # Filter to wallet1 only
    summary = await svc.get_dashboard_summary(
        DashboardFiltersInput(period=ReportPeriod.THIS_MONTH, wallet_id=wallet.id)
    )
    assert summary.total_balance == Decimal("1100000")  # 1M + 100k
    assert summary.period_income == Decimal("100000")


# ── period filter ────────────────────────────────────────────────────────────

async def test_summary_period_this_month_only(session, owner, wallet):
    # Transaction this month
    await _create_transaction(session, wallet.id, Decimal("100000"), TransactionKind.EXPENSE, date=TODAY)
    # Transaction last month
    last_month = (TODAY.replace(day=1) - datetime.timedelta(days=1))
    await _create_transaction(session, wallet.id, Decimal("50000"), TransactionKind.EXPENSE, date=last_month)

    svc = _report_service(session, owner)
    summary = await svc.get_dashboard_summary(DashboardFiltersInput(period=ReportPeriod.THIS_MONTH))

    # period_expense should only include this month
    assert summary.period_expense == Decimal("100000")
    # total_balance includes all time
    assert summary.total_balance == Decimal("850000")  # 1M - 100k - 50k
