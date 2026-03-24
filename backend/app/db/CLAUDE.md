# DB Layer — Guide for Claude Agents

## Purpose
SQLAlchemy models, engine, and custom column types. Single-schema PostgreSQL.

## Base Classes

```python
from app.db.base import BaseModel, HasCreatedAt, HasUpdatedAt

class MyModel(BaseModel, HasCreatedAt, HasUpdatedAt, kw_only=True):
    __tablename__ = "my_table"
```

| Class | Provides |
|-------|----------|
| `BaseModel` | `id: UUID` (auto PK, init=False) + AsyncAttrs |
| `HasCreatedAt` | `created_at: datetime` (server_default now(), init=False) |
| `HasUpdatedAt` | `updated_at: datetime \| None` (onupdate now(), init=False) |

## MappedAsDataclass Field Ordering Rule
Required fields (no default) MUST come before optional fields (with default):

```python
class Wallet(BaseModel, HasCreatedAt, HasUpdatedAt, kw_only=True):
    __tablename__ = "wallets"

    name: Mapped[str] = mapped_column(String(100))        # required first
    owner_id: Mapped[uuid.UUID] = mapped_column(...)      # required first
    currency: Mapped[str] = mapped_column(default="PYG")  # optional after
    is_archived: Mapped[bool] = mapped_column(default=False)
```

## IntEnumType — Enum as SMALLINT

```python
from app.db.types import IntEnumType

@strawberry.enum
class WalletKind(enum.IntEnum):
    CASH = 1
    BANK = 2
    DEBIT = 3
    CREDIT = 4

wallet_kind: Mapped[WalletKind] = mapped_column(IntEnumType(WalletKind))
```

SQLAlchemy reads integers from DB and returns the enum. GraphQL sees enum names (CASH, BANK...).
Alembic renders `IntEnumType` as `sa.SmallInteger()` via the hook in `alembic/env.py`.

## Relationships

```python
members: Mapped[list["WalletMember"]] = relationship(
    "WalletMember",
    back_populates="wallet",
    cascade="all, delete-orphan",
    default_factory=list,
    init=False,
)
```

Always `init=False` for relationships. Use explicit loading in repositories (not lazy).

## Lazy Loading Strategies
- `selectinload()` — use in repositories for 1:N collections
- `joinedload()` — use for N:1 (single object) relations

## Monetary Amounts

```python
from sqlalchemy import Numeric
amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
```

## Adding a New Model
1. Create `app/graphql/<module>/models/<model>.py`
2. No changes needed in `alembic/env.py` — models are auto-discovered via `pkgutil` scan of `app/graphql/**/models/`
3. Run `uv run alembic revision --autogenerate -m "add <model> table"`
