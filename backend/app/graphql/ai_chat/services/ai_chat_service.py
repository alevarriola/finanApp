import datetime
import difflib
import logging
import re
import unicodedata
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from app.auth.auth_info import AuthInfo
from app.core.config import Settings
from app.core.rate_limit import consume_rate_limit
from app.graphql.ai_chat.agents.transaction_parser_agent import TransactionParserAgent
from app.graphql.ai_chat.types.ai_chat_types import (
    AiCategoryContext,
    AiWalletContext,
    ParsedTransaction,
    ValidatedTransaction,
)
from app.graphql.categories.enums import CategoryKind
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.transactions.enums import TransactionKind
from app.graphql.wallets.enums import WalletKind, WalletRole
from app.graphql.wallets.repositories.wallet_repository import WalletRepository

logger = logging.getLogger(__name__)

_RATE_LIMIT_WINDOW_SECONDS = 24 * 60 * 60
_SUSPICIOUS_PROMPT_PATTERNS = [
    "ignore previous instructions",
    "system prompt",
    "developer message",
    "reveal your prompt",
    "show your prompt",
    "act as",
    "tool call",
    "function call",
]
_TRANSACTION_VERBS = {
    "gaste",
    "gasté",
    "pague",
    "pagué",
    "compre",
    "compré",
    "cobre",
    "cobré",
    "recibi",
    "recibí",
    "ingrese",
    "ingresé",
    "deposite",
    "deposité",
    "spent",
    "paid",
    "bought",
    "received",
    "earned",
    "deposited",
}
_TRANSACTION_HINTS = {
    "cash",
    "efectivo",
    "wallet",
    "billetera",
    "cuenta",
    "bank",
    "banco",
    "card",
    "tarjeta",
    "credit",
    "credito",
    "crédito",
    "debit",
    "debito",
    "débito",
    "salary",
    "salario",
    "supermercado",
    "restaurant",
    "restaurante",
    "uber",
    "combustible",
    "nafta",
}


class RateLimitError(Exception):
    pass


class SuspiciousPromptError(Exception):
    pass


class AiProviderError(Exception):
    pass


