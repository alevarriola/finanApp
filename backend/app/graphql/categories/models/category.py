import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel, HasCreatedAt
from app.db.types import IntEnumType
from app.graphql.categories.enums import CategoryKind


class Category(BaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100))
    category_kind: Mapped[CategoryKind] = mapped_column(IntEnumType(CategoryKind))

    icon: Mapped[str] = mapped_column(String(10), default="📁")
    color: Mapped[str] = mapped_column(String(7), default="#94a3b8")
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        default=None,
    )
