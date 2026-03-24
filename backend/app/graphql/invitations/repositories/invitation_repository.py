import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.graphql.invitations.enums import InvitationStatus
from app.graphql.invitations.models.invitation import Invitation


class InvitationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, invitation_id: uuid.UUID) -> Invitation | None:
        stmt = (
            select(Invitation)
            .where(Invitation.id == invitation_id)
            .options(selectinload(Invitation.wallet), selectinload(Invitation.invited_by))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_for_email(self, email: str) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .where(
                Invitation.invited_email == email.lower(),
                Invitation.status == InvitationStatus.PENDING,
            )
            .options(selectinload(Invitation.wallet), selectinload(Invitation.invited_by))
            .order_by(Invitation.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_for_wallet(self, wallet_id: uuid.UUID) -> list[Invitation]:
        stmt = (
            select(Invitation)
            .where(Invitation.wallet_id == wallet_id)
            .options(selectinload(Invitation.wallet), selectinload(Invitation.invited_by))
            .order_by(Invitation.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

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
