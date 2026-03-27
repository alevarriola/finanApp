import uuid

import strawberry

from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.models.category import Category


@strawberry.type
class CategoryType:
    id: uuid.UUID
    name: str
    name_es: str | None
    category_kind: CategoryKind
    color: str
    is_global: bool

    @classmethod
    def from_model(cls, model: Category) -> "CategoryType":
        return cls(
            id=uuid.UUID(str(model.id)),
            name=model.name,
            name_es=model.name_es,
            category_kind=model.category_kind,
            color=model.color,
            is_global=model.user_id is None,
        )


@strawberry.input
class CreateCategoryInput:
    name: str
    category_kind: CategoryKind
    color: str = "#94a3b8"
