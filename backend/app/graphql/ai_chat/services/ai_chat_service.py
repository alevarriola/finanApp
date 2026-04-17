from app.auth.auth_info import AuthInfo
from app.core.config import Settings
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
        auth_info: AuthInfo,
        settings: Settings,
    ) -> None:
        self.wallet_repository = wallet_repository
        self.category_repository = category_repository
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
        default_currency = self._pick_default_currency(wallet_context)

        return ParsedTransaction(
            raw_text=sanitized_text,
            currency=default_currency,
            description=sanitized_text,
            confidence=0.0,
            requires_confirmation=True,
        )

    def _sanitize_text(self, text: str) -> str:
        stripped = "".join(ch for ch in text if ch.isprintable() or ch.isspace())
        return " ".join(stripped.split())

    def _pick_default_currency(self, wallet_context: list[AiWalletContext]) -> str | None:
        currencies = {wallet.currency for wallet in wallet_context}
        if len(currencies) == 1:
            return next(iter(currencies))
        return None
