# DB Layer — Guide for Claude Agents

## Purpose
Defines SQLAlchemy models and engine configuration. Single-schema PostgreSQL (no multi-tenant).

## Available Base Classes

```python
from app.db.base import BaseModel, HasCreatedAt, HasUpdatedAt

class MyModel(BaseModel, HasCreatedAt, HasUpdatedAt, kw_only=True):
    __tablename__ = "my_table"
    # ... columns
```

| Class | Provides | Init |
|-------|----------|------|
| `BaseModel` | `id: UUID` (auto PK) + `AsyncAttrs` | `init=False` |
| `HasCreatedAt` | `created_at: datetime` (server_default) | `init=False` |
| `HasUpdatedAt` | `updated_at: datetime \| None` (onupdate) | `init=False` |

## Model Pattern (MappedAsDataclass)

```python
import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import BaseModel, HasCreatedAt, HasUpdatedAt

class Wallet(BaseModel, HasCreatedAt, HasUpdatedAt, kw_only=True):
    __tablename__ = "wallets"

    # Fields with init (go in constructor)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Optional fields (with default)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    # Relationships (always init=False)
    user: Mapped["User"] = relationship(init=False, lazy="joined")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="wallet",
        cascade="all, delete-orphan",
        default_factory=list,
        lazy="selectin",
    )
```

## Common Column Types

```python
from decimal import Decimal
from sqlalchemy import DECIMAL, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import TypeDecorator
import enum

# IntEnum for PostgreSQL (stored as SmallInteger)
class IntEnum(TypeDecorator):
    impl = SmallInteger
    cache_ok = True
    def __init__(self, enumtype): self._enumtype = enumtype
    def process_bind_param(self, value, dialect):
        return value.value if hasattr(value, "value") else value
    def process_result_value(self, value, dialect):
        return self._enumtype(value) if value is not None else None

# Decimal for monetary amounts
amount: Mapped[Decimal] = mapped_column(DECIMAL(precision=15, scale=2), nullable=False)

# JSONB with change tracking
metadata: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False)
```

## Lazy Loading Strategies
- `lazy="joined"` → Eager JOIN (1:1 or N:1 relations)
- `lazy="selectin"` → SELECT IN (1:N collections)
- `lazy="select"` → Lazy load (only when not always needed)

## Migrations
```bash
# Create new migration (ONLY create, never run manually)
uv run alembic revision --autogenerate -m "add wallets table"
```
Files are created in `alembic/versions/`. The `env.py` imports `Base.metadata` automatically.
