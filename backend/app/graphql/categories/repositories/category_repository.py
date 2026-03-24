import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.categories.models.category import Category


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, user_id: uuid.UUID) -> list[Category]:
        stmt = (
            select(Category)
            .where(or_(Category.user_id == user_id, Category.user_id.is_(None)))
            .order_by(Category.category_kind, Category.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_ids(self, category_ids: list[uuid.UUID]) -> list[Category]:
        if not category_ids:
            return []
        stmt = select(Category).where(Category.id.in_(category_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def create(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        return category
