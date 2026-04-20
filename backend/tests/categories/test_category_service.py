import pytest

from app.auth.auth_info import AuthInfo
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.categories.services.category_service import CategoryService
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService


@pytest.fixture
def category_service(session, auth_info):
    return CategoryService(CategoryRepository(session), auth_info)


async def _make_user(session, email: str):
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(email=email, name=email.split("@")[0], password="pass123")


async def test_list_categories_includes_global(session, auth_info):
    repo = CategoryRepository(session)
    from app.graphql.categories.models.category import Category

    global_cat = Category(
        name="Global Expense",
        category_kind=CategoryKind.EXPENSE,
        user_id=None,
    )
    session.add(global_cat)
    await session.flush()

    service = CategoryService(repo, auth_info)
    categories = await service.list_categories()

    assert any(c.name == "Global Expense" for c in categories)
    assert any(c.user_id is None for c in categories)


async def test_list_categories_includes_own_custom(category_service, auth_info):
    await category_service.create_category(
        name="My custom",
        category_kind=CategoryKind.EXPENSE,
        color="#ff0000",
    )

    categories = await category_service.list_categories()
    names = [c.name for c in categories]
    assert "My custom" in names


async def test_list_categories_excludes_other_user(session, auth_info):
    other = await _make_user(session, "other_cat@test.com")
    other_info = AuthInfo(user_id=other.id, email=other.email)
    other_service = CategoryService(CategoryRepository(session), other_info)

    await other_service.create_category(
        name="Other's private",
        category_kind=CategoryKind.INCOME,
    )

    my_service = CategoryService(CategoryRepository(session), auth_info)
    categories = await my_service.list_categories()
    names = [c.name for c in categories]
    assert "Other's private" not in names


async def test_create_category_defaults(category_service, auth_info):
    cat = await category_service.create_category(
        name="Side income",
        category_kind=CategoryKind.INCOME,
    )

    assert cat.name == "Side income"
    assert cat.category_kind == CategoryKind.INCOME
    assert cat.color == "#94a3b8"
    assert cat.user_id == auth_info.user_id


async def test_create_category_custom_color(category_service, auth_info):
    cat = await category_service.create_category(
        name="Transport",
        category_kind=CategoryKind.EXPENSE,
        color="#3b82f6",
    )

    assert cat.color == "#3b82f6"
    assert cat.user_id == auth_info.user_id


async def test_list_categories_ordered_by_kind_then_name(category_service):
    await category_service.create_category("Zebra", CategoryKind.EXPENSE)
    await category_service.create_category("Apple", CategoryKind.EXPENSE)
    await category_service.create_category("Mango", CategoryKind.INCOME)

    categories = await category_service.list_categories()
    user_cats = [c for c in categories if c.user_id is not None]

    income = [c for c in user_cats if c.category_kind == CategoryKind.INCOME]
    expense = [c for c in user_cats if c.category_kind == CategoryKind.EXPENSE]

    assert income[0].name == "Mango"
    assert expense[0].name == "Apple"
    assert expense[1].name == "Zebra"

async def test_create_category_name_es_defaults_to_none(category_service):
    cat = await category_service.create_category(
        name="Custom",
        category_kind=CategoryKind.EXPENSE,
    )
    assert cat.name_es is None


async def test_global_category_has_name_es(session, auth_info):
    from app.graphql.categories.models.category import Category

    cat = Category(
        name="Groceries",
        category_kind=CategoryKind.EXPENSE,
        user_id=None,
        name_es="Supermercado",
    )
    session.add(cat)
    await session.flush()

    service = CategoryService(CategoryRepository(session), auth_info)
    categories = await service.list_categories()
    groceries = next((c for c in categories if c.name == "Groceries"), None)

    assert groceries is not None
    assert groceries.name_es == "Supermercado"
