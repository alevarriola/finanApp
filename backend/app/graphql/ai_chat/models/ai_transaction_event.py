import uuid
from typing import Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, HasCreatedAt, HasUpdatedAt
from app.db.types import IntEnumType
from app.graphql.ai_chat.enums import AiTransactionEventStatus


class AiTransactionEvent(BaseModel, HasCreatedAt, HasUpdatedAt, kw_only=True):
    __tablename__ = "ai_transaction_events"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    raw_text: Mapped[str] = mapped_column(String(500))
    status: Mapped[AiTransactionEventStatus] = mapped_column(IntEnumType(AiTransactionEventStatus))
    parsed_output: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=None)
    validated_output: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=None
    )
    final_output: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=None)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True, default=None)
    corrected_fields: Mapped[list[str]] = mapped_column(JSONB, default_factory=list)
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        index=True,
    )
