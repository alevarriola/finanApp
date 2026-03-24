import datetime
import uuid
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, HasCreatedAt
from app.db.types import IntEnumType
from app.graphql.transactions.enums import TransactionKind


class Transaction(BaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "transactions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    transaction_kind: Mapped[TransactionKind] = mapped_column(IntEnumType(TransactionKind))
    date: Mapped[datetime.date] = mapped_column(Date)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )

    category_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)
