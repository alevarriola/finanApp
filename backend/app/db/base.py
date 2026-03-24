import datetime
import uuid

from sqlalchemy import TIMESTAMP, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(DeclarativeBase):
    pass


class HasPrimaryKey(MappedAsDataclass):
    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        default_factory=uuid.uuid4,
        primary_key=True,
        init=False,
    )


class HasCreatedAt(MappedAsDataclass):
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        init=False,
    )


class HasUpdatedAt(MappedAsDataclass):
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
        nullable=True,
        init=False,
        default=None,
    )


class BaseModel(Base, HasPrimaryKey, AsyncAttrs):
    __abstract__ = True
