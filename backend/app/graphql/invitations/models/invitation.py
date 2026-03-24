import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, HasCreatedAt
from app.db.types import IntEnumType
from app.graphql.invitations.enums import InvitationStatus
from app.graphql.wallets.enums import WalletRole


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
