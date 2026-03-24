import datetime
import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.transactions.enums import TransactionKind
from app.graphql.transactions.services.transaction_service import TransactionService
from app.graphql.transactions.types.transaction_types import TransactionType


@strawberry.type
class TransactionQueries:
    @strawberry.field
    @inject
    async def transactions(
        self,
        wallet_id: uuid.UUID,
        service: Injected[TransactionService],
        transaction_kind: TransactionKind | None = None,
        category_id: uuid.UUID | None = None,
        date_from: datetime.date | None = None,
        date_to: datetime.date | None = None,
    ) -> list[TransactionType]:
        try:
            txns = await service.list_transactions(
                wallet_id=wallet_id,
                transaction_kind=transaction_kind,
                category_id=category_id,
                date_from=date_from,
                date_to=date_to,
            )
        except (NotFoundError, UnauthorizedError) as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        return [TransactionType.from_model(t) for t in txns]
