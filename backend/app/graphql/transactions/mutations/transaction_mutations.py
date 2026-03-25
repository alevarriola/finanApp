import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.auth.auth_info import AuthInfo
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.idempotency import check_idempotency, raise_duplicate, save_idempotency
from app.graphql.transactions.services.transaction_service import TransactionService
from app.graphql.transactions.types.transaction_types import (
    CreateTransactionInput,
    TransactionType,
    UpdateTransactionInput,
)


@strawberry.type
class TransactionMutations:
    @strawberry.mutation
    @inject
    async def create_transaction(
        self,
        input: CreateTransactionInput,
        service: Injected[TransactionService],
        auth_info: Injected[AuthInfo],
        idempotency_key: uuid.UUID | None = None,
    ) -> TransactionType:
        if idempotency_key:
            cached = await check_idempotency(auth_info.user_id, idempotency_key)
            if cached:
                raise_duplicate()

        try:
            transaction = await service.create_transaction(
                wallet_id=input.wallet_id,
                amount=input.amount,
                transaction_kind=input.transaction_kind,
                date=input.date,
                category_id=input.category_id,
                description=input.description,
            )
        except (NotFoundError, UnauthorizedError) as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})

        if idempotency_key:
            await save_idempotency(auth_info.user_id, idempotency_key, {"id": str(transaction.id)})

        return TransactionType.from_model(transaction)

    @strawberry.mutation
    @inject
    async def update_transaction(
        self,
        input: UpdateTransactionInput,
        service: Injected[TransactionService],
    ) -> TransactionType:
        kwargs = {}
        if input.amount is not strawberry.UNSET:
            kwargs["amount"] = input.amount
        if input.description is not strawberry.UNSET:
            kwargs["description"] = input.description
        if input.date is not strawberry.UNSET:
            kwargs["date"] = input.date
        if input.category_id is not strawberry.UNSET:
            kwargs["category_id"] = input.category_id
        try:
            transaction = await service.update_transaction(input.transaction_id, **kwargs)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return TransactionType.from_model(transaction)

    @strawberry.mutation
    @inject
    async def delete_transaction(
        self,
        transaction_id: uuid.UUID,
        service: Injected[TransactionService],
    ) -> bool:
        try:
            await service.delete_transaction(transaction_id)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return True
