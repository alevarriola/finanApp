import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.auth.auth_info import AuthInfo
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.users.services.user_service import UserService
from app.graphql.users.types.user_types import UserType


@strawberry.type
class UserMutations:
    @strawberry.mutation
    @inject
    async def update_profile(
        self,
        name: str,
        service: Injected[UserService],
        auth_info: Injected[AuthInfo],
    ) -> UserType:
        try:
            user = await service.update_name(auth_info.user_id, name)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        return UserType.from_model(user)

    @strawberry.mutation
    @inject
    async def change_password(
        self,
        current_password: str,
        new_password: str,
        service: Injected[UserService],
        auth_info: Injected[AuthInfo],
    ) -> bool:
        try:
            await service.change_password(auth_info.user_id, current_password, new_password)
        except (NotFoundError, UnauthorizedError) as e:
            code = 404 if isinstance(e, NotFoundError) else 401
            raise GraphQLError(str(e), extensions={"statusCode": code})
        return True
