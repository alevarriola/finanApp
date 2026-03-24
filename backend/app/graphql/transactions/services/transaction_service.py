import datetime
import uuid
from decimal import Decimal

from app.auth.auth_info import AuthInfo
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.transactions.enums import TransactionKind
from app.graphql.transactions.models.transaction import Transaction
from app.graphql.transactions.repositories.transaction_repository import TransactionRepository
from app.graphql.wallets.enums import WalletRole
from app.graphql.wallets.repositories.wallet_repository import WalletRepository

_UNSET = object()


class TransactionService:
    def __init__(
        self,
        repository: TransactionRepository,
        wallet_repository: WalletRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.wallet_repository = wallet_repository
        self.auth_info = auth_info

    async def _check_wallet_access(
        self, wallet_id: uuid.UUID, require_editor: bool = False
    ) -> None:
        wallet = await self.wallet_repository.get_by_id(wallet_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        member = await self.wallet_repository.get_member(wallet_id, self.auth_info.user_id)
        if not member:
            raise NotFoundError("Wallet not found")
        if require_editor and member.role == WalletRole.VIEWER:
            raise UnauthorizedError("Viewers cannot modify transactions")

    async def create_transaction(
        self,
        wallet_id: uuid.UUID,
        amount: Decimal,
        transaction_kind: TransactionKind,
        date: datetime.date,
        category_id: uuid.UUID | None = None,
        description: str | None = None,
    ) -> Transaction:
        await self._check_wallet_access(wallet_id, require_editor=True)
        transaction = Transaction(
            wallet_id=wallet_id,
            amount=amount,
            transaction_kind=transaction_kind,
            date=date,
            created_by_id=self.auth_info.user_id,
            category_id=category_id,
            description=description,
        )
        transaction_id = transaction.id
        await self.repository.create(transaction)
        result = await self.repository.get_by_id(transaction_id)
        return result  # type: ignore[return-value]

    async def list_transactions(
        self,
        wallet_id: uuid.UUID,
        transaction_kind: TransactionKind | None = None,
        category_id: uuid.UUID | None = None,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
    ) -> list[Transaction]:
        await self._check_wallet_access(wallet_id)
        return await self.repository.get_by_wallet(
            wallet_id,
            transaction_kind=transaction_kind,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        )

    async def update_transaction(
        self,
        transaction_id: uuid.UUID,
        amount: Decimal | None = None,
        description: str | None = None,
        date: datetime.date | None = None,
        category_id: uuid.UUID | None = None,
    ) -> Transaction:
        transaction = await self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError("Transaction not found")
        await self._check_wallet_access(transaction.wallet_id, require_editor=True)

        if amount is not None:
            transaction.amount = amount
        if description is not None:
            transaction.description = description
        if date is not None:
            transaction.date = date
        if category_id is not None:
            transaction.category_id = category_id

        return await self.repository.save(transaction)

    async def delete_transaction(self, transaction_id: uuid.UUID) -> None:
        transaction = await self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError("Transaction not found")
        await self._check_wallet_access(transaction.wallet_id, require_editor=True)
        await self.repository.delete(transaction)

    async def get_wallet_balance(self, wallet_id: uuid.UUID, initial_balance: Decimal) -> Decimal:
        net = await self.repository.get_wallet_net(wallet_id)
        return initial_balance + net

    async def get_wallet_balances(self, wallets: list) -> dict[uuid.UUID, Decimal]:
        if not wallets:
            return {}
        nets = await self.repository.get_nets_for_wallets([uuid.UUID(str(w.id)) for w in wallets])
        return {
            uuid.UUID(str(w.id)): w.initial_balance + nets.get(uuid.UUID(str(w.id)), Decimal("0"))
            for w in wallets
        }
