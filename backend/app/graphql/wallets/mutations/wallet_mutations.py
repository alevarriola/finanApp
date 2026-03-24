import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.wallets.services.wallet_service import WalletService
from app.graphql.wallets.types.wallet_types import CreateWalletInput, UpdateWalletInput, WalletType


@strawberry.type
class WalletMutations:
    @strawberry.mutation
    @inject
    async def create_wallet(
        self,
        input: CreateWalletInput,
        service: Injected[WalletService],
    ) -> WalletType:
        wallet = await service.create_wallet(
            name=input.name,
            wallet_kind=input.wallet_kind,
            currency=input.currency,
            initial_balance=input.initial_balance,
        )
        return WalletType.from_model(wallet, service.auth_info.user_id)

    @strawberry.mutation
    @inject
    async def update_wallet(
        self,
        input: UpdateWalletInput,
        service: Injected[WalletService],
    ) -> WalletType:
        try:
            wallet = await service.update_wallet(
                wallet_id=input.wallet_id,
                name=input.name,
                currency=input.currency,
            )
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return WalletType.from_model(wallet, service.auth_info.user_id)

    @strawberry.mutation
    @inject
    async def archive_wallet(
        self,
        wallet_id: uuid.UUID,
        service: Injected[WalletService],
    ) -> WalletType:
        try:
            wallet = await service.archive_wallet(wallet_id)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return WalletType.from_model(wallet, service.auth_info.user_id)
