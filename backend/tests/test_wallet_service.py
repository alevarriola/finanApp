import uuid
from decimal import Decimal

import pytest

from app.auth.auth_info import AuthInfo
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.models.wallet_member import WalletMember
from app.graphql.wallets.repositories.wallet_repository import WalletRepository
from app.graphql.wallets.services.wallet_service import WalletService
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService


async def _make_user(session, email: str):
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(email=email, name=email.split("@")[0], password="pass123")


def _wallet_service(session, user):
    return WalletService(WalletRepository(session), AuthInfo(user_id=user.id, email=user.email))


@pytest.fixture
async def owner(test_user):
    return test_user


@pytest.fixture
async def wallet(session, owner):
    svc = _wallet_service(session, owner)
    return await svc.create_wallet(name="Test Wallet", wallet_kind=WalletKind.CASH, currency="PYG", initial_balance=Decimal("0"))


# ── create_wallet ─────────────────────────────────────────────────────────────

async def test_create_wallet(session, owner):
    svc = _wallet_service(session, owner)
    wallet = await svc.create_wallet(name="My Wallet", wallet_kind=WalletKind.BANK, currency="USD", initial_balance=Decimal("1000"))

    assert wallet.name == "My Wallet"
    assert wallet.wallet_kind == WalletKind.BANK
    assert wallet.currency == "USD"
    assert wallet.initial_balance == Decimal("1000")


async def test_create_wallet_adds_owner_member(session, owner):
    svc = _wallet_service(session, owner)
    wallet = await svc.create_wallet(name="W", wallet_kind=WalletKind.CASH, currency="PYG", initial_balance=Decimal("0"))

    member = await WalletRepository(session).get_member(wallet.id, owner.id)
    assert member is not None
    assert member.role == WalletRole.OWNER


# ── get_user_wallets ──────────────────────────────────────────────────────────

async def test_get_user_wallets(session, owner, wallet):
    svc = _wallet_service(session, owner)
    wallets = await svc.get_user_wallets()
    assert len(wallets) >= 1
    assert any(w.id == wallet.id for w in wallets)


async def test_get_user_wallets_excludes_other_users(session, owner, wallet):
    other = await _make_user(session, "other@test.com")
    svc = _wallet_service(session, other)
    wallets = await svc.get_user_wallets()
    assert not any(w.id == wallet.id for w in wallets)


# ── update_wallet ─────────────────────────────────────────────────────────────

async def test_update_wallet_name(session, owner, wallet):
    svc = _wallet_service(session, owner)
    updated = await svc.update_wallet(wallet.id, name="New Name")
    assert updated.name == "New Name"


async def test_update_wallet_viewer_raises(session, owner, wallet):
    viewer = await _make_user(session, "viewer@test.com")
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=viewer.id, role=WalletRole.VIEWER)
    )
    svc = _wallet_service(session, viewer)
    with pytest.raises(UnauthorizedError):
        await svc.update_wallet(wallet.id, name="Nope")


# ── leave_wallet ──────────────────────────────────────────────────────────────

async def test_leave_wallet(session, owner, wallet):
    member_user = await _make_user(session, "member@test.com")
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=member_user.id, role=WalletRole.EDITOR)
    )

    svc = _wallet_service(session, member_user)
    await svc.leave_wallet(wallet.id)

    left = await WalletRepository(session).get_member(wallet.id, member_user.id)
    assert left is None


async def test_leave_wallet_owner_raises(session, owner, wallet):
    svc = _wallet_service(session, owner)
    with pytest.raises(UnauthorizedError):
        await svc.leave_wallet(wallet.id)


async def test_leave_wallet_not_member_raises(session, wallet):
    stranger = await _make_user(session, "stranger@test.com")
    svc = _wallet_service(session, stranger)
    with pytest.raises(NotFoundError):
        await svc.leave_wallet(wallet.id)


# ── archive_wallet ────────────────────────────────────────────────────────────

async def test_archive_wallet(session, owner, wallet):
    svc = _wallet_service(session, owner)
    archived = await svc.archive_wallet(wallet.id)
    assert archived.is_archived is True


async def test_archive_wallet_non_owner_raises(session, owner, wallet):
    editor = await _make_user(session, "editor@test.com")
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=editor.id, role=WalletRole.EDITOR)
    )
    svc = _wallet_service(session, editor)
    with pytest.raises(UnauthorizedError):
        await svc.archive_wallet(wallet.id)


# ── get_wallet_members ────────────────────────────────────────────────────────

async def test_get_wallet_members(session, owner, wallet):
    svc = _wallet_service(session, owner)
    members = await svc.get_wallet_members(wallet.id)
    assert len(members) == 1
