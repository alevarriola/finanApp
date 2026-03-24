from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, HasCreatedAt
from app.db.types import IntEnumType
from app.graphql.invitations.enums import InvitationStatus
from app.graphql.wallets.enums import WalletRole

if TYPE_CHECKING:
    from app.graphql.users.models.user import User
    from app.graphql.wallets.models.wallet import Wallet


class Invitation(BaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "invitations"

    # Required fields first (no defaults)
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("wallets.id", ondelete="CASCADE"),
        index=True,
    )
    invited_email: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[WalletRole] = mapped_column(IntEnumType(WalletRole))

    # Defaulted fields after
    invited_by_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    token: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default_factory=uuid.uuid4,
        unique=True,
    )
    status: Mapped[InvitationStatus] = mapped_column(
        IntEnumType(InvitationStatus),
        default=InvitationStatus.PENDING,
    )

    wallet: Mapped[Wallet] = relationship("Wallet", init=False, default=None)
    invited_by: Mapped[User | None] = relationship(
        "User",
        init=False,
        default=None,
        foreign_keys=[invited_by_id],
    )
