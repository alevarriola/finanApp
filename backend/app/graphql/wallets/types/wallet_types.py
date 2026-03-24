import datetime
import uuid
from decimal import Decimal

import strawberry

from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.models.wallet import Wallet


@strawberry.type
class WalletMemberType:
    user_id: uuid.UUID
    role: WalletRole


@strawberry.type
class WalletType:
    id: uuid.UUID
    name: str
    wallet_kind: WalletKind
    currency: str
    initial_balance: Decimal
    current_balance: Decimal
    is_archived: bool
    owner_id: uuid.UUID
    my_role: WalletRole
    members: list[WalletMemberType]
    created_at: datetime.datetime

    @classmethod
    def from_model(
        cls,
        model: Wallet,
        my_user_id: uuid.UUID,
        current_balance: Decimal | None = None,
    ) -> "WalletType":
        my_role = WalletRole.VIEWER
        for m in model.members:
            if uuid.UUID(str(m.user_id)) == my_user_id:
                my_role = m.role
                break

        return cls(
            id=uuid.UUID(str(model.id)),
            name=model.name,
            wallet_kind=model.wallet_kind,
            currency=model.currency,
            initial_balance=model.initial_balance,
            current_balance=current_balance if current_balance is not None else model.initial_balance,
            is_archived=model.is_archived,
            owner_id=uuid.UUID(str(model.owner_id)),
            my_role=my_role,
            members=[
                WalletMemberType(user_id=uuid.UUID(str(m.user_id)), role=m.role)
                for m in model.members
            ],
            created_at=model.created_at,
        )


@strawberry.input
class CreateWalletInput:
    name: str
    wallet_kind: WalletKind
    currency: str = "PYG"
    initial_balance: Decimal = Decimal("0")


@strawberry.input
class UpdateWalletInput:
    wallet_id: uuid.UUID
    name: str | None = None
    currency: str | None = None
