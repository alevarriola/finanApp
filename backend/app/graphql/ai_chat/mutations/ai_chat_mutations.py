import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.graphql.ai_chat.services.ai_chat_service import AiChatService
from app.graphql.ai_chat.types.ai_chat_types import (
    ParsedTransactionType,
    ValidatedTransactionType,
)


@strawberry.type
class AiChatMutations:
    @strawberry.mutation
    @inject
    async def parse_transaction(
        self,
        text: str,
        service: Injected[AiChatService],
    ) -> ParsedTransactionType:
        try:
            parsed = await service.parse_transaction(text)
        except PermissionError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403, "type": "FeatureLockedError"})
        except ValueError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 400, "type": "ValidationError"})

        return ParsedTransactionType.from_model(parsed)

    @strawberry.mutation
    @inject
    async def validate_transaction(
        self,
        text: str,
        service: Injected[AiChatService],
    ) -> ValidatedTransactionType:
        try:
            validated = await service.validate_transaction(text)
        except PermissionError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403, "type": "FeatureLockedError"})
        except ValueError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 400, "type": "ValidationError"})

        return ValidatedTransactionType.from_model(validated)
