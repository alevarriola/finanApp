import enum

import strawberry


@strawberry.enum
class InvitationStatus(enum.IntEnum):
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3
    CANCELLED = 4
