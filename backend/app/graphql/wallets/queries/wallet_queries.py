import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.graphql.transactions.services.transaction_service import TransactionService
from app.graphql.wallets.services.wallet_service import WalletService
from app.graphql.wallets.types.wallet_types import WalletMemberDetailType, WalletType


@strawberry.type
class WalletQueries:
    @strawberry.field
    @inject
    async def wallets(
        self,
        wallet_service: Injected[WalletService],
        transaction_service: Injected[TransactionService],
    ) -> list[WalletType]:
        wallets = await wallet_service.get_user_wallets()
        balances = await transaction_service.get_wallet_balances(wallets)
        return [
            WalletType.from_model(w, wallet_service.auth_info.user_id, balances.get(uuid.UUID(str(w.id))))
            for w in wallets
        ]

    @strawberry.field
    @inject
    async def wallet(
        self,
        wallet_id: uuid.UUID,
        wallet_service: Injected[WalletService],
        transaction_service: Injected[TransactionService],
    ) -> WalletType:
        try:
            wallet = await wallet_service.get_by_id(wallet_id)
        except Exception as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        balance = await transaction_service.get_wallet_balance(wallet_id, wallet.initial_balance)
        return WalletType.from_model(wallet, wallet_service.auth_info.user_id, balance)

    @strawberry.field
    @inject
    async def wallet_members(
        self,
        wallet_id: uuid.UUID,
        wallet_service: Injected[WalletService],
    ) -> list[WalletMemberDetailType]:
        try:
            rows = await wallet_service.get_wallet_members(wallet_id)
        except Exception as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return [
            WalletMemberDetailType(
                user_id=uuid.UUID(str(member.user_id)),
                name=user.name,
                email=user.email,
                role=member.role,
                joined_at=member.created_at,
            )
            for member, user in rows
        ]
