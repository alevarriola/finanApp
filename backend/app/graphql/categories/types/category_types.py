import uuid

import strawberry

from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.models.category import Category


@strawberry.type
class CategoryType:
    id: uuid.UUID
    name: str
    category_kind: CategoryKind
    icon: str
    color: str
    is_global: bool

    @classmethod
    def from_model(cls, model: Category) -> "CategoryType":
        return cls(
            id=uuid.UUID(str(model.id)),
            name=model.name,
            category_kind=model.category_kind,
            icon=model.icon,
            color=model.color,
            is_global=model.user_id is None,
        )


@strawberry.input
class CreateCategoryInput:
    name: str
    category_kind: CategoryKind
    icon: str = "📁"
    color: str = "#94a3b8"
