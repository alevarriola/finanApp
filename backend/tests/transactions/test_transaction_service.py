import datetime
import uuid
from decimal import Decimal

import pytest

from app.auth.auth_info import AuthInfo
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.models.category import Category
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.transactions.enums import TransactionKind
from app.graphql.transactions.repositories.transaction_repository import TransactionRepository
from app.graphql.transactions.services.transaction_service import TransactionService
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService
from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.models.wallet_member import WalletMember
from app.graphql.wallets.repositories.wallet_repository import WalletRepository
from app.graphql.wallets.services.wallet_service import WalletService

TODAY = datetime.date.today()


async def _make_user(session, email: str):
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(email=email, name=email.split("@")[0], password="pass123")


def _wallet_service(session, user):
    info = AuthInfo(user_id=user.id, email=user.email)
    return WalletService(WalletRepository(session), info)


def _transaction_service(session, user):
    info = AuthInfo(user_id=user.id, email=user.email)
    return TransactionService(
        TransactionRepository(session),
        WalletRepository(session),
        info,
    )


@pytest.fixture
async def owner(test_user):
    return test_user


@pytest.fixture
async def wallet(session, owner):
    svc = _wallet_service(session, owner)
    return await svc.create_wallet("Test Wallet", WalletKind.BANK, "USD", Decimal("1000"))


@pytest.fixture
def tx_service(session, owner):
    return _transaction_service(session, owner)


# ── create ────────────────────────────────────────────────────────────────────


async def test_create_transaction_basic(tx_service, wallet):
    tx = await tx_service.create_transaction(
        wallet_id=wallet.id,
        amount=Decimal("50.00"),
        transaction_kind=TransactionKind.EXPENSE,
        date=TODAY,
    )

    assert tx.amount == Decimal("50.00")
    assert tx.transaction_kind == TransactionKind.EXPENSE
    assert tx.date == TODAY
    assert tx.description is None
    assert tx.category_id is None


async def test_create_transaction_with_description(tx_service, wallet):
    tx = await tx_service.create_transaction(
        wallet_id=wallet.id,
        amount=Decimal("200.00"),
        transaction_kind=TransactionKind.INCOME,
        date=TODAY,
        description="Freelance payment",
    )
    assert tx.description == "Freelance payment"


async def test_create_transaction_with_category(session, tx_service, wallet, auth_info):
    cat = Category(name="Food", category_kind=CategoryKind.EXPENSE, user_id=auth_info.user_id)
    session.add(cat)
    await session.flush()

    tx = await tx_service.create_transaction(
        wallet_id=wallet.id,
        amount=Decimal("30.00"),
        transaction_kind=TransactionKind.EXPENSE,
        date=TODAY,
        category_id=cat.id,
    )
    assert tx.category_id == cat.id


async def test_create_transaction_wrong_wallet_raises(tx_service):
    with pytest.raises(NotFoundError):
        await tx_service.create_transaction(
            wallet_id=uuid.uuid4(),
            amount=Decimal("10"),
            transaction_kind=TransactionKind.EXPENSE,
            date=TODAY,
        )


async def test_create_transaction_viewer_raises(session, wallet, owner):
    viewer_user = await _make_user(session, "viewer_tx@test.com")
    repo = WalletRepository(session)
    await repo.add_member(WalletMember(
        wallet_id=wallet.id,
        user_id=viewer_user.id,
        role=WalletRole.VIEWER,
    ))
    viewer_svc = _transaction_service(session, viewer_user)

    with pytest.raises(UnauthorizedError):
        await viewer_svc.create_transaction(
            wallet_id=wallet.id,
            amount=Decimal("10"),
            transaction_kind=TransactionKind.EXPENSE,
            date=TODAY,
        )


# ── list ──────────────────────────────────────────────────────────────────────


async def test_list_transactions_returns_wallet_txs(tx_service, wallet):
    await tx_service.create_transaction(wallet.id, Decimal("10"), TransactionKind.EXPENSE, TODAY)
    await tx_service.create_transaction(wallet.id, Decimal("20"), TransactionKind.INCOME, TODAY)

    txs = await tx_service.list_transactions(wallet.id)
    assert len(txs) == 2


async def test_list_transactions_filter_by_kind(tx_service, wallet):
    await tx_service.create_transaction(wallet.id, Decimal("10"), TransactionKind.EXPENSE, TODAY)
    await tx_service.create_transaction(wallet.id, Decimal("50"), TransactionKind.INCOME, TODAY)

    expenses = await tx_service.list_transactions(wallet.id, transaction_kind=TransactionKind.EXPENSE)
    assert len(expenses) == 1
    assert expenses[0].transaction_kind == TransactionKind.EXPENSE


