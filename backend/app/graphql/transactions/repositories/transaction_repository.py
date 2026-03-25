import datetime
import uuid
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.transactions.enums import TransactionKind
from app.graphql.transactions.models.transaction import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_wallet(
        self,
        wallet_id: uuid.UUID,
        transaction_kind: TransactionKind | None = None,
        category_id: uuid.UUID | None = None,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
    ) -> list[Transaction]:
        stmt = select(Transaction).where(Transaction.wallet_id == wallet_id)
        if transaction_kind is not None:
            stmt = stmt.where(Transaction.transaction_kind == transaction_kind)
        if category_id is not None:
            stmt = stmt.where(Transaction.category_id == category_id)
        if date_from is not None:
            stmt = stmt.where(Transaction.date >= date_from)
        if date_to is not None:
            stmt = stmt.where(Transaction.date <= date_to)
        stmt = stmt.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_by_id(self, transaction_id: uuid.UUID) -> Transaction | None:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_wallet_net(self, wallet_id: uuid.UUID) -> Decimal:
        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.transaction_kind == TransactionKind.INCOME, Transaction.amount),
                        else_=-Transaction.amount,
                    )
                ),
                Decimal("0"),
            )
        ).where(Transaction.wallet_id == wallet_id)
        result = await self.session.execute(stmt)
        return result.scalar() or Decimal("0")

    async def get_nets_for_wallets(self, wallet_ids: list[uuid.UUID]) -> dict[uuid.UUID, Decimal]:
        if not wallet_ids:
            return {}
        stmt = (
            select(
                Transaction.wallet_id,
                func.sum(
                    case(
                        (Transaction.transaction_kind == TransactionKind.INCOME, Transaction.amount),
                        else_=-Transaction.amount,
                    )
                ).label("net"),
            )
            .where(Transaction.wallet_id.in_(wallet_ids))
            .group_by(Transaction.wallet_id)
        )
        result = await self.session.execute(stmt)
        return {uuid.UUID(str(row.wallet_id)): row.net for row in result}

    async def create(self, transaction: Transaction) -> Transaction:
        self.session.add(transaction)
        await self.session.flush()
        return transaction

    async def save(self, transaction: Transaction) -> Transaction:
        await self.session.flush()
        return transaction

    async def get_all_for_user(
        self,
        user_id: uuid.UUID,
        wallet_id: uuid.UUID | None = None,
        transaction_kind: TransactionKind | None = None,
        category_id: uuid.UUID | None = None,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
    ) -> list[Transaction]:
        from app.graphql.wallets.models.wallet import Wallet
        from app.graphql.wallets.models.wallet_member import WalletMember

        stmt = (
            select(Transaction, Wallet.name)
            .join(WalletMember, Transaction.wallet_id == WalletMember.wallet_id)
            .join(Wallet, Transaction.wallet_id == Wallet.id)
            .where(WalletMember.user_id == user_id, Wallet.is_archived.is_(False))
        )
        if wallet_id is not None:
            stmt = stmt.where(Transaction.wallet_id == wallet_id)
        if transaction_kind is not None:
            stmt = stmt.where(Transaction.transaction_kind == transaction_kind)
        if category_id is not None:
            stmt = stmt.where(Transaction.category_id == category_id)
        if date_from is not None:
            stmt = stmt.where(Transaction.date >= date_from)
        if date_to is not None:
            stmt = stmt.where(Transaction.date <= date_to)
        stmt = stmt.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        rows = (await self.session.execute(stmt)).all()
        result = []
        for txn, wallet_name in rows:
            txn.wallet_name = wallet_name  # type: ignore[attr-defined]
            result.append(txn)
        return result

    async def delete(self, transaction: Transaction) -> None:
        await self.session.delete(transaction)
        await self.session.flush()
