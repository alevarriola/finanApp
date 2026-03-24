import pytest

from app.core.exceptions import DuplicateError, UnauthorizedError
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService


@pytest.fixture
def user_service(session):
    return UserService(UserRepository(session))


async def test_register_creates_user(user_service):
    user = await user_service.register(
        email="new@test.com",
        name="New User",
        password="secret123",
    )

    assert user.email == "new@test.com"
    assert user.name == "New User"
    assert user.hashed_password != "secret123"
    assert user.is_active is True


async def test_register_duplicate_email_raises(user_service, test_user):
    with pytest.raises(DuplicateError):
        await user_service.register(
            email=test_user.email,
            name="Other",
            password="password123",
        )


async def test_login_success(user_service, test_user):
    user = await user_service.login(email=test_user.email, password="password123")
    assert user.id == test_user.id


async def test_login_wrong_password_raises(user_service, test_user):
    with pytest.raises(UnauthorizedError):
        await user_service.login(email=test_user.email, password="wrong")


async def test_login_unknown_email_raises(user_service):
    with pytest.raises(UnauthorizedError):
        await user_service.login(email="ghost@test.com", password="password123")


async def test_get_by_id(user_service, test_user):
    found = await user_service.get_by_id(test_user.id)
    assert found is not None
    assert found.id == test_user.id


async def test_get_by_id_unknown_returns_none(user_service):
    import uuid
    found = await user_service.get_by_id(uuid.uuid4())
    assert found is None
