import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, HasCreatedAt
from app.db.types import IntEnumType
from app.graphql.wallets.enums import WalletRole


class WalletMember(BaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "wallet_members"
    __table_args__ = (UniqueConstraint("wallet_id", "user_id", name="uq_wallet_members_wallet_user"),)

    # Required fields (no defaults)
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    # Optional fields
    role: Mapped[WalletRole] = mapped_column(IntEnumType(WalletRole), default=WalletRole.OWNER)

    wallet: Mapped["Wallet"] = relationship(  # type: ignore[name-defined]
        "Wallet",
        back_populates="members",
        init=False,
        default=None,
    )
