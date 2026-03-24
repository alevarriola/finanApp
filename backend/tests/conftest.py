import asyncpg
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.auth.auth_info import AuthInfo
from app.core.config import get_settings
from app.db.base import Base
from app.graphql.users.models.user import User
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService
from app.graphql.categories.models.category import Category
from app.graphql.transactions.models.transaction import Transaction
from app.graphql.wallets.models.wallet import Wallet
from app.graphql.wallets.models.wallet_member import WalletMember

_ = (User, Wallet, WalletMember, Category, Transaction)

_settings = get_settings()
TEST_DB_URL = _settings.database_url.rsplit("/", 1)[0] + "/finanapp_test"
_RAW_PG_URL = _settings.database_url.replace("+asyncpg", "").rsplit("/", 1)[0] + "/postgres"


@pytest.fixture(scope="session", autouse=True)
async def create_test_db():
    conn = await asyncpg.connect(_RAW_PG_URL)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'finanapp_test'"
        )
        if not exists:
            await conn.execute("CREATE DATABASE finanapp_test")
    finally:
        await conn.close()


@pytest.fixture(scope="session")
async def engine(create_test_db):
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def session(engine):
    async with engine.connect() as conn:
        await conn.begin()
        sess = AsyncSession(bind=conn, join_transaction_mode="create_savepoint")
        yield sess
        await sess.close()
        await conn.rollback()


@pytest.fixture
async def test_user(session) -> User:
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(
        email="user@test.com",
        name="Test User",
        password="password123",
    )


@pytest.fixture
def auth_info(test_user: User) -> AuthInfo:
    return AuthInfo(user_id=test_user.id, email=test_user.email)
