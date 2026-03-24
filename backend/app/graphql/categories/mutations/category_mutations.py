import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject

from app.graphql.categories.services.category_service import CategoryService
from app.graphql.categories.types.category_types import CategoryType, CreateCategoryInput


@strawberry.type
class CategoryMutations:
    @strawberry.mutation
    @inject
    async def create_category(
        self,
        input: CreateCategoryInput,
        service: Injected[CategoryService],
    ) -> CategoryType:
        category = await service.create_category(
            name=input.name,
            category_kind=input.category_kind,
            icon=input.icon,
            color=input.color,
        )
        return CategoryType.from_model(category)
