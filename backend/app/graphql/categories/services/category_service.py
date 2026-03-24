from app.auth.auth_info import AuthInfo
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.models.category import Category
from app.graphql.categories.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, repository: CategoryRepository, auth_info: AuthInfo) -> None:
        self.repository = repository
        self.auth_info = auth_info

    async def list_categories(self) -> list[Category]:
        return await self.repository.get_all(self.auth_info.user_id)

    async def create_category(
        self,
        name: str,
        category_kind: CategoryKind,
        color: str = "#94a3b8",
    ) -> Category:
        category = Category(
            name=name,
            category_kind=category_kind,
            color=color,
            user_id=self.auth_info.user_id,
        )
        return await self.repository.create(category)
