import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject
from graphql import GraphQLError

from app.auth.jwt_service import JWTService
from app.core.exceptions import DuplicateError, UnauthorizedError
from app.graphql.users.services.user_service import UserService
from app.graphql.users.types.user_types import LoginInput, RegisterInput, TokensType, UserType


@strawberry.type
class AuthMutations:
    @strawberry.mutation
    @inject
    async def register(
        self,
        input: RegisterInput,
        service: Injected[UserService],
        jwt_service: Injected[JWTService],
    ) -> TokensType:
        try:
            user = await service.register(
                email=input.email,
                name=input.name,
                password=input.password,
            )
        except DuplicateError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 409, "type": "DuplicateError"})

        access_token = jwt_service.create_access_token(user.id, user.email)
        refresh_token = jwt_service.create_refresh_token(user.id)

        try:
            await service.send_verification_email(user.id)
        except Exception:
            pass  # Don't block registration if email fails

        return TokensType(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserType.from_model(user),
        )

    @strawberry.mutation
    @inject
    async def login(
        self,
        input: LoginInput,
        service: Injected[UserService],
        jwt_service: Injected[JWTService],
    ) -> TokensType:
        try:
            user = await service.login(email=input.email, password=input.password)
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 401, "type": "UnauthorizedError"})

        access_token = jwt_service.create_access_token(user.id, user.email)
        refresh_token = jwt_service.create_refresh_token(user.id)

        return TokensType(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserType.from_model(user),
        )
