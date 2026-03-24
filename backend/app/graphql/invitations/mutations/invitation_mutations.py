import uuid

import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.core.exceptions import DuplicateError, NotFoundError, UnauthorizedError
from app.graphql.invitations.services.invitation_service import InvitationService
from app.graphql.invitations.types.invitation_types import InvitationType, InviteUserInput


@strawberry.type
class InvitationMutations:
    @strawberry.mutation
    @inject
    async def invite_user(
        self,
        input: InviteUserInput,
        service: Injected[InvitationService],
    ) -> InvitationType:
        try:
            invitation = await service.invite_user(
                wallet_id=input.wallet_id,
                invited_email=input.invited_email,
                role=input.role,
            )
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        except DuplicateError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 409})
        return InvitationType.from_model(invitation)

    @strawberry.mutation
    @inject
    async def accept_invitation(
        self,
        invitation_id: uuid.UUID,
        service: Injected[InvitationService],
    ) -> InvitationType:
        try:
            invitation = await service.accept_invitation(invitation_id)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return InvitationType.from_model(invitation)

    @strawberry.mutation
    @inject
    async def reject_invitation(
        self,
        invitation_id: uuid.UUID,
        service: Injected[InvitationService],
    ) -> InvitationType:
        try:
            invitation = await service.reject_invitation(invitation_id)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return InvitationType.from_model(invitation)

    @strawberry.mutation
    @inject
    async def cancel_invitation(
        self,
        invitation_id: uuid.UUID,
        service: Injected[InvitationService],
    ) -> bool:
        try:
            return await service.cancel_invitation(invitation_id)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
