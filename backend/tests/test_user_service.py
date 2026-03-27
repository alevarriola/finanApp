import uuid

import pytest

from app.core.exceptions import DuplicateError, NotFoundError, UnauthorizedError
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService


def _service(session):
    return UserService(UserRepository(session))


# ── register ──────────────────────────────────────────────────────────────────

async def test_register_creates_user(session):
    svc = _service(session)
    user = await svc.register(email="new@test.com", name="New User", password="pass1234")

    assert user.email == "new@test.com"
    assert user.name == "New User"
    assert user.is_active is True
    assert user.is_verified is False
    assert user.hashed_password != "pass1234"


async def test_register_normalizes_email(session):
    svc = _service(session)
    user = await svc.register(email="UPPER@Test.COM", name="Upper", password="pass1234")
    assert user.email == "upper@test.com"


async def test_register_duplicate_email_raises(session):
    svc = _service(session)
    await svc.register(email="dupe@test.com", name="First", password="pass1234")
    with pytest.raises(DuplicateError):
        await svc.register(email="dupe@test.com", name="Second", password="pass1234")


# ── login ─────────────────────────────────────────────────────────────────────

async def test_login_success(session):
    svc = _service(session)
    await svc.register(email="login@test.com", name="Login", password="pass1234")
    user = await svc.login(email="login@test.com", password="pass1234")
    assert user.email == "login@test.com"


async def test_login_wrong_password_raises(session):
    svc = _service(session)
    await svc.register(email="wrongpw@test.com", name="Wrong", password="pass1234")
    with pytest.raises(UnauthorizedError):
        await svc.login(email="wrongpw@test.com", password="wrongpass")


async def test_login_unknown_email_raises(session):
    svc = _service(session)
    with pytest.raises(UnauthorizedError):
        await svc.login(email="ghost@test.com", password="pass1234")


async def test_login_inactive_user_raises(session):
    svc = _service(session)
    user = await svc.register(email="inactive@test.com", name="Inactive", password="pass1234")
    user.is_active = False
    await session.flush()

    with pytest.raises(UnauthorizedError):
        await svc.login(email="inactive@test.com", password="pass1234")


# ── update_name ───────────────────────────────────────────────────────────────

async def test_update_name(session):
    svc = _service(session)
    user = await svc.register(email="rename@test.com", name="Old Name", password="pass1234")
    updated = await svc.update_name(user.id, "New Name")
    assert updated.name == "New Name"


async def test_update_name_unknown_user_raises(session):
    svc = _service(session)
    with pytest.raises(NotFoundError):
        await svc.update_name(uuid.uuid4(), "Name")


# ── change_password ───────────────────────────────────────────────────────────

async def test_change_password_success(session):
    svc = _service(session)
    user = await svc.register(email="chpw@test.com", name="ChPw", password="oldpass12")
    await svc.change_password(user.id, "oldpass12", "newpass12")

    # Login with new password works
    logged = await svc.login(email="chpw@test.com", password="newpass12")
    assert logged.id == user.id


async def test_change_password_wrong_current_raises(session):
    svc = _service(session)
    user = await svc.register(email="chpw2@test.com", name="ChPw2", password="oldpass12")
    with pytest.raises(UnauthorizedError):
        await svc.change_password(user.id, "wrongcurrent", "newpass12")


async def test_change_password_unknown_user_raises(session):
    svc = _service(session)
    with pytest.raises(NotFoundError):
        await svc.change_password(uuid.uuid4(), "old", "new")
