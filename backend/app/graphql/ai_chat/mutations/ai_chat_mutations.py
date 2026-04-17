import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.graphql.ai_chat.services.ai_chat_service import (
    AiChatService,
    AiProviderError,
    RateLimitError,
    SuspiciousPromptError,
)
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
        except RateLimitError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 429, "type": "RateLimitError"})
        except SuspiciousPromptError as e:
            raise GraphQLError(
                str(e),
                extensions={"statusCode": 400, "type": "SuspiciousPromptError"},
            )
        except ValueError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 400, "type": "AiInputError"})
        except AiProviderError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 503, "type": "AiProviderError"})

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
        except RateLimitError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 429, "type": "RateLimitError"})
        except SuspiciousPromptError as e:
            raise GraphQLError(
                str(e),
                extensions={"statusCode": 400, "type": "SuspiciousPromptError"},
            )
        except ValueError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 400, "type": "AiInputError"})
        except AiProviderError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 503, "type": "AiProviderError"})

        return ValidatedTransactionType.from_model(validated)
