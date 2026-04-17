from decimal import Decimal

import pytest

from app.core.config import get_settings
from app.graphql.ai_chat.agents.transaction_parser_agent import TransactionParserAgent
from app.graphql.ai_chat.services.ai_chat_service import AiChatService
from app.graphql.ai_chat.types.ai_chat_types import ParsedTransaction
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.categories.services.category_service import CategoryService
from app.graphql.schemas.schema import Mutation
from app.graphql.transactions.enums import TransactionKind
from app.graphql.wallets.enums import WalletKind
from app.graphql.wallets.repositories.wallet_repository import WalletRepository
from app.graphql.wallets.services.wallet_service import WalletService


@pytest.fixture
def ai_chat_service(session, auth_info, tmp_path):
    allowlist = tmp_path / "ai_chat_allowed_emails.txt"
    allowlist.write_text(f"{auth_info.email}\n", encoding="utf-8")
    settings = get_settings().model_copy(
        update={"ai_chat_allowlist_path": str(allowlist)}
    )
    return AiChatService(
        wallet_repository=WalletRepository(session),
        category_repository=CategoryRepository(session),
        transaction_parser_agent=TransactionParserAgent(settings),
        auth_info=auth_info,
        settings=settings,
    )


@pytest.fixture
def wallet_service(session, auth_info):
    return WalletService(WalletRepository(session), auth_info)


@pytest.fixture
def category_service(session, auth_info):
    return CategoryService(CategoryRepository(session), auth_info)


def _service_with_settings(session, auth_info, settings):
    return AiChatService(
        wallet_repository=WalletRepository(session),
        category_repository=CategoryRepository(session),
        transaction_parser_agent=TransactionParserAgent(settings),
        auth_info=auth_info,
        settings=settings,
    )


async def test_parse_transaction_rejects_blank_text(ai_chat_service):
    with pytest.raises(ValueError, match="cannot be empty"):
        await ai_chat_service.parse_transaction(" \n\t ")


async def test_parse_transaction_uses_agent_output(ai_chat_service, wallet_service) -> None:
    await wallet_service.create_wallet(
        name="Cash Wallet",
        wallet_kind=WalletKind.CASH,
        currency="USD",
        initial_balance=Decimal("0"),
    )

    captured: dict[str, str] = {}

    async def fake_run(user_prompt: str, instructions: str) -> ParsedTransaction:
        captured["user_prompt"] = user_prompt
        captured["instructions"] = instructions
        return ParsedTransaction(
            raw_text="ignored by service",
            wallet_hint="cash wallet",
            amount=Decimal("100000"),
            currency=None,
            transaction_kind=TransactionKind.EXPENSE,
            category_hint="food",
            description="cena familiar",
            confidence=0.91,
        )

    ai_chat_service.transaction_parser_agent.run = fake_run  # type: ignore[method-assign]

    parsed = await ai_chat_service.parse_transaction("Gast\x00e   100k\n en cena")

    assert isinstance(parsed, ParsedTransaction)
    assert parsed.raw_text == "Gaste 100k en cena"
    assert parsed.description == "cena familiar"
    assert parsed.currency == "USD"
    assert parsed.requires_confirmation is True
    assert parsed.confidence == 0.91
    assert "Normalized user text:" in captured["user_prompt"]
    assert "100000" in captured["user_prompt"]
    assert "Cash Wallet" in captured["instructions"]


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


@pytest.fixture
def parser_agent() -> TransactionParserAgent:
    return TransactionParserAgent(get_settings())


def test_parser_agent_normalizes_colloquial_amounts(parser_agent: TransactionParserAgent) -> None:
    normalized = parser_agent.normalize_colloquial_amounts("Gaste 100k y 1 palo en total")

    assert normalized == "Gaste 100000 y 1000000 en total"


async def test_parser_agent_falls_back_when_primary_fails(
    parser_agent: TransactionParserAgent,
) -> None:
    async def fail_primary(user_prompt: str, instructions: str) -> ParsedTransaction:
        raise RuntimeError("primary failed")

    async def use_fallback(user_prompt: str, instructions: str) -> ParsedTransaction:
        return ParsedTransaction(
            raw_text=user_prompt,
            amount=Decimal("25000"),
            transaction_kind=TransactionKind.EXPENSE,
            confidence=0.7,
        )

    parser_agent._run_primary = fail_primary  # type: ignore[method-assign]
    parser_agent._run_fallback = use_fallback  # type: ignore[method-assign]

    parsed = await parser_agent.run("prompt", "instructions")

    assert parsed.amount == Decimal("25000")
    assert parsed.transaction_kind == TransactionKind.EXPENSE


async def test_ai_chat_denies_user_not_in_allowlist(session, auth_info) -> None:
    settings = get_settings().model_copy(
        update={
            "ai_chat_allowlist_path": "tests/fixtures/nonexistent_allowlist.txt",
            "ai_chat_beta_message": "AI chat is in progress.",
        }
    )
    service = _service_with_settings(session, auth_info, settings)

    with pytest.raises(PermissionError, match="AI chat is in progress."):
        service.ensure_access()


async def test_ai_chat_allows_user_in_allowlist(session, auth_info, tmp_path) -> None:
    allowlist = tmp_path / "ai_chat_allowed_emails.txt"
    allowlist.write_text(f"# private beta\n{auth_info.email}\n", encoding="utf-8")
    settings = get_settings().model_copy(
        update={"ai_chat_allowlist_path": str(allowlist)}
    )
    service = _service_with_settings(session, auth_info, settings)

    service.ensure_access()


async def test_ai_chat_denies_when_feature_disabled(session, auth_info, tmp_path) -> None:
    allowlist = tmp_path / "ai_chat_allowed_emails.txt"
    allowlist.write_text(f"{auth_info.email}\n", encoding="utf-8")
    settings = get_settings().model_copy(
        update={
            "ai_chat_enabled": False,
            "ai_chat_allowlist_path": str(allowlist),
            "ai_chat_beta_message": "Feature in progress.",
        }
    )
    service = _service_with_settings(session, auth_info, settings)

    with pytest.raises(PermissionError, match="Feature in progress."):
        service.ensure_access()
