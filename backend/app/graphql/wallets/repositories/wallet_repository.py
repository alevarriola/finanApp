import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.graphql.users.models.user import User
from app.graphql.wallets.models.wallet import Wallet
from app.graphql.wallets.models.wallet_member import WalletMember


class WalletRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_wallets(self, user_id: uuid.UUID) -> list[Wallet]:
        stmt = (
            select(Wallet)
            .join(WalletMember, Wallet.id == WalletMember.wallet_id)
            .where(WalletMember.user_id == user_id)
            .where(Wallet.is_archived.is_(False))
            .options(selectinload(Wallet.members))
            .order_by(Wallet.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique())

    async def get_by_id(self, wallet_id: uuid.UUID) -> Wallet | None:
        stmt = (
            select(Wallet)
            .where(Wallet.id == wallet_id)
            .options(selectinload(Wallet.members))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_member(self, wallet_id: uuid.UUID, user_id: uuid.UUID) -> WalletMember | None:
        stmt = select(WalletMember).where(
            WalletMember.wallet_id == wallet_id,
            WalletMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_members_with_users(
        self, wallet_id: uuid.UUID
    ) -> list[tuple[WalletMember, User]]:
        stmt = (
            select(WalletMember, User)
            .join(User, WalletMember.user_id == User.id)
            .where(WalletMember.wallet_id == wallet_id)
            .order_by(WalletMember.created_at)
        )
        result = await self.session.execute(stmt)
        return list(result.tuples())

    async def create(self, wallet: Wallet) -> Wallet:
        self.session.add(wallet)
        await self.session.flush()
        return wallet

    async def add_member(self, member: WalletMember) -> WalletMember:
        self.session.add(member)
        await self.session.flush()
        return member

    async def save(self, wallet: Wallet) -> Wallet:
        await self.session.flush()
        return wallet
