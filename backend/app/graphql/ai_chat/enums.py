import enum

import strawberry


@strawberry.enum
class ValidationStatus(enum.IntEnum):
    PARSED = 1
    VALIDATED = 2