class AiChatService:
    def __init__(
        self,
        wallet_repository: WalletRepository,
        category_repository: CategoryRepository,
        transaction_parser_agent: TransactionParserAgent,
        auth_info: AuthInfo,
        settings: Settings,
    ) -> None:
        self.wallet_repository = wallet_repository
        self.category_repository = category_repository
        self.transaction_parser_agent = transaction_parser_agent
        self.auth_info = auth_info
        self.settings = settings

    async def ensure_access(self) -> None:
        if not self.settings.ai_chat_enabled:
            raise PermissionError(self.settings.ai_chat_beta_message)
        if self.auth_info.email.lower() not in self._load_allowed_emails():
            raise PermissionError(self.settings.ai_chat_beta_message)
        await self._ensure_rate_limit()

    async def get_wallet_context(self) -> list[AiWalletContext]:
        wallets = await self.wallet_repository.get_user_wallets(self.auth_info.user_id)
        contexts: list[AiWalletContext] = []

        for wallet in wallets:
            member = next(
                (m for m in wallet.members if m.user_id == self.auth_info.user_id),
                None,
            )
            if member is None:
                continue
            contexts.append(
                AiWalletContext(
                    id=wallet.id,
                    name=wallet.name,
                    wallet_kind=wallet.wallet_kind,
                    currency=wallet.currency,
                    role=member.role,
                )
            )

        return contexts

    async def get_category_context(self) -> list[AiCategoryContext]:
        categories = await self.category_repository.get_all(self.auth_info.user_id)
        return [
            AiCategoryContext(
                id=category.id,
                name=category.name,
                name_es=category.name_es,
                category_kind=category.category_kind,
            )
            for category in categories
        ]

    async def parse_transaction(self, text: str) -> ParsedTransaction:
        await self.ensure_access()
        sanitized_text = self._sanitize_text(text)
        if not sanitized_text:
            raise ValueError("Transaction text cannot be empty")
        if len(sanitized_text) > self.settings.ai_chat_max_input_chars:
            raise ValueError("Transaction text is too long")
        self._guard_prompt(sanitized_text)
        if not self._looks_like_transaction_request(sanitized_text):
            raise ValueError("Please describe one income or expense in a single sentence")

        wallet_context = await self.get_wallet_context()
        category_context = await self.get_category_context()
        default_currency = self._pick_default_currency(wallet_context)
        normalized_text = self.transaction_parser_agent.normalize_colloquial_amounts(sanitized_text)
        instructions = self._build_instructions(wallet_context, category_context, default_currency)
        user_prompt = self._build_user_prompt(sanitized_text, normalized_text)
        try:
            parsed = await self.transaction_parser_agent.run(user_prompt, instructions)
        except Exception as exc:
            logger.exception(
                "AI provider failure while parsing transaction",
                extra={"user_id": str(self.auth_info.user_id), "email": self.auth_info.email},
            )
            raise AiProviderError("AI parsing is temporarily unavailable") from exc

        return parsed.model_copy(
            update={
                "raw_text": sanitized_text,
                "currency": parsed.currency or default_currency,
                "requires_confirmation": True,
            }
        )

    async def validate_transaction(self, text: str) -> ValidatedTransaction:
        parsed = await self.parse_transaction(text)
        wallet_context = await self.get_wallet_context()
        category_context = await self.get_category_context()
        return self._build_validated_transaction(parsed, wallet_context, category_context)

    def _sanitize_text(self, text: str) -> str:
        stripped = "".join(ch for ch in text if ch.isprintable() or ch.isspace())
        return " ".join(stripped.split())

    def _pick_default_currency(self, wallet_context: list[AiWalletContext]) -> str | None:
        currencies = {wallet.currency for wallet in wallet_context}
        if len(currencies) == 1:
            return next(iter(currencies))
        return None

    async def _ensure_rate_limit(self) -> None:
        allowed = await self._consume_rate_limit()
        if not allowed:
            raise RateLimitError("AI chat daily limit reached. Please try again tomorrow")

    async def _consume_rate_limit(self) -> bool:
        key = self._rate_limit_key(self.auth_info.user_id)
        return await consume_rate_limit(
            redis_url=self.settings.redis_url,
            key=key,
            limit=self.settings.ai_chat_max_requests_per_day,
            window_seconds=_RATE_LIMIT_WINDOW_SECONDS,
        )

    def _rate_limit_key(self, user_id: UUID) -> str:
        return f"rate-limit:ai-chat:{user_id}"

    def _guard_prompt(self, sanitized_text: str) -> None:
        normalized_text = self._normalize_match_text(sanitized_text)
        if any(pattern in normalized_text for pattern in _SUSPICIOUS_PROMPT_PATTERNS):
            logger.warning(
                "Blocked suspicious AI chat prompt",
                extra={
                    "user_id": str(self.auth_info.user_id),
                    "email": self.auth_info.email,
                    "prompt": sanitized_text,
                },
            )
            raise SuspiciousPromptError(
                "I could not process that message. Please describe only one income or expense"
            )

    def _looks_like_transaction_request(self, sanitized_text: str) -> bool:
        normalized_text = self._normalize_match_text(sanitized_text)
        words = set(normalized_text.split())
        signal_count = 0

        if re.search(r"\d", sanitized_text):
            signal_count += 1
        if words.intersection(_TRANSACTION_VERBS):
            signal_count += 1
        if words.intersection(_TRANSACTION_HINTS):
            signal_count += 1

        return signal_count >= 2

    def _build_validated_transaction(
        self,
        parsed: ParsedTransaction,
        wallet_context: list[AiWalletContext],
        category_context: list[AiCategoryContext],
    ) -> ValidatedTransaction:
        unresolved_fields: list[str] = []
        wallet = self._resolve_wallet(parsed.wallet_hint, wallet_context)
        transaction_kind = self._resolve_transaction_kind(parsed, category_context)
        category = self._resolve_category(parsed.category_hint, transaction_kind, category_context)
        amount = self._validate_amount(parsed.amount)
        date = self._normalize_date(parsed.date)
        currency = self._normalize_currency(parsed.currency)

        if wallet is None:
            unresolved_fields.append("wallet")
        if amount is None:
            unresolved_fields.append("amount")
        if transaction_kind is None:
            unresolved_fields.append("transaction_kind")
        if category is None:
            unresolved_fields.append("category")
        if currency is None and wallet is None:
            unresolved_fields.append("currency")
        elif wallet is not None:
            if currency is None:
                currency = wallet.currency
            elif currency != wallet.currency:
                unresolved_fields.append("currency")
        if parsed.confidence < 0.65:
            unresolved_fields.append("confidence")

        return ValidatedTransaction(
            raw_text=parsed.raw_text,
            wallet_id=wallet.id if wallet is not None else None,
            wallet_name=wallet.name if wallet is not None else None,
            category_id=category.id if category is not None else None,
            category_name=category.name if category is not None else None,
            amount=amount,
            currency=currency,
            transaction_kind=transaction_kind,
            description=parsed.description,
            date=date,
            confidence=parsed.confidence,
            requires_confirmation=True,
            unresolved_fields=sorted(set(unresolved_fields)),
        )

    def _resolve_wallet(
        self,
        wallet_hint: str | None,
        wallet_context: list[AiWalletContext],
    ) -> AiWalletContext | None:
        writable_wallets = [
            wallet
            for wallet in wallet_context
            if wallet.role in {WalletRole.OWNER, WalletRole.EDITOR}
        ]
        if not wallet_hint:
            if len(writable_wallets) == 1:
                return writable_wallets[0]
            return None

        best_wallet = self._find_best_match(wallet_hint, wallet_context, self._wallet_aliases)
        if best_wallet is None or best_wallet.role == WalletRole.VIEWER:
            return None
        return best_wallet

    def _resolve_transaction_kind(
        self,
        parsed: ParsedTransaction,
        category_context: list[AiCategoryContext],
    ) -> TransactionKind | None:
        if parsed.transaction_kind is not None:
            return parsed.transaction_kind
        if not parsed.category_hint:
            return None

        matched_category = self._find_best_match(
            parsed.category_hint,
            category_context,
            self._category_aliases,
        )
        if matched_category is None:
            return None
        if matched_category.category_kind == CategoryKind.EXPENSE:
            return TransactionKind.EXPENSE
        return TransactionKind.INCOME

    def _resolve_category(
        self,
        category_hint: str | None,
        transaction_kind: TransactionKind | None,
        category_context: list[AiCategoryContext],
    ) -> AiCategoryContext | None:
        if not category_hint:
            return None

        if transaction_kind is None:
            candidates = category_context
        else:
            category_kind = (
                CategoryKind.EXPENSE
                if transaction_kind == TransactionKind.EXPENSE
                else CategoryKind.INCOME
            )
            candidates = [
                category for category in category_context if category.category_kind == category_kind
            ]

        return self._find_best_match(category_hint, candidates, self._category_aliases)

    def _validate_amount(self, amount: Decimal | None) -> Decimal | None:
        if amount is None or amount <= Decimal("0"):
            return None
        return amount.quantize(Decimal("0.01"))

    def _normalize_currency(self, currency: str | None) -> str | None:
        if not currency:
            return None
        normalized = currency.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            return None
        return normalized

    def _normalize_date(self, value: datetime.date | None) -> datetime.date:
        if value is None:
            return datetime.date.today()
        return value

    def _find_best_match[T](
        self,
        hint: str,
        candidates: list[T],
        alias_builder: Callable[[T], list[str]],
    ) -> T | None:
        normalized_hint = self._normalize_match_text(hint)
        if not normalized_hint:
            return None

        scored: list[tuple[float, T]] = []
        for candidate in candidates:
            aliases = alias_builder(candidate)
            score = max(
                (
                    self._score_match(normalized_hint, self._normalize_match_text(alias))
                    for alias in aliases
                ),
                default=0.0,
            )
            if score >= 0.55:
                scored.append((score, candidate))

        if not scored:
            return None

        scored.sort(key=lambda item: item[0], reverse=True)
        best_score, best_candidate = scored[0]
        if len(scored) > 1 and best_score - scored[1][0] < 0.08:
            return None
        return best_candidate

    def _wallet_aliases(self, wallet: AiWalletContext) -> list[str]:
        kind_aliases = {
            WalletKind.CASH: ["cash", "efectivo"],
            WalletKind.BANK: ["bank", "banco", "cuenta bancaria"],
            WalletKind.DEBIT: ["debit", "debito", "tarjeta debito", "tarjeta de debito"],
            WalletKind.CREDIT: ["credit", "credito", "tarjeta credito", "tarjeta de credito"],
        }
        aliases = [wallet.name]
        for kind_alias in kind_aliases.get(wallet.wallet_kind, []):
            aliases.append(kind_alias)
            aliases.append(f"{wallet.name} {kind_alias}")
            aliases.append(f"{kind_alias} {wallet.name}")
        return aliases

    def _category_aliases(self, category: AiCategoryContext) -> list[str]:
        aliases = [category.name]
        if category.name_es:
            aliases.append(category.name_es)
        return aliases

    def _score_match(self, hint: str, candidate: str) -> float:
        if not hint or not candidate:
            return 0.0
        if hint == candidate:
            return 1.0
        if hint in candidate or candidate in hint:
            return 0.92
        return difflib.SequenceMatcher(a=hint, b=candidate).ratio()

    def _normalize_match_text(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        cleaned_text = "".join(
            ch if ch.isalnum() or ch.isspace() else " "
            for ch in ascii_text.lower()
        )
        return " ".join(
            cleaned_text.split()
        )

    def _load_allowed_emails(self) -> set[str]:
        path = self._resolve_allowlist_path()
        if not path.exists():
            return set()
        emails: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            normalized = line.strip().lower()
            if not normalized or normalized.startswith("#"):
                continue
            emails.add(normalized)
        return emails

    def _resolve_allowlist_path(self) -> Path:
        configured_path = Path(self.settings.ai_chat_allowlist_path).expanduser()
        if configured_path.is_absolute():
            return configured_path
        backend_root = Path(__file__).resolve().parents[4]
        return backend_root / configured_path

    def _build_user_prompt(self, sanitized_text: str, normalized_text: str) -> str:
        return "\n".join(
            [
                "Original user text:",
                sanitized_text,
                "",
                "Normalized user text:",
                normalized_text,
            ]
        )

    def _build_instructions(
        self,
        wallet_context: list[AiWalletContext],
        category_context: list[AiCategoryContext],
        default_currency: str | None,
    ) -> str:
        wallet_lines = [
            (
                f"- {wallet.name} | kind={wallet.wallet_kind.name} | "
                f"currency={wallet.currency} | role={wallet.role.name}"
            )
            for wallet in wallet_context
        ]
        category_lines = [
            f"- {category.name} | es={category.name_es or '-'} | kind={category.category_kind.name}"
            for category in category_context
        ]
        wallet_section = wallet_lines or ["- none"]
        category_section = category_lines or ["- none"]

        sections = [
            "Context for the current user:",
            "Wallets:",
            *wallet_section,
            "",
            "Categories:",
            *category_section,
            "",
            f"Default currency: {default_currency or 'unknown'}",
            (
                "If the user mentions relative dates like yesterday, infer the actual "
                "calendar date from the current local context."
            ),
        ]
        return "\n".join(sections)
