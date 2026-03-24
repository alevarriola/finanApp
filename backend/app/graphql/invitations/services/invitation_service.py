import uuid

from app.auth.auth_info import AuthInfo
from app.core.exceptions import DuplicateError, NotFoundError, UnauthorizedError
from app.graphql.invitations.enums import InvitationStatus
from app.graphql.invitations.models.invitation import Invitation
from app.graphql.invitations.repositories.invitation_repository import InvitationRepository
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.wallets.enums import WalletRole
from app.graphql.wallets.models.wallet_member import WalletMember
from app.graphql.wallets.repositories.wallet_repository import WalletRepository


class InvitationService:
    def __init__(
        self,
        repository: InvitationRepository,
        wallet_repository: WalletRepository,
        user_repository: UserRepository,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.wallet_repository = wallet_repository
        self.user_repository = user_repository
        self.auth_info = auth_info

    async def invite_user(
        self,
        wallet_id: uuid.UUID,
        invited_email: str,
        role: WalletRole,
    ) -> Invitation:
        invited_email = invited_email.lower().strip()

        if invited_email == self.auth_info.email.lower():
            raise DuplicateError("You cannot invite yourself")

        member = await self.wallet_repository.get_member(wallet_id, self.auth_info.user_id)
        if not member or member.role != WalletRole.OWNER:
            raise UnauthorizedError("Only owners can invite members")

        invited_user = await self.user_repository.get_by_email(invited_email)
        if invited_user:
            existing = await self.wallet_repository.get_member(wallet_id, invited_user.id)
            if existing:
                raise DuplicateError("User is already a member of this wallet")

        pending = await self.repository.get_pending_for_wallet_and_email(wallet_id, invited_email)
        if pending:
            raise DuplicateError("A pending invitation already exists for this email")

        invitation = Invitation(
            wallet_id=wallet_id,
            invited_by_id=self.auth_info.user_id,
            invited_email=invited_email,
            role=role,
        )
        invitation_id = invitation.id
        await self.repository.create(invitation)
        result = await self.repository.get_by_id(invitation_id)
        return result  # type: ignore[return-value]

    async def list_received(self) -> list[Invitation]:
        return await self.repository.get_pending_for_email(self.auth_info.email)

    async def list_sent_for_wallet(self, wallet_id: uuid.UUID) -> list[Invitation]:
        member = await self.wallet_repository.get_member(wallet_id, self.auth_info.user_id)
        if not member or member.role != WalletRole.OWNER:
            raise UnauthorizedError("Only owners can view wallet invitations")
        return await self.repository.get_for_wallet(wallet_id)

    async def accept_invitation(self, invitation_id: uuid.UUID) -> Invitation:
        inv = await self.repository.get_by_id(invitation_id)
        if not inv or inv.invited_email != self.auth_info.email.lower():
            raise NotFoundError("Invitation not found")
        if inv.status != InvitationStatus.PENDING:
            raise UnauthorizedError("Invitation is no longer pending")

        user = await self.user_repository.get_by_email(self.auth_info.email)
        if not user:
            raise NotFoundError("User not found")

        wallet_id = uuid.UUID(str(inv.wallet_id))
        existing = await self.wallet_repository.get_member(wallet_id, user.id)
        if not existing:
            member = WalletMember(
                wallet_id=wallet_id,
                user_id=user.id,
                role=inv.role,
            )
            await self.wallet_repository.add_member(member)

        inv.status = InvitationStatus.ACCEPTED
        return await self.repository.save(inv)

    async def reject_invitation(self, invitation_id: uuid.UUID) -> Invitation:
        inv = await self.repository.get_by_id(invitation_id)
        if not inv or inv.invited_email != self.auth_info.email.lower():
            raise NotFoundError("Invitation not found")
        if inv.status != InvitationStatus.PENDING:
            raise UnauthorizedError("Invitation is no longer pending")
        inv.status = InvitationStatus.REJECTED
        return await self.repository.save(inv)

    async def cancel_invitation(self, invitation_id: uuid.UUID) -> bool:
        inv = await self.repository.get_by_id(invitation_id)
        if not inv:
            raise NotFoundError("Invitation not found")
        member = await self.wallet_repository.get_member(
            uuid.UUID(str(inv.wallet_id)), self.auth_info.user_id
        )
        if not member or member.role != WalletRole.OWNER:
            raise UnauthorizedError("Only owners can cancel invitations")
        if inv.status != InvitationStatus.PENDING:
            raise UnauthorizedError("Only pending invitations can be cancelled")
        inv.status = InvitationStatus.CANCELLED
        await self.repository.save(inv)
        return True
