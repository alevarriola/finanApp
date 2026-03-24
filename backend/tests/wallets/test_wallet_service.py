import uuid
from decimal import Decimal

import pytest

from app.auth.auth_info import AuthInfo
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService
from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.repositories.wallet_repository import WalletRepository
from app.graphql.wallets.services.wallet_service import WalletService


@pytest.fixture
def wallet_service(session, auth_info):
    return WalletService(WalletRepository(session), auth_info)


async def _make_user(session, email: str):
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(email=email, name=email.split("@")[0], password="pass123")


async def _make_service(session, user):
    info = AuthInfo(user_id=user.id, email=user.email)
    return WalletService(WalletRepository(session), info)


async def test_create_wallet(wallet_service, auth_info):
    wallet = await wallet_service.create_wallet(
        name="Savings",
        wallet_kind=WalletKind.BANK,
        currency="PYG",
        initial_balance=Decimal("500000"),
    )

    assert wallet.name == "Savings"
    assert wallet.wallet_kind == WalletKind.BANK
    assert wallet.currency == "PYG"
    assert wallet.initial_balance == Decimal("500000")
    assert wallet.owner_id == auth_info.user_id
    assert wallet.is_archived is False
    assert len(wallet.members) == 1
    assert wallet.members[0].role == WalletRole.OWNER
    assert wallet.members[0].user_id == auth_info.user_id


async def test_get_user_wallets_returns_own(wallet_service, auth_info):
    await wallet_service.create_wallet("Cash", WalletKind.CASH, "PYG", Decimal("0"))
    await wallet_service.create_wallet("Bank", WalletKind.BANK, "USD", Decimal("1000"))

    wallets = await wallet_service.get_user_wallets()
    assert len(wallets) == 2


async def test_get_user_wallets_excludes_other_users(session, wallet_service):
    other = await _make_user(session, "other@test.com")
    other_service = await _make_service(session, other)
    await other_service.create_wallet("Other's wallet", WalletKind.CASH, "PYG", Decimal("0"))

    wallets = await wallet_service.get_user_wallets()
    assert len(wallets) == 0


async def test_get_by_id_success(wallet_service):
    created = await wallet_service.create_wallet("My wallet", WalletKind.CASH, "PYG", Decimal("0"))
    found = await wallet_service.get_by_id(created.id)
    assert found.id == created.id


async def test_get_by_id_not_found_raises(wallet_service):
    with pytest.raises(NotFoundError):
        await wallet_service.get_by_id(uuid.uuid4())


async def test_get_by_id_not_member_raises(session, wallet_service):
    other = await _make_user(session, "stranger@test.com")
    other_service = await _make_service(session, other)
    other_wallet = await other_service.create_wallet("Private", WalletKind.CASH, "PYG", Decimal("0"))

    with pytest.raises(NotFoundError):
        await wallet_service.get_by_id(other_wallet.id)


async def test_update_wallet_owner(wallet_service):
    wallet = await wallet_service.create_wallet("Old name", WalletKind.CASH, "PYG", Decimal("0"))
    updated = await wallet_service.update_wallet(wallet.id, name="New name", currency="USD")

    assert updated.name == "New name"
    assert updated.currency == "USD"


async def test_update_wallet_viewer_raises(session, wallet_service, auth_info):
    wallet = await wallet_service.create_wallet("My wallet", WalletKind.CASH, "PYG", Decimal("0"))

    viewer = await _make_user(session, "viewer@test.com")
    from app.graphql.wallets.models.wallet_member import WalletMember
    repo = WalletRepository(session)
    await repo.add_member(WalletMember(
        wallet_id=wallet.id,
        user_id=viewer.id,
        role=WalletRole.VIEWER,
    ))

    viewer_service = await _make_service(session, viewer)
    with pytest.raises(UnauthorizedError):
        await viewer_service.update_wallet(wallet.id, name="Hacked")


async def test_archive_wallet_owner(wallet_service):
    wallet = await wallet_service.create_wallet("To archive", WalletKind.CASH, "PYG", Decimal("0"))
    archived = await wallet_service.archive_wallet(wallet.id)
    assert archived.is_archived is True


async def test_archive_wallet_archived_excluded_from_list(wallet_service):
    wallet = await wallet_service.create_wallet("Active", WalletKind.CASH, "PYG", Decimal("0"))
    await wallet_service.archive_wallet(wallet.id)

    wallets = await wallet_service.get_user_wallets()
    assert all(not w.is_archived for w in wallets)


async def test_archive_wallet_non_owner_raises(session, wallet_service):
    wallet = await wallet_service.create_wallet("My wallet", WalletKind.CASH, "PYG", Decimal("0"))

    editor = await _make_user(session, "editor@test.com")
    repo = WalletRepository(session)
    from app.graphql.wallets.models.wallet_member import WalletMember
    await repo.add_member(WalletMember(
        wallet_id=wallet.id,
        user_id=editor.id,
        role=WalletRole.EDITOR,
    ))

    editor_service = await _make_service(session, editor)
    with pytest.raises(UnauthorizedError):
        await editor_service.archive_wallet(wallet.id)
