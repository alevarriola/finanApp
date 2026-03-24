import enum

import strawberry


@strawberry.enum
class ReportPeriod(enum.Enum):
    THIS_MONTH = "THIS_MONTH"
    LAST_MONTH = "LAST_MONTH"
    LAST_3_MONTHS = "LAST_3_MONTHS"
    LAST_6_MONTHS = "LAST_6_MONTHS"
    THIS_YEAR = "THIS_YEAR"
