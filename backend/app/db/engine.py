from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings


def create_engine(settings: Settings):
    return create_async_engine(
        settings.database_url,
        echo=settings.environment == "dev",
    )


def create_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    engine = create_engine(settings)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        async with session.begin():
            yield session
