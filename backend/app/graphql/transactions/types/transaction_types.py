import datetime
import uuid
from decimal import Decimal

import strawberry

from app.graphql.transactions.enums import TransactionKind
from app.graphql.transactions.models.transaction import Transaction


@strawberry.type
class TransactionType:
    id: uuid.UUID
    wallet_id: uuid.UUID
    amount: Decimal
    transaction_kind: TransactionKind
    date: datetime.date
    description: str | None
    category_id: uuid.UUID | None
    created_by_id: uuid.UUID | None
    created_at: datetime.datetime
    wallet_name: str | None
    wallet_currency: str | None

    @classmethod
    def from_model(cls, model: Transaction) -> "TransactionType":
        return cls(
            id=uuid.UUID(str(model.id)),
            wallet_id=uuid.UUID(str(model.wallet_id)),
            amount=model.amount,
            transaction_kind=model.transaction_kind,
            date=model.date,
            description=model.description,
            category_id=uuid.UUID(str(model.category_id)) if model.category_id else None,
            created_by_id=uuid.UUID(str(model.created_by_id)) if model.created_by_id else None,
            created_at=model.created_at,
            wallet_name=getattr(model, "wallet_name", None),
            wallet_currency=getattr(model, "wallet_currency", None),
        )


@strawberry.input
class CreateTransactionInput:
    wallet_id: uuid.UUID
    amount: Decimal
    transaction_kind: TransactionKind
    date: datetime.date
    category_id: uuid.UUID | None = None
    description: str | None = None


@strawberry.input
class UpdateTransactionInput:
    transaction_id: uuid.UUID
    amount: Decimal | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    date: datetime.date | None = strawberry.UNSET
    category_id: uuid.UUID | None = strawberry.UNSET
