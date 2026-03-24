import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.graphql.wallets.services.wallet_service import WalletService
from app.graphql.wallets.types.wallet_types import WalletType


@strawberry.type
class WalletQueries:
    @strawberry.field
    @inject
    async def wallets(self, service: Injected[WalletService]) -> list[WalletType]:
        wallets = await service.get_user_wallets()
        return [WalletType.from_model(w, service.auth_info.user_id) for w in wallets]

    @strawberry.field
    @inject
    async def wallet(
        self,
        wallet_id: uuid.UUID,
        service: Injected[WalletService],
    ) -> WalletType:
        try:
            wallet = await service.get_by_id(wallet_id)
        except Exception as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        return WalletType.from_model(wallet, service.auth_info.user_id)
