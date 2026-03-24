import pytest

from app.auth.auth_info import AuthInfo
from app.core.exceptions import DuplicateError, NotFoundError, UnauthorizedError
from app.graphql.invitations.enums import InvitationStatus
from app.graphql.invitations.repositories.invitation_repository import InvitationRepository
from app.graphql.invitations.services.invitation_service import InvitationService
from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.repositories.wallet_repository import WalletRepository
from app.graphql.wallets.services.wallet_service import WalletService
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService


async def _make_user(session, email: str):
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(email=email, name=email.split("@")[0], password="pass123")


def _wallet_service(session, user):
    info = AuthInfo(user_id=user.id, email=user.email)
    return WalletService(WalletRepository(session), info)


def _invitation_service(session, user):
    info = AuthInfo(user_id=user.id, email=user.email)
    return InvitationService(
        InvitationRepository(session),
        WalletRepository(session),
        UserRepository(session),
        info,
    )


@pytest.fixture
async def owner(test_user):
    return test_user


@pytest.fixture
async def other_user(session):
    return await _make_user(session, "other@test.com")


@pytest.fixture
async def wallet(session, owner):
    svc = _wallet_service(session, owner)
    return await svc.create_wallet(name="Shared Wallet", wallet_kind=WalletKind.CASH, currency="PYG", initial_balance=__import__("decimal").Decimal("0"))


# ── invite_user ────────────────────────────────────────────────────────────────

async def test_invite_user_creates_pending_invitation(session, owner, wallet):
    svc = _invitation_service(session, owner)
    inv = await svc.invite_user(wallet.id, "newuser@test.com", WalletRole.VIEWER)

    assert inv.wallet_id == wallet.id
    assert inv.invited_email == "newuser@test.com"
    assert inv.role == WalletRole.VIEWER
    assert inv.status == InvitationStatus.PENDING
    assert inv.invited_by_id == owner.id


async def test_invite_user_non_owner_raises_unauthorized(session, owner, wallet):
    editor = await _make_user(session, "editor@test.com")
    # Add editor as EDITOR member
    from app.graphql.wallets.models.wallet_member import WalletMember
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=editor.id, role=WalletRole.EDITOR)
    )
    svc = _invitation_service(session, editor)
    with pytest.raises(UnauthorizedError):
        await svc.invite_user(wallet.id, "target@test.com", WalletRole.VIEWER)


async def test_invite_self_raises_duplicate(session, owner, wallet):
    svc = _invitation_service(session, owner)
    with pytest.raises(DuplicateError):
        await svc.invite_user(wallet.id, owner.email, WalletRole.VIEWER)


async def test_invite_existing_member_raises_duplicate(session, owner, wallet, other_user):
    # Add other_user as a member first
    from app.graphql.wallets.models.wallet_member import WalletMember
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=other_user.id, role=WalletRole.VIEWER)
    )
    svc = _invitation_service(session, owner)
    with pytest.raises(DuplicateError):
        await svc.invite_user(wallet.id, other_user.email, WalletRole.VIEWER)


async def test_invite_duplicate_pending_raises_duplicate(session, owner, wallet):
    svc = _invitation_service(session, owner)
    await svc.invite_user(wallet.id, "newuser@test.com", WalletRole.VIEWER)
    with pytest.raises(DuplicateError):
        await svc.invite_user(wallet.id, "newuser@test.com", WalletRole.EDITOR)


async def test_invite_normalizes_email(session, owner, wallet):
    svc = _invitation_service(session, owner)
    inv = await svc.invite_user(wallet.id, "  NewUser@Test.COM  ", WalletRole.VIEWER)
    assert inv.invited_email == "newuser@test.com"


# ── list_received ──────────────────────────────────────────────────────────────

async def test_list_received_returns_pending_for_email(session, owner, wallet, other_user):
    owner_svc = _invitation_service(session, owner)
    await owner_svc.invite_user(wallet.id, other_user.email, WalletRole.VIEWER)

    other_svc = _invitation_service(session, other_user)
    received = await other_svc.list_received()

    assert len(received) == 1
    assert received[0].invited_email == other_user.email
    assert received[0].status == InvitationStatus.PENDING


async def test_list_received_empty_when_no_invitations(session, other_user):
    svc = _invitation_service(session, other_user)
    assert await svc.list_received() == []


# ── accept_invitation ─────────────────────────────────────────────────────────

