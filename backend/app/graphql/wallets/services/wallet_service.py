import uuid
from decimal import Decimal

from app.auth.auth_info import AuthInfo
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.models.wallet import Wallet
from app.graphql.wallets.models.wallet_member import WalletMember
from app.graphql.wallets.repositories.wallet_repository import WalletRepository


class WalletService:
    def __init__(self, repository: WalletRepository, auth_info: AuthInfo) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def create_wallet(
        self,
        name: str,
        wallet_kind: WalletKind,
        currency: str,
        initial_balance: Decimal,
    ) -> Wallet:
        wallet = Wallet(
            name=name,
            wallet_kind=wallet_kind,
            currency=currency,
            initial_balance=initial_balance,
            owner_id=self.auth_info.user_id,
        )
        wallet_id = wallet.id
        await self.repository.create(wallet)

        member = WalletMember(
            wallet_id=wallet_id,
            user_id=self.auth_info.user_id,
            role=WalletRole.OWNER,
        )
        await self.repository.add_member(member)
        self.repository.session.expire(wallet)

        wallet = await self.repository.get_by_id(wallet_id)
        return wallet  # type: ignore[return-value]

    async def get_user_wallets(self) -> list[Wallet]:
        return await self.repository.get_user_wallets(self.auth_info.user_id)

    async def get_by_id(self, wallet_id: uuid.UUID) -> Wallet:
        wallet = await self.repository.get_by_id(wallet_id)
        if not wallet:
            raise NotFoundError("Wallet not found")
        member = await self.repository.get_member(wallet_id, self.auth_info.user_id)
        if not member:
            raise NotFoundError("Wallet not found")
        return wallet

    async def update_wallet(
        self,
        wallet_id: uuid.UUID,
        name: str | None = None,
        currency: str | None = None,
    ) -> Wallet:
        wallet = await self.get_by_id(wallet_id)
        member = await self.repository.get_member(wallet_id, self.auth_info.user_id)
        if member and member.role == WalletRole.VIEWER:
            raise UnauthorizedError("Viewers cannot edit wallets")

        if name is not None:
            wallet.name = name
        if currency is not None:
            wallet.currency = currency

        return await self.repository.save(wallet)

    async def get_wallet_members(self, wallet_id: uuid.UUID) -> list[tuple]:
        member = await self.repository.get_member(wallet_id, self.auth_info.user_id)
        if not member:
            raise NotFoundError("Wallet not found")
        return await self.repository.get_members_with_users(wallet_id)

    async def leave_wallet(self, wallet_id: uuid.UUID) -> None:
        member = await self.repository.get_member(wallet_id, self.auth_info.user_id)
        if not member:
            raise NotFoundError("Wallet not found")
        if member.role == WalletRole.OWNER:
            raise UnauthorizedError("The owner cannot leave their own wallet")
        await self.repository.remove_member(wallet_id, self.auth_info.user_id)

    async def archive_wallet(self, wallet_id: uuid.UUID) -> Wallet:
        wallet = await self.get_by_id(wallet_id)
        member = await self.repository.get_member(wallet_id, self.auth_info.user_id)
        if not member or member.role != WalletRole.OWNER:
            raise UnauthorizedError("Only the owner can archive a wallet")

        wallet.is_archived = True
        return await self.repository.save(wallet)
