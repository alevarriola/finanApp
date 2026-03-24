import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject

from app.graphql.categories.services.category_service import CategoryService
from app.graphql.categories.types.category_types import CategoryType


@strawberry.type
class CategoryQueries:
    @strawberry.field
    @inject
    async def categories(self, service: Injected[CategoryService]) -> list[CategoryType]:
        categories = await service.list_categories()
        return [CategoryType.from_model(c) for c in categories]
