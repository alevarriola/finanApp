import uuid

import bcrypt

from app.core.email_service import create_verification_token, get_verification_data, send_verification_email
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

    async def update_name(self, user_id: uuid.UUID, name: str) -> User:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        user.name = name
        return await self.repository.save(user)

    async def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> None:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if not bcrypt.checkpw(current_password.encode(), user.hashed_password.encode()):
            raise UnauthorizedError("Current password is incorrect")
        user.hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        await self.repository.save(user)

    async def send_verification_email(self, user_id: uuid.UUID) -> bool:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if user.is_verified:
            return True
        token = await create_verification_token(user.id, user.email)
        send_verification_email(user.email, token)
        return True

    async def verify_email(self, token: uuid.UUID) -> bool:
        data = await get_verification_data(token)
        if not data:
            raise NotFoundError("Invalid or expired verification link")
        user = await self.repository.get_by_id(uuid.UUID(data["user_id"]))
        if not user:
            raise NotFoundError("User not found")
        if user.email != data["email"]:
            raise UnauthorizedError("Email mismatch")
        user.is_verified = True
        await self.repository.save(user)
        return True
