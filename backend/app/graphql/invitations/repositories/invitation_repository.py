import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.invitations.enums import InvitationStatus
from app.graphql.invitations.models.invitation import Invitation
from app.graphql.users.models.user import User
from app.graphql.wallets.models.wallet import Wallet


def _attach_names(inv: Invitation, wallet_name: str, invited_by_name: str | None) -> Invitation:
    inv.wallet_name = wallet_name  # type: ignore[attr-defined]
    inv.invited_by_name = invited_by_name  # type: ignore[attr-defined]
    return inv


class InvitationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, invitation_id: uuid.UUID) -> Invitation | None:
        stmt = (
            select(Invitation, Wallet.name, User.name)
            .join(Wallet, Invitation.wallet_id == Wallet.id)
            .outerjoin(User, Invitation.invited_by_id == User.id)
            .where(Invitation.id == invitation_id)
        )
        row = (await self.session.execute(stmt)).one_or_none()
        if row is None:
            return None
        inv, wallet_name, invited_by_name = row
        return _attach_names(inv, wallet_name or "Unknown", invited_by_name)

    async def get_pending_for_email(self, email: str) -> list[Invitation]:
        stmt = (
            select(Invitation, Wallet.name, User.name)
            .join(Wallet, Invitation.wallet_id == Wallet.id)
            .outerjoin(User, Invitation.invited_by_id == User.id)
            .where(
                Invitation.invited_email == email.lower(),
                Invitation.status == InvitationStatus.PENDING,
            )
            .order_by(Invitation.created_at.desc())
        )
        rows = (await self.session.execute(stmt)).all()
        return [_attach_names(inv, wn or "Unknown", ibn) for inv, wn, ibn in rows]

    async def get_for_wallet(self, wallet_id: uuid.UUID) -> list[Invitation]:
        stmt = (
            select(Invitation, Wallet.name, User.name)
            .join(Wallet, Invitation.wallet_id == Wallet.id)
            .outerjoin(User, Invitation.invited_by_id == User.id)
            .where(Invitation.wallet_id == wallet_id)
            .order_by(Invitation.created_at.desc())
        )
        rows = (await self.session.execute(stmt)).all()
        return [_attach_names(inv, wn or "Unknown", ibn) for inv, wn, ibn in rows]

    async def get_pending_for_wallet_and_email(
        self, wallet_id: uuid.UUID, email: str
    ) -> Invitation | None:
        stmt = select(Invitation).where(
            Invitation.wallet_id == wallet_id,
            Invitation.invited_email == email.lower(),
            Invitation.status == InvitationStatus.PENDING,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, invitation: Invitation) -> Invitation:
        self.session.add(invitation)
        await self.session.flush()
        return invitation

    async def save(self, invitation: Invitation) -> Invitation:
        await self.session.flush()
        return invitation