async def test_accept_invitation_adds_member(session, owner, wallet, other_user):
    owner_svc = _invitation_service(session, owner)
    inv = await owner_svc.invite_user(wallet.id, other_user.email, WalletRole.VIEWER)

    other_svc = _invitation_service(session, other_user)
    accepted = await other_svc.accept_invitation(inv.id)

    assert accepted.status == InvitationStatus.ACCEPTED

    member = await WalletRepository(session).get_member(wallet.id, other_user.id)
    assert member is not None
    assert member.role == WalletRole.VIEWER


async def test_accept_invitation_wrong_user_raises_not_found(session, owner, wallet):
    owner_svc = _invitation_service(session, owner)
    inv = await owner_svc.invite_user(wallet.id, "stranger@test.com", WalletRole.VIEWER)

    # other_user tries to accept an invitation meant for stranger
    wrong_user = await _make_user(session, "wrong@test.com")
    svc = _invitation_service(session, wrong_user)
    with pytest.raises(NotFoundError):
        await svc.accept_invitation(inv.id)


async def test_accept_already_accepted_raises_unauthorized(session, owner, wallet, other_user):
    owner_svc = _invitation_service(session, owner)
    inv = await owner_svc.invite_user(wallet.id, other_user.email, WalletRole.VIEWER)

    other_svc = _invitation_service(session, other_user)
    await other_svc.accept_invitation(inv.id)

    with pytest.raises(UnauthorizedError):
        await other_svc.accept_invitation(inv.id)


# ── reject_invitation ─────────────────────────────────────────────────────────

async def test_reject_invitation_sets_rejected(session, owner, wallet, other_user):
    owner_svc = _invitation_service(session, owner)
    inv = await owner_svc.invite_user(wallet.id, other_user.email, WalletRole.VIEWER)

    other_svc = _invitation_service(session, other_user)
    rejected = await other_svc.reject_invitation(inv.id)

    assert rejected.status == InvitationStatus.REJECTED

    # Should not be a member
    member = await WalletRepository(session).get_member(wallet.id, other_user.id)
    assert member is None


async def test_reject_invitation_wrong_user_raises_not_found(session, owner, wallet):
    owner_svc = _invitation_service(session, owner)
    inv = await owner_svc.invite_user(wallet.id, "stranger@test.com", WalletRole.VIEWER)

    wrong_user = await _make_user(session, "wrong2@test.com")
    svc = _invitation_service(session, wrong_user)
    with pytest.raises(NotFoundError):
        await svc.reject_invitation(inv.id)


# ── cancel_invitation ─────────────────────────────────────────────────────────

async def test_cancel_invitation_sets_cancelled(session, owner, wallet):
    svc = _invitation_service(session, owner)
    inv = await svc.invite_user(wallet.id, "cancel@test.com", WalletRole.VIEWER)

    result = await svc.cancel_invitation(inv.id)
    assert result is True


async def test_cancel_invitation_non_owner_raises_unauthorized(session, owner, wallet):
    from app.graphql.wallets.models.wallet_member import WalletMember
    editor = await _make_user(session, "editor2@test.com")
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=editor.id, role=WalletRole.EDITOR)
    )

    owner_svc = _invitation_service(session, owner)
    inv = await owner_svc.invite_user(wallet.id, "cancel2@test.com", WalletRole.VIEWER)

    editor_svc = _invitation_service(session, editor)
    with pytest.raises(UnauthorizedError):
        await editor_svc.cancel_invitation(inv.id)


async def test_cancel_accepted_invitation_raises_unauthorized(session, owner, wallet, other_user):
    owner_svc = _invitation_service(session, owner)
    inv = await owner_svc.invite_user(wallet.id, other_user.email, WalletRole.VIEWER)

    other_svc = _invitation_service(session, other_user)
    await other_svc.accept_invitation(inv.id)

    with pytest.raises(UnauthorizedError):
        await owner_svc.cancel_invitation(inv.id)


# ── list_sent_for_wallet ──────────────────────────────────────────────────────

async def test_list_sent_returns_all_statuses(session, owner, wallet, other_user):
    svc = _invitation_service(session, owner)
    inv = await svc.invite_user(wallet.id, other_user.email, WalletRole.VIEWER)
    await svc.invite_user(wallet.id, "another@test.com", WalletRole.EDITOR)

    sent = await svc.list_sent_for_wallet(wallet.id)
    assert len(sent) == 2
    ids = {i.id for i in sent}
    assert inv.id in ids


async def test_list_sent_non_owner_raises_unauthorized(session, owner, wallet, other_user):
    from app.graphql.wallets.models.wallet_member import WalletMember
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=other_user.id, role=WalletRole.VIEWER)
    )
    svc = _invitation_service(session, other_user)
    with pytest.raises(UnauthorizedError):
        await svc.list_sent_for_wallet(wallet.id)
