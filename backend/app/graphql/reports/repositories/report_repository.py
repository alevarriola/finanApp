import datetime
import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.categories.models.category import Category
from app.graphql.transactions.enums import TransactionKind
from app.graphql.transactions.models.transaction import Transaction
from app.graphql.wallets.models.wallet import Wallet
from app.graphql.wallets.models.wallet_member import WalletMember


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_tx_stmt(
        self,
        user_id: uuid.UUID,
        start: datetime.date,
        end: datetime.date,
        wallet_id: uuid.UUID | None,
        category_id: uuid.UUID | None,
        kind: TransactionKind,
        currency: str | None = None,
    ):
        stmt = (
            select(func.coalesce(func.sum(Transaction.amount), Decimal(0)))
            .join(WalletMember, Transaction.wallet_id == WalletMember.wallet_id)
            .join(Wallet, Transaction.wallet_id == Wallet.id)
            .where(
                WalletMember.user_id == user_id,
                Wallet.is_archived.is_(False),
                Transaction.transaction_kind == kind,
                Transaction.date >= start,
                Transaction.date <= end,
            )
        )
        if wallet_id:
            stmt = stmt.where(Transaction.wallet_id == wallet_id)
        if category_id:
            stmt = stmt.where(Transaction.category_id == category_id)
        if currency:
            stmt = stmt.where(Wallet.currency == currency)
        return stmt

    async def get_user_currencies(self, user_id: uuid.UUID) -> list[str]:
        stmt = (
            select(Wallet.currency)
            .join(WalletMember, Wallet.id == WalletMember.wallet_id)
            .where(WalletMember.user_id == user_id, Wallet.is_archived.is_(False))
            .distinct()
            .order_by(Wallet.currency)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows)

    async def get_total_balance(
        self, user_id: uuid.UUID, wallet_id: uuid.UUID | None = None, currency: str | None = None
    ) -> Decimal:
        initial_stmt = (
            select(func.coalesce(func.sum(Wallet.initial_balance), Decimal(0)))
            .join(WalletMember, Wallet.id == WalletMember.wallet_id)
            .where(WalletMember.user_id == user_id, Wallet.is_archived.is_(False))
        )
        if wallet_id:
            initial_stmt = initial_stmt.where(Wallet.id == wallet_id)
        if currency:
            initial_stmt = initial_stmt.where(Wallet.currency == currency)

        income_stmt = (
            select(func.coalesce(func.sum(Transaction.amount), Decimal(0)))
            .join(WalletMember, Transaction.wallet_id == WalletMember.wallet_id)
            .join(Wallet, Transaction.wallet_id == Wallet.id)
            .where(
                WalletMember.user_id == user_id,
                Wallet.is_archived.is_(False),
                Transaction.transaction_kind == TransactionKind.INCOME,
            )
        )
        expense_stmt = (
            select(func.coalesce(func.sum(Transaction.amount), Decimal(0)))
            .join(WalletMember, Transaction.wallet_id == WalletMember.wallet_id)
            .join(Wallet, Transaction.wallet_id == Wallet.id)
            .where(
                WalletMember.user_id == user_id,
                Wallet.is_archived.is_(False),
                Transaction.transaction_kind == TransactionKind.EXPENSE,
            )
        )
        if wallet_id:
            income_stmt = income_stmt.where(Transaction.wallet_id == wallet_id)
            expense_stmt = expense_stmt.where(Transaction.wallet_id == wallet_id)
        if currency:
            income_stmt = income_stmt.where(Wallet.currency == currency)
            expense_stmt = expense_stmt.where(Wallet.currency == currency)

        initial = (await self.session.execute(initial_stmt)).scalar() or Decimal(0)
        income = (await self.session.execute(income_stmt)).scalar() or Decimal(0)
        expense = (await self.session.execute(expense_stmt)).scalar() or Decimal(0)
        return initial + income - expense

    async def get_period_stats(
        self,
        user_id: uuid.UUID,
        start: datetime.date,
        end: datetime.date,
        wallet_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        currency: str | None = None,
    ) -> tuple[Decimal, Decimal]:
        income = (
            await self.session.execute(
                self._base_tx_stmt(user_id, start, end, wallet_id, category_id, TransactionKind.INCOME, currency)
            )
        ).scalar() or Decimal(0)
        expense = (
            await self.session.execute(
                self._base_tx_stmt(user_id, start, end, wallet_id, category_id, TransactionKind.EXPENSE, currency)
            )
        ).scalar() or Decimal(0)
        return income, expense

    async def get_expenses_by_category(
        self,
        user_id: uuid.UUID,
        start: datetime.date,
        end: datetime.date,
        wallet_id: uuid.UUID | None = None,
        currency: str | None = None,
    ) -> list[tuple]:
        stmt = (
            select(
                Category.id,
                Category.name,
                Category.name_es,
                Category.color,
                func.sum(Transaction.amount).label("total"),
            )
            .join(WalletMember, Transaction.wallet_id == WalletMember.wallet_id)
            .join(Wallet, Transaction.wallet_id == Wallet.id)
            .outerjoin(Category, Transaction.category_id == Category.id)
            .where(
                WalletMember.user_id == user_id,
                Wallet.is_archived.is_(False),
                Transaction.transaction_kind == TransactionKind.EXPENSE,
                Transaction.date >= start,
                Transaction.date <= end,
            )
        )
        if wallet_id:
            stmt = stmt.where(Transaction.wallet_id == wallet_id)
        if currency:
            stmt = stmt.where(Wallet.currency == currency)

        stmt = stmt.group_by(Category.id, Category.name, Category.name_es, Category.color).order_by(
            func.sum(Transaction.amount).desc()
        )
        return list((await self.session.execute(stmt)).all())

    async def get_monthly_income(
        self,
        user_id: uuid.UUID,
        start: datetime.date,
        wallet_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        currency: str | None = None,
    ) -> list[tuple]:
        month_col = func.date_trunc("month", Transaction.date).label("month")
        stmt = (
            select(month_col, func.sum(Transaction.amount).label("total"))
            .join(WalletMember, Transaction.wallet_id == WalletMember.wallet_id)
            .join(Wallet, Transaction.wallet_id == Wallet.id)
            .where(
                WalletMember.user_id == user_id,
                Wallet.is_archived.is_(False),
                Transaction.transaction_kind == TransactionKind.INCOME,
                Transaction.date >= start,
            )
        )
        if wallet_id:
            stmt = stmt.where(Transaction.wallet_id == wallet_id)
        if category_id:
            stmt = stmt.where(Transaction.category_id == category_id)
        if currency:
            stmt = stmt.where(Wallet.currency == currency)
        stmt = stmt.group_by(month_col).order_by(month_col)
        return list((await self.session.execute(stmt)).all())

    async def get_monthly_expense(
        self,
        user_id: uuid.UUID,
        start: datetime.date,
        wallet_id: uuid.UUID | None = None,
        category_id: uuid.UUID | None = None,
        currency: str | None = None,
    ) -> list[tuple]:
        month_col = func.date_trunc("month", Transaction.date).label("month")
        stmt = (
            select(month_col, func.sum(Transaction.amount).label("total"))
            .join(WalletMember, Transaction.wallet_id == WalletMember.wallet_id)
            .join(Wallet, Transaction.wallet_id == Wallet.id)
            .where(
                WalletMember.user_id == user_id,
                Wallet.is_archived.is_(False),
                Transaction.transaction_kind == TransactionKind.EXPENSE,
                Transaction.date >= start,
            )
        )
        if wallet_id:
            stmt = stmt.where(Transaction.wallet_id == wallet_id)
        if category_id:
            stmt = stmt.where(Transaction.category_id == category_id)
        if currency:
            stmt = stmt.where(Wallet.currency == currency)
        stmt = stmt.group_by(month_col).order_by(month_col)
        return list((await self.session.execute(stmt)).all())
