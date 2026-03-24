import enum

import strawberry


@strawberry.enum
class TransactionKind(enum.IntEnum):
    INCOME = 1
    EXPENSE = 2
