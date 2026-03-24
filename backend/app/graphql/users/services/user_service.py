import uuid

import bcrypt

from app.core.exceptions import DuplicateError, NotFoundError, UnauthorizedError
from app.graphql.users.models.user import User
from app.graphql.users.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register(self, email: str, name: str, password: str) -> User:
        existing = await self.repository.get_by_email(email)
        if existing:
            raise DuplicateError("A user with this email already exists")

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(
            email=email.lower(),
            name=name,
            hashed_password=hashed,
        )
        return await self.repository.create(user)

    async def login(self, email: str, password: str) -> User:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid email or password")

        if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self.repository.get_by_id(user_id)
