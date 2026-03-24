import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject

from app.core.middleware.graphql_middleware import get_current_auth_info
from app.graphql.users.services.user_service import UserService
from app.graphql.users.types.user_types import UserType


@strawberry.type
class UserQueries:
    @strawberry.field
    @inject
    async def me(self, service: Injected[UserService]) -> UserType | None:
        auth_info = get_current_auth_info()
        if auth_info is None:
            return None
        user = await service.get_by_id(auth_info.user_id)
        return UserType.from_model(user) if user else None
