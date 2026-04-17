import enum

import strawberry


@strawberry.enum
class ValidationStatus(enum.IntEnum):
    PARSED = 1
    VALIDATED = 2


@strawberry.enum
class AiTransactionEventStatus(enum.IntEnum):
    VALIDATED = 1
    CONFIRMED = 2
    EDITED = 3
    CANCELLED = 4
