import datetime
from decimal import Decimal

import pytest

from app.auth.auth_info import AuthInfo
from app.core.config import get_settings
from app.graphql.ai_chat.agents.transaction_parser_agent import TransactionParserAgent
from app.graphql.ai_chat.services.ai_chat_service import AiChatService
from app.graphql.ai_chat.types.ai_chat_types import ParsedTransaction, ValidatedTransaction
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.categories.services.category_service import CategoryService
from app.graphql.schemas.schema import Mutation
from app.graphql.transactions.enums import TransactionKind
from app.graphql.users.repositories.user_repository import UserRepository
from app.graphql.users.services.user_service import UserService
from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.models.wallet_member import WalletMember
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


async def _make_user(session, email: str):
    repo = UserRepository(session)
    service = UserService(repo)
    return await service.register(
        email=email,
        name=email.split("@", 1)[0],
        password="password123",
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
    assert "validate_transaction" in field_names


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


async def test_validate_transaction_resolves_wallet_category_and_defaults(
    ai_chat_service,
    wallet_service,
    category_service,
) -> None:
    wallet = await wallet_service.create_wallet(
        name="Tarjeta Itaú",
        wallet_kind=WalletKind.CREDIT,
        currency="USD",
        initial_balance=Decimal("0"),
    )
    category = await category_service.create_category(
        name="Food",
        category_kind=CategoryKind.EXPENSE,
    )

    async def fake_parse_transaction(text: str) -> ParsedTransaction:
        return ParsedTransaction(
            raw_text=text,
            wallet_hint="tarjeta de credito de itau",
            amount=Decimal("100"),
            currency="usd",
            transaction_kind=TransactionKind.EXPENSE,
            category_hint="food",
            description="cena familiar",
            confidence=0.91,
        )

    ai_chat_service.parse_transaction = fake_parse_transaction  # type: ignore[method-assign]

    validated = await ai_chat_service.validate_transaction(
        "Gaste 100 USD en cena familiar con mi tarjeta Itaú"
    )

    assert isinstance(validated, ValidatedTransaction)
    assert validated.wallet_id == wallet.id
    assert validated.wallet_name == "Tarjeta Itaú"
    assert validated.category_id == category.id
    assert validated.category_name == "Food"
    assert validated.amount == Decimal("100.00")
    assert validated.currency == "USD"
    assert validated.transaction_kind == TransactionKind.EXPENSE
    assert validated.date == datetime.date.today()
    assert validated.unresolved_fields == []


async def test_validate_transaction_marks_ambiguous_wallet(ai_chat_service, wallet_service) -> None:
    await wallet_service.create_wallet(
        name="Itaú Visa",
        wallet_kind=WalletKind.CREDIT,
        currency="USD",
        initial_balance=Decimal("0"),
    )
    await wallet_service.create_wallet(
        name="Itaú Master",
        wallet_kind=WalletKind.CREDIT,
        currency="USD",
        initial_balance=Decimal("0"),
    )

    async def fake_parse_transaction(text: str) -> ParsedTransaction:
        return ParsedTransaction(
            raw_text=text,
            wallet_hint="itau",
            amount=Decimal("50"),
            currency="USD",
            transaction_kind=TransactionKind.EXPENSE,
            category_hint=None,
            confidence=0.9,
        )

    ai_chat_service.parse_transaction = fake_parse_transaction  # type: ignore[method-assign]

    validated = await ai_chat_service.validate_transaction("Gaste 50 en Itau")

    assert validated.wallet_id is None
    assert "wallet" in validated.unresolved_fields
    assert "category" in validated.unresolved_fields


async def test_validate_transaction_rejects_viewer_wallet(session, auth_info, tmp_path) -> None:
    owner = await _make_user(session, "owner@test.com")
    owner_auth = AuthInfo(user_id=owner.id, email=owner.email)
    owner_service = _service_with_settings(
        session,
        owner_auth,
        get_settings().model_copy(
            update={"ai_chat_allowlist_path": str(tmp_path / "owner_allowlist.txt")}
        ),
    )
    (tmp_path / "owner_allowlist.txt").write_text(
        f"{owner.email}\n{auth_info.email}\n",
        encoding="utf-8",
    )

    owner_wallet_service = WalletService(WalletRepository(session), owner_auth)
    wallet = await owner_wallet_service.create_wallet(
        name="Banco Familiar",
        wallet_kind=WalletKind.BANK,
        currency="PYG",
        initial_balance=Decimal("0"),
    )
    await WalletRepository(session).add_member(
        WalletMember(wallet_id=wallet.id, user_id=auth_info.user_id, role=WalletRole.VIEWER)
    )

    async def fake_parse_transaction(text: str) -> ParsedTransaction:
        return ParsedTransaction(
            raw_text=text,
            wallet_hint="banco familiar",
            amount=Decimal("120000"),
            currency="PYG",
            transaction_kind=TransactionKind.EXPENSE,
            confidence=0.87,
        )

    owner_service.auth_info = auth_info
    owner_service.parse_transaction = fake_parse_transaction  # type: ignore[method-assign]

    validated = await owner_service.validate_transaction("Gaste 120000 desde Banco Familiar")

    assert validated.wallet_id is None
    assert "wallet" in validated.unresolved_fields


async def test_validate_transaction_flags_currency_mismatch(
    ai_chat_service,
    wallet_service,
) -> None:
    await wallet_service.create_wallet(
        name="Cash Wallet",
        wallet_kind=WalletKind.CASH,
        currency="PYG",
        initial_balance=Decimal("0"),
    )

    async def fake_parse_transaction(text: str) -> ParsedTransaction:
        return ParsedTransaction(
            raw_text=text,
            wallet_hint="cash wallet",
            amount=Decimal("10"),
            currency="USD",
            transaction_kind=TransactionKind.EXPENSE,
            confidence=0.88,
        )

    ai_chat_service.parse_transaction = fake_parse_transaction  # type: ignore[method-assign]

    validated = await ai_chat_service.validate_transaction("Spent 10 dollars")

    assert validated.wallet_name == "Cash Wallet"
    assert "currency" in validated.unresolved_fields


async def test_validate_transaction_infers_kind_from_category(
    ai_chat_service,
    category_service,
) -> None:
    category = await category_service.create_category(
        name="Salary",
        category_kind=CategoryKind.INCOME,
    )

    async def fake_parse_transaction(text: str) -> ParsedTransaction:
        return ParsedTransaction(
            raw_text=text,
            wallet_hint=None,
            amount=Decimal("500"),
            currency=None,
            transaction_kind=None,
            category_hint="salary",
            confidence=0.9,
        )

    ai_chat_service.parse_transaction = fake_parse_transaction  # type: ignore[method-assign]

    validated = await ai_chat_service.validate_transaction("Cobre salario")

    assert validated.transaction_kind == TransactionKind.INCOME
    assert validated.category_id == category.id