async def test_list_transactions_filter_by_date_range(tx_service, wallet):
    yesterday = TODAY - datetime.timedelta(days=1)
    last_week = TODAY - datetime.timedelta(days=7)

    await tx_service.create_transaction(wallet.id, Decimal("10"), TransactionKind.EXPENSE, last_week)
    await tx_service.create_transaction(wallet.id, Decimal("20"), TransactionKind.EXPENSE, yesterday)
    await tx_service.create_transaction(wallet.id, Decimal("30"), TransactionKind.EXPENSE, TODAY)

    txs = await tx_service.list_transactions(wallet.id, date_from=yesterday, date_to=TODAY)
    assert len(txs) == 2
    amounts = {t.amount for t in txs}
    assert amounts == {Decimal("20"), Decimal("30")}


async def test_list_transactions_other_wallet_raises(session, wallet, owner):
    other_user = await _make_user(session, "other_tx@test.com")
    stranger_svc = _transaction_service(session, other_user)

    with pytest.raises(NotFoundError):
        await stranger_svc.list_transactions(wallet.id)


# ── update ────────────────────────────────────────────────────────────────────


async def test_update_transaction_amount(tx_service, wallet):
    tx = await tx_service.create_transaction(
        wallet.id, Decimal("100"), TransactionKind.EXPENSE, TODAY
    )
    updated = await tx_service.update_transaction(tx.id, amount=Decimal("150"))
    assert updated.amount == Decimal("150")


async def test_update_transaction_description(tx_service, wallet):
    tx = await tx_service.create_transaction(
        wallet.id, Decimal("50"), TransactionKind.INCOME, TODAY
    )
    updated = await tx_service.update_transaction(tx.id, description="Updated note")
    assert updated.description == "Updated note"


async def test_update_transaction_not_found_raises(tx_service):
    with pytest.raises(NotFoundError):
        await tx_service.update_transaction(uuid.uuid4(), amount=Decimal("99"))


# ── delete ────────────────────────────────────────────────────────────────────


async def test_delete_transaction(tx_service, wallet):
    tx = await tx_service.create_transaction(
        wallet.id, Decimal("25"), TransactionKind.EXPENSE, TODAY
    )
    await tx_service.delete_transaction(tx.id)

    txs = await tx_service.list_transactions(wallet.id)
    ids = [t.id for t in txs]
    assert tx.id not in ids


async def test_delete_transaction_not_found_raises(tx_service):
    with pytest.raises(NotFoundError):
        await tx_service.delete_transaction(uuid.uuid4())


async def test_delete_transaction_viewer_raises(session, wallet, owner):
    owner_svc = _transaction_service(session, owner)
    tx = await owner_svc.create_transaction(
        wallet.id, Decimal("10"), TransactionKind.EXPENSE, TODAY
    )

    viewer_user = await _make_user(session, "viewer_del@test.com")
    repo = WalletRepository(session)
    await repo.add_member(WalletMember(
        wallet_id=wallet.id,
        user_id=viewer_user.id,
        role=WalletRole.VIEWER,
    ))
    viewer_svc = _transaction_service(session, viewer_user)

    with pytest.raises(UnauthorizedError):
        await viewer_svc.delete_transaction(tx.id)


# ── balance ───────────────────────────────────────────────────────────────────


async def test_get_wallet_balance_no_transactions(tx_service, wallet):
    balance = await tx_service.get_wallet_balance(wallet.id, wallet.initial_balance)
    assert balance == wallet.initial_balance


async def test_get_wallet_balance_with_income(tx_service, wallet):
    await tx_service.create_transaction(
        wallet.id, Decimal("500"), TransactionKind.INCOME, TODAY
    )
    balance = await tx_service.get_wallet_balance(wallet.id, wallet.initial_balance)
    assert balance == Decimal("1500.00")


async def test_get_wallet_balance_with_expense(tx_service, wallet):
    await tx_service.create_transaction(
        wallet.id, Decimal("200"), TransactionKind.EXPENSE, TODAY
    )
    balance = await tx_service.get_wallet_balance(wallet.id, wallet.initial_balance)
    assert balance == Decimal("800.00")


async def test_get_wallet_balance_mixed(tx_service, wallet):
    await tx_service.create_transaction(wallet.id, Decimal("300"), TransactionKind.INCOME, TODAY)
    await tx_service.create_transaction(wallet.id, Decimal("100"), TransactionKind.EXPENSE, TODAY)
    balance = await tx_service.get_wallet_balance(wallet.id, wallet.initial_balance)
    assert balance == Decimal("1200.00")


async def test_get_wallet_balances_batch(session, owner, wallet):
    svc = _transaction_service(session, owner)
    wallet_svc = _wallet_service(session, owner)

    wallet2 = await wallet_svc.create_wallet("Second", WalletKind.CASH, "USD", Decimal("500"))

    await svc.create_transaction(wallet.id, Decimal("100"), TransactionKind.INCOME, TODAY)
    await svc.create_transaction(wallet2.id, Decimal("50"), TransactionKind.EXPENSE, TODAY)

    wallets = await wallet_svc.get_user_wallets()
    balances = await svc.get_wallet_balances(wallets)

    w1_id = uuid.UUID(str(wallet.id))
    w2_id = uuid.UUID(str(wallet2.id))

    assert balances[w1_id] == Decimal("1100.00")
    assert balances[w2_id] == Decimal("450.00")
