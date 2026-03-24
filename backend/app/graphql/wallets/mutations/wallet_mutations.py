import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.transactions.services.transaction_service import TransactionService
from app.graphql.wallets.services.wallet_service import WalletService
from app.graphql.wallets.types.wallet_types import CreateWalletInput, UpdateWalletInput, WalletType


@strawberry.type
class WalletMutations:
    @strawberry.mutation
    @inject
    async def create_wallet(
        self,
        input: CreateWalletInput,
        wallet_service: Injected[WalletService],
        transaction_service: Injected[TransactionService],
    ) -> WalletType:
        wallet = await wallet_service.create_wallet(
            name=input.name,
            wallet_kind=input.wallet_kind,
            currency=input.currency,
            initial_balance=input.initial_balance,
        )
        balance = await transaction_service.get_wallet_balance(
            uuid.UUID(str(wallet.id)), wallet.initial_balance
        )
        return WalletType.from_model(wallet, wallet_service.auth_info.user_id, balance)

    @strawberry.mutation
    @inject
    async def update_wallet(
        self,
        input: UpdateWalletInput,
        wallet_service: Injected[WalletService],
        transaction_service: Injected[TransactionService],
    ) -> WalletType:
        try:
            wallet = await wallet_service.update_wallet(
                wallet_id=input.wallet_id,
                name=input.name,
                currency=input.currency,
            )
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        balance = await transaction_service.get_wallet_balance(
            uuid.UUID(str(wallet.id)), wallet.initial_balance
        )
        return WalletType.from_model(wallet, wallet_service.auth_info.user_id, balance)

    @strawberry.mutation
    @inject
    async def archive_wallet(
        self,
        wallet_id: uuid.UUID,
        wallet_service: Injected[WalletService],
        transaction_service: Injected[TransactionService],
    ) -> WalletType:
        try:
            wallet = await wallet_service.archive_wallet(wallet_id)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        balance = await transaction_service.get_wallet_balance(
            uuid.UUID(str(wallet.id)), wallet.initial_balance
        )
        return WalletType.from_model(wallet, wallet_service.auth_info.user_id, balance)
