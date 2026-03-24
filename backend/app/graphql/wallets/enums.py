import enum

import strawberry


@strawberry.enum
class WalletKind(enum.IntEnum):
    CASH = 1
    BANK = 2
    DEBIT = 3
    CREDIT = 4


@strawberry.enum
class WalletRole(enum.IntEnum):
    OWNER = 1
    EDITOR = 2
    VIEWER = 3
