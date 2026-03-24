"""Custom SQLAlchemy column types."""
import enum

from sqlalchemy import SmallInteger
from sqlalchemy.types import TypeDecorator


class IntEnumType(TypeDecorator):
    """Stores a Python IntEnum as SMALLINT in PostgreSQL."""

    impl = SmallInteger
    cache_ok = True

    def __init__(self, enumtype: type[enum.IntEnum]) -> None:
        super().__init__()
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        if isinstance(value, self._enumtype):
            return value.value
        return int(value)

    def process_result_value(self, value, dialect):  # type: ignore[override]
        if value is None:
            return None
        return self._enumtype(value)
