import datetime
import uuid

import strawberry

from app.graphql.invitations.enums import InvitationStatus
from app.graphql.invitations.models.invitation import Invitation
from app.graphql.wallets.enums import WalletRole


@strawberry.type
class InvitationType:
    id: uuid.UUID
    wallet_id: uuid.UUID
    wallet_name: str
    invited_by_name: str | None
    invited_email: str
    role: WalletRole
    status: InvitationStatus
    created_at: datetime.datetime

    @classmethod
    def from_model(cls, model: Invitation) -> "InvitationType":
        return cls(
            id=uuid.UUID(str(model.id)),
            wallet_id=uuid.UUID(str(model.wallet_id)),
            wallet_name=getattr(model, "wallet_name", "Unknown"),
            invited_by_name=getattr(model, "invited_by_name", None),
            invited_email=model.invited_email,
            role=model.role,
            status=model.status,
            created_at=model.created_at,
        )


@strawberry.input
class InviteUserInput:
    wallet_id: uuid.UUID
    invited_email: str
    role: WalletRole = WalletRole.VIEWER
