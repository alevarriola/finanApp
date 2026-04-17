from decimal import Decimal

import pytest

from app.core.config import get_settings
from app.graphql.ai_chat.services.ai_chat_service import AiChatService
from app.graphql.ai_chat.types.ai_chat_types import ParsedTransaction
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.categories.services.category_service import CategoryService
from app.graphql.schemas.schema import Mutation
from app.graphql.wallets.enums import WalletKind
from app.graphql.wallets.repositories.wallet_repository import WalletRepository
from app.graphql.wallets.services.wallet_service import WalletService


@pytest.fixture
def ai_chat_service(session, auth_info):
    return AiChatService(
        wallet_repository=WalletRepository(session),
        category_repository=CategoryRepository(session),
        auth_info=auth_info,
        settings=get_settings(),
    )


@pytest.fixture
def wallet_service(session, auth_info):
    return WalletService(WalletRepository(session), auth_info)


@pytest.fixture
def category_service(session, auth_info):
    return CategoryService(CategoryRepository(session), auth_info)


async def test_parse_transaction_rejects_blank_text(ai_chat_service):
    with pytest.raises(ValueError, match="cannot be empty"):
        await ai_chat_service.parse_transaction(" \n\t ")


async def test_parse_transaction_returns_sanitized_stub(ai_chat_service, wallet_service) -> None:
    await wallet_service.create_wallet(
        name="Cash Wallet",
        wallet_kind=WalletKind.CASH,
        currency="USD",
        initial_balance=Decimal("0"),
    )

    parsed = await ai_chat_service.parse_transaction("Gast\x00e   100 usd\n en cena")

    assert isinstance(parsed, ParsedTransaction)
    assert parsed.raw_text == "Gaste 100 usd en cena"
    assert parsed.description == "Gaste 100 usd en cena"
    assert parsed.currency == "USD"
    assert parsed.requires_confirmation is True
    assert parsed.confidence == 0.0


async def test_context_only_includes_current_user_entities(
    ai_chat_service,
    wallet_service,
    category_service,
) -> None:
    await wallet_service.create_wallet(
        name="Itaú",
        wallet_kind=WalletKind.CREDIT,
        currency="PYG",
        initial_balance=Decimal("0"),
    )
    await category_service.create_category(
        name="Restaurante",
        category_kind=CategoryKind.EXPENSE,
    )

    wallets = await ai_chat_service.get_wallet_context()
    categories = await ai_chat_service.get_category_context()

    assert len(wallets) == 1
    assert wallets[0].name == "Itaú"
    assert wallets[0].currency == "PYG"
    assert len(categories) == 1
    assert categories[0].name == "Restaurante"


def test_settings_expose_ai_defaults() -> None:
    settings = get_settings()

    assert settings.ai_primary_model == "gpt-4.1-mini"
    assert settings.ai_fallback_model == "gpt-4o-mini"
    assert hasattr(settings, "openai_api_key")


def test_schema_registers_parse_transaction_mutation() -> None:
    field_names = {field.python_name for field in Mutation.__strawberry_definition__.fields}

    assert "parse_transaction" in field_names
