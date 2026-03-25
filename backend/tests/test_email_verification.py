import uuid

import pytest

from app.auth.auth_info import AuthInfo
from app.core.email_service import create_verification_token, get_verification_data
from app.core.exceptions import NotFoundError
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService


async def test_create_and_get_verification_token():
    user_id = uuid.uuid4()
    email = "verify@test.com"
    token = await create_verification_token(user_id, email)

    assert isinstance(token, uuid.UUID)

    data = await get_verification_data(token)
    assert data is not None
    assert data["user_id"] == str(user_id)
    assert data["email"] == email


async def test_verification_token_consumed_after_get():
    user_id = uuid.uuid4()
    token = await create_verification_token(user_id, "consume@test.com")

    data = await get_verification_data(token)
    assert data is not None

    data2 = await get_verification_data(token)
    assert data2 is None


async def test_invalid_token_returns_none():
    data = await get_verification_data(uuid.uuid4())
    assert data is None


async def test_verify_email_marks_user_verified(session, test_user):
    service = UserService(UserRepository(session))
    assert not test_user.is_verified

    token = await create_verification_token(test_user.id, test_user.email)
    result = await service.verify_email(token)

    assert result is True
    assert test_user.is_verified is True


async def test_verify_email_invalid_token_raises(session):
    service = UserService(UserRepository(session))
    with pytest.raises(NotFoundError):
        await service.verify_email(uuid.uuid4())


async def test_verify_email_wrong_email_raises(session, test_user):
    service = UserService(UserRepository(session))
    token = await create_verification_token(test_user.id, "wrong@test.com")
    from app.core.exceptions import UnauthorizedError
    with pytest.raises(UnauthorizedError):
        await service.verify_email(token)
