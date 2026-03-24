import enum

import strawberry


@strawberry.enum
class CategoryKind(enum.IntEnum):
    INCOME = 1
    EXPENSE = 2
