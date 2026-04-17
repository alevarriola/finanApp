from app.auth.auth_info import AuthInfo
from app.core.config import Settings
from app.graphql.ai_chat.agents.transaction_parser_agent import TransactionParserAgent
from app.graphql.ai_chat.types.ai_chat_types import (
    AiCategoryContext,
    AiWalletContext,
    ParsedTransaction,
)
from app.graphql.categories.repositories.category_repository import CategoryRepository
from app.graphql.wallets.repositories.wallet_repository import WalletRepository


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
        sanitized_text = self._sanitize_text(text)
        if not sanitized_text:
            raise ValueError("Transaction text cannot be empty")

        wallet_context = await self.get_wallet_context()
        category_context = await self.get_category_context()
        default_currency = self._pick_default_currency(wallet_context)
        normalized_text = self.transaction_parser_agent.normalize_colloquial_amounts(sanitized_text)
        instructions = self._build_instructions(wallet_context, category_context, default_currency)
        user_prompt = self._build_user_prompt(sanitized_text, normalized_text)
        parsed = await self.transaction_parser_agent.run(user_prompt, instructions)

        return parsed.model_copy(
            update={
                "raw_text": sanitized_text,
                "currency": parsed.currency or default_currency,
                "requires_confirmation": True,
            }
        )

    def _sanitize_text(self, text: str) -> str:
        stripped = "".join(ch for ch in text if ch.isprintable() or ch.isspace())
        return " ".join(stripped.split())

    def _pick_default_currency(self, wallet_context: list[AiWalletContext]) -> str | None:
        currencies = {wallet.currency for wallet in wallet_context}
        if len(currencies) == 1:
            return next(iter(currencies))
        return None

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
