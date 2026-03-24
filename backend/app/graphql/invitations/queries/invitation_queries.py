import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.invitations.services.invitation_service import InvitationService
from app.graphql.invitations.types.invitation_types import InvitationType


@strawberry.type
class InvitationQueries:
    @strawberry.field
    @inject
    async def received_invitations(
        self,
        service: Injected[InvitationService],
    ) -> list[InvitationType]:
        invitations = await service.list_received()
        return [InvitationType.from_model(i) for i in invitations]

    @strawberry.field
    @inject
    async def sent_invitations(
        self,
        wallet_id: uuid.UUID,
        service: Injected[InvitationService],
    ) -> list[InvitationType]:
        try:
            invitations = await service.list_sent_for_wallet(wallet_id)
        except (NotFoundError, UnauthorizedError) as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return [InvitationType.from_model(i) for i in invitations]
