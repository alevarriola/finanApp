import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, HasCreatedAt, HasUpdatedAt
from app.db.types import IntEnumType
from app.graphql.wallets.enums import WalletKind


class Wallet(BaseModel, HasCreatedAt, HasUpdatedAt, kw_only=True):
    __tablename__ = "wallets"

    # Required fields (no defaults)
    name: Mapped[str] = mapped_column(String(100))
    wallet_kind: Mapped[WalletKind] = mapped_column(IntEnumType(WalletKind))
    owner_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # Optional fields (with defaults)
    currency: Mapped[str] = mapped_column(String(10), default="PYG")
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=Decimal("0"))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    members: Mapped[list["WalletMember"]] = relationship(  # type: ignore[name-defined]
        "WalletMember",
        back_populates="wallet",
        cascade="all, delete-orphan",
        default_factory=list,
        init=False,
    )
