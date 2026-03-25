import datetime
import uuid

import strawberry

from app.graphql.users.models.user import User


@strawberry.type
class UserType:
    id: uuid.UUID
    email: str
    name: str
    is_active: bool
    is_verified: bool
    created_at: datetime.datetime

    @classmethod
    def from_model(cls, model: User) -> "UserType":
        return cls(
            id=model.id,
            email=model.email,
            name=model.name,
            is_active=model.is_active,
            is_verified=model.is_verified,
            created_at=model.created_at,
        )


@strawberry.type
class TokensType:
    access_token: str
    refresh_token: str
    user: UserType


@strawberry.input
class RegisterInput:
    email: str
    name: str
    password: str


@strawberry.input
class LoginInput:
    email: str
    password: str
